from pathlib import Path
import sys

ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/"src"))
from review_team import *

SOURCE=(ROOT/"data"/"seeded_artifact"/"order_service.py").read_text(encoding="utf-8")
GOLDEN=ROOT/"data"/"golden_defects.json"


def test_deterministic_checks_are_objective():
    ids={f.id for f in deterministic_checks(SOURCE)}
    assert ids == {"DEF-SEC-03","DEF-MNT-01","DEF-MNT-02"}


def test_structured_findings_have_evidence():
    for finding in specialist_review(SOURCE,"security"):
        assert finding.line > 0 and finding.evidence and finding.recommendation


def test_supervisor_deduplicates():
    same=deterministic_checks(SOURCE)
    merged=synthesize([same,same])
    assert len(merged)==len({f.id for f in same})


def test_measured_comparison_is_bounded():
    single, augmented, multi=run_single(SOURCE),run_augmented(SOURCE),run_multi(SOURCE)
    scores=[evaluate(run,GOLDEN) for run in (single,augmented,multi)]
    assert scores[0]["recall"] < scores[2]["recall"] == 1.0
    assert multi.model_calls == 3 and len(multi.trace) == 5
    assert all(score["false_positives"] == 0 for score in scores)


def test_model_provider_contract_supports_single_and_specialists():
    class FakeProvider:
        def review(self,source,role):
            categories=[role] if role!="general" else ["security"]
            lines={"correctness":7,"security":15,"maintainability":6}
            findings=[Finding(f"MODEL-{category}",category,lines[category],"Evidence-based issue",
                source.splitlines()[lines[category]-1],"high","Apply a targeted correction.",f"{role}_model")
                for category in categories]
            return findings,{"prompt_tokens":100,"completion_tokens":25,"cost_usd":0.001}
    provider=FakeProvider()
    single=run_model_review(SOURCE,provider)
    multi=run_model_multi(SOURCE,provider)
    assert single.model_calls==1 and multi.model_calls==3
    assert evaluate(single,GOLDEN)["found"]==1
    assert len(multi.trace)==4
