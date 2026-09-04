"""The three review SYSTEMS we compare. One naming scheme, no duplicates.

    run_single_reviewer      1 model call, no tools, no supervisor
    run_checks_plus_reviewer deterministic checks (0 model calls) + 1 model call
    run_specialist_team      deterministic checks + 3 specialist calls + supervisor

All three take the same `provider` (see model_reviewers), so the comparison changes the
ARCHITECTURE while holding the reviewer constant. Every token and cost figure below
comes from the provider's own usage report; a step that makes no model call reports
zero and says so in the trace.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

from .checks import deterministic_checks
from .model_reviewers import ReviewerProvider
from .schemas import ReviewRun
from .supervisor import synthesize_with_report

SPECIALIST_ROLES = ("correctness", "security", "maintainability")

# The trace entry for a step that used ordinary code instead of a model. Writing the
# zeros down explicitly is the point: we never let a free step borrow a model's numbers.
NO_MODEL_CALL = {"model_calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
                 "cost_usd": 0.0, "note": "no model call - deterministic code"}


def _totals(usages: list[dict]) -> tuple[int, int, float]:
    """Add up what the provider said each call actually consumed."""
    prompt = sum(int(u.get("prompt_tokens", 0)) for u in usages)
    completion = sum(int(u.get("completion_tokens", 0)) for u in usages)
    cost = sum(float(u.get("cost_usd", 0.0)) for u in usages)
    return prompt, completion, cost


def run_single_reviewer(source: str, provider: ReviewerProvider) -> ReviewRun:
    """System 1: ask one reviewer about everything, and report exactly what it said."""
    start = perf_counter()
    findings, usage = provider.review(source, "general")
    prompt, completion, cost = _totals([usage])
    return ReviewRun(
        system="single_reviewer",
        findings=findings,
        model_calls=1,
        prompt_tokens=prompt, completion_tokens=completion, cost_usd=cost,
        elapsed_ms=(perf_counter() - start) * 1000,
        raw_findings=len(findings),
        trace=[{"step": "general_reviewer", "count": len(findings), "usage": usage}],
    )


def run_checks_plus_reviewer(source: str, provider: ReviewerProvider,
                             max_findings: int = 20, merge_by: str = "location") -> ReviewRun:
    """System 2: prove what a parser can prove, then spend ONE model call on judgement."""
    start = perf_counter()
    checks = deterministic_checks(source)                    # free, deterministic, 0 tokens
    findings, usage = provider.review(source, "general")     # the only model call
    report = synthesize_with_report([checks, findings], max_findings, merge_by)
    prompt, completion, cost = _totals([usage])
    return ReviewRun(
        system="checks_plus_reviewer",
        findings=report.findings,
        model_calls=1,
        prompt_tokens=prompt, completion_tokens=completion, cost_usd=cost,
        elapsed_ms=(perf_counter() - start) * 1000,
        raw_findings=report.received,
        merged_duplicates=report.merged_duplicates,
        dropped_over_cap=report.dropped_over_cap,
        trace=[
            {"step": "deterministic_checks", "count": len(checks), "usage": NO_MODEL_CALL},
            {"step": "general_reviewer", "count": len(findings), "usage": usage},
            {"step": "supervisor", "count": report.kept,
             "merged_duplicates": report.merged_duplicates,
             "dropped_over_cap": report.dropped_over_cap, "merge_key": report.merge_key},
        ],
    )


def run_specialist_team(source: str, provider: ReviewerProvider, parallel: bool = False,
                        max_findings: int = 20, merge_by: str = "location") -> ReviewRun:
    """System 3: fan out to three narrow reviewers, then fan in at the supervisor.

    `parallel=False` runs the branches one after another: easiest to read and debug.
    `parallel=True` runs them in threads. Wall-clock time drops because the calls wait
    on the network at the same time; the number of calls, tokens and cost do NOT drop.
    """
    start = perf_counter()

    def branch(role: str):
        return provider.review(source, role)                 # each branch: 1 model call

    if parallel:
        # Fan-out: three independent branches, bounded at exactly three workers.
        with ThreadPoolExecutor(max_workers=len(SPECIALIST_ROLES)) as pool:
            results = list(pool.map(branch, SPECIALIST_ROLES))
    else:
        results = [branch(role) for role in SPECIALIST_ROLES]

    groups = [findings for findings, _ in results]
    usages = [usage for _, usage in results]
    checks = deterministic_checks(source)                    # free, deterministic, 0 tokens

    # Fan-in: one bounded merge step, which also reports what it merged and truncated.
    report = synthesize_with_report([checks, *groups], max_findings, merge_by)
    prompt, completion, cost = _totals(usages)

    trace = [{"step": "deterministic_checks", "count": len(checks), "usage": NO_MODEL_CALL}]
    trace += [{"step": f"{role}_specialist", "count": len(group), "usage": usage}
              for role, group, usage in zip(SPECIALIST_ROLES, groups, usages)]
    trace.append({"step": "supervisor", "count": report.kept,
                  "received": report.received,
                  "merged_duplicates": report.merged_duplicates,
                  "dropped_over_cap": report.dropped_over_cap,
                  "merge_key": report.merge_key,
                  "execution": "parallel" if parallel else "sequential"})

    return ReviewRun(
        system="specialist_team_parallel" if parallel else "specialist_team",
        findings=report.findings,
        model_calls=len(SPECIALIST_ROLES),
        prompt_tokens=prompt, completion_tokens=completion, cost_usd=cost,
        elapsed_ms=(perf_counter() - start) * 1000,
        raw_findings=report.received,
        merged_duplicates=report.merged_duplicates,
        dropped_over_cap=report.dropped_over_cap,
        trace=trace,
    )
