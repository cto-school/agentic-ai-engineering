"""Tests for the Day 4 review team.

Deliberately NOT tested: "the multi-agent system wins". Whether decomposition helps is
the measured result of the lesson, not an invariant. What we do test is that the
measurement itself is trustworthy: telemetry is real, defects are counted once,
duplicates and truncation are reported, and the same run is reproducible.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from review_team import (  # noqa: E402
    FallbackReviewer, Finding, MockStructuredReviewer, deterministic_checks, evaluate,
    run_checks_plus_reviewer, run_single_reviewer, run_specialist_team, single_reviewer,
    specialist_review, synthesize_with_report,
)

SOURCE = (ROOT / "data" / "seeded_artifact" / "order_service.py").read_text(encoding="utf-8")
GOLDEN = ROOT / "data" / "golden_defects.json"


# --- deterministic tools -------------------------------------------------------------

def test_deterministic_checks_report_objective_facts():
    checks = deterministic_checks(SOURCE)
    assert [f.id for f in checks] == ["AST-MUTABLE-DEFAULT-6", "AST-EVAL-20", "AST-BROAD-EXCEPT-26"]
    assert all(f.evidence for f in checks)


def test_checker_ids_do_not_leak_the_answer_key():
    # A real static analyser cannot know our golden ids, so ours must not use them.
    assert not any(f.id.startswith("DEF-") for f in deterministic_checks(SOURCE))


def test_structured_findings_have_evidence():
    for finding in specialist_review(SOURCE, "security"):
        assert finding.line > 0 and finding.evidence and finding.recommendation


# --- supervisor ----------------------------------------------------------------------

def test_supervisor_reports_what_it_merged():
    checks = deterministic_checks(SOURCE)
    report = synthesize_with_report([checks, checks], merge_by="id")
    assert report.received == 6 and report.kept == 3 and report.merged_duplicates == 3


def test_location_merge_catches_duplicates_that_id_merge_misses():
    groups = [deterministic_checks(SOURCE), specialist_review(SOURCE, "security")]
    by_id = synthesize_with_report(groups, merge_by="id")
    by_location = synthesize_with_report(groups, merge_by="location")
    # The AST checker and the security specialist both report eval() on line 20 under
    # different ids: only the location rule recognises them as one defect.
    assert by_id.merged_duplicates == 0
    assert by_location.merged_duplicates == 1


def test_supervisor_records_how_many_it_truncated():
    report = synthesize_with_report([specialist_review(SOURCE, "security")], max_findings=2)
    assert report.kept == 2 and report.dropped_over_cap == 2


def test_supervisor_merge_key_is_validated():
    with pytest.raises(ValueError):
        synthesize_with_report([[]], merge_by="vibes")


# --- evaluation ----------------------------------------------------------------------

def test_each_golden_defect_is_counted_once_and_extras_are_duplicates():
    from review_team.schemas import ReviewRun
    eval_finding = Finding("X-1", "security", 20, "eval", "return eval(expression)",
                           "critical", "stop", "a")
    twin = Finding("X-2", "security", 20, "eval again", "return eval(expression)",
                   "critical", "stop", "b")
    row = evaluate(ReviewRun("demo", [eval_finding, twin]), GOLDEN)
    assert row["found"] == 1 and row["duplicates"] == 1 and row["false_positives"] == 0


def test_unsupported_findings_are_false_positives():
    from review_team.schemas import ReviewRun
    invented = Finding("X-9", "security", 1, "docstring is unsafe", '"""..."""',
                       "low", "none", "a")
    row = evaluate(ReviewRun("demo", [invented]), GOLDEN)
    assert row["found"] == 0 and row["false_positives"] == 1


# --- telemetry -----------------------------------------------------------------------

def test_token_counts_come_from_the_provider_not_from_a_guess():
    provider = MockStructuredReviewer()
    single = run_single_reviewer(SOURCE, provider)
    augmented = run_checks_plus_reviewer(SOURCE, provider)
    usage = single.trace[0]["usage"]
    assert single.total_tokens == usage["prompt_tokens"] + usage["completion_tokens"]
    # Adding a free AST pass must not change the model bill.
    assert augmented.model_calls == 1 and augmented.total_tokens == single.total_tokens
    checks_step = augmented.trace[0]
    assert checks_step["step"] == "deterministic_checks"
    assert checks_step["usage"]["model_calls"] == 0 and checks_step["usage"]["prompt_tokens"] == 0


def test_team_pays_three_times_the_tokens_of_one_reviewer():
    provider = MockStructuredReviewer()
    single = run_single_reviewer(SOURCE, provider)
    team = run_specialist_team(SOURCE, provider)
    assert team.model_calls == 3
    assert team.prompt_tokens == 3 * single.prompt_tokens


# --- the measured comparison (no "multi always wins" assertion) -----------------------

def test_blind_spot_scenario_is_where_specialists_help():
    provider = MockStructuredReviewer(scenario="blind_spots")
    rows = [evaluate(run, GOLDEN) for run in (
        run_single_reviewer(SOURCE, provider),
        run_checks_plus_reviewer(SOURCE, provider),
        run_specialist_team(SOURCE, provider))]
    assert [row["found"] for row in rows] == [5, 6, 9]


def test_strong_generalist_scenario_is_where_the_team_is_not_worth_it():
    provider = MockStructuredReviewer(scenario="strong_generalist")
    single = evaluate(run_single_reviewer(SOURCE, provider), GOLDEN)
    team = evaluate(run_specialist_team(SOURCE, provider), GOLDEN)
    assert team["found"] == single["found"]           # no extra defects discovered
    assert team["model_calls"] > single["model_calls"]  # but three times the calls
    assert team["merged_duplicates"] > 0                # and duplicated work to merge


def test_every_system_stays_within_its_bounds():
    for scenario in ("blind_spots", "strong_generalist"):
        provider = MockStructuredReviewer(scenario=scenario)
        for run in (run_single_reviewer(SOURCE, provider),
                    run_checks_plus_reviewer(SOURCE, provider),
                    run_specialist_team(SOURCE, provider)):
            row = evaluate(run, GOLDEN)
            assert 0.0 <= row["recall"] <= 1.0
            assert row["false_positives"] == 0
            assert row["model_calls"] <= 3


# --- fan-out -------------------------------------------------------------------------

def test_parallel_and_sequential_fan_out_agree():
    provider = MockStructuredReviewer()
    sequential = run_specialist_team(SOURCE, provider, parallel=False)
    parallel = run_specialist_team(SOURCE, provider, parallel=True)
    assert [f.id for f in sequential.findings] == [f.id for f in parallel.findings]
    assert sequential.model_calls == parallel.model_calls  # parallel saves time, not cost


# --- provider contract ---------------------------------------------------------------

def test_any_provider_satisfying_the_contract_can_drive_every_system():
    class FakeProvider:
        def __init__(self):
            self.roles = []

        def review(self, source, role):
            self.roles.append(role)
            line = {"general": 20, "correctness": 7, "security": 15, "maintainability": 6}[role]
            category = "security" if role == "general" else role
            finding = Finding(f"FAKE-{role}", category, line, "Evidence-based issue",
                              source.splitlines()[line - 1], "high", "Fix it", f"{role}_fake")
            return [finding], {"prompt_tokens": 100, "completion_tokens": 25, "cost_usd": 0.001}

    provider = FakeProvider()
    single = run_single_reviewer(SOURCE, provider)
    team = run_specialist_team(SOURCE, provider)
    assert single.model_calls == 1 and team.model_calls == 3
    assert provider.roles == ["general", "correctness", "security", "maintainability"]
    assert single.cost_usd == pytest.approx(0.001) and team.cost_usd == pytest.approx(0.003)
    assert evaluate(single, GOLDEN)["found"] == 1
    assert len(team.trace) == 5  # checks + three specialists + supervisor


def test_fallback_reviewer_survives_a_live_failure():
    import contextlib
    import io

    class BrokenProvider:
        def review(self, source, role):
            raise RuntimeError("503 upstream unavailable")

    provider = FallbackReviewer(BrokenProvider(), MockStructuredReviewer())
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):  # no pytest fixture: validate_course.py calls tests directly
        findings, usage = provider.review(SOURCE, "general")
    assert findings and usage["live"] is False and provider.failures == 1
    assert "falling back" in captured.getvalue()


def test_scenarios_change_only_the_reviewer_not_the_artifact():
    a = {f.id for f in single_reviewer(SOURCE, "blind_spots")}
    b = {f.id for f in single_reviewer(SOURCE, "strong_generalist")}
    assert a < b and "DEF-COR-02" not in b
