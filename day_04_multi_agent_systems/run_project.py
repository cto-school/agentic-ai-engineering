"""Run the Day 4 review team end to end and print every trace.

Offline by default. Set OPENROUTER_API_KEY to run the same three systems against a real
model; any live failure falls back to the deterministic reviewer and says so.

    python run_project.py                  # default scenario: blind_spots
    python run_project.py strong_generalist
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from review_team import (FallbackReviewer, MockStructuredReviewer, OpenRouterReviewer,  # noqa: E402
                         evaluate, run_checks_plus_reviewer, run_single_reviewer,
                         run_specialist_team)

SOURCE = (ROOT / "data" / "seeded_artifact" / "order_service.py").read_text(encoding="utf-8")
GOLDEN = ROOT / "data" / "golden_defects.json"


def build_provider(scenario):
    """Live reviewer when a key exists (with a mock safety net), otherwise the mock."""
    if os.getenv("OPENROUTER_API_KEY"):
        return FallbackReviewer(OpenRouterReviewer(), MockStructuredReviewer(scenario))
    return MockStructuredReviewer(scenario)


def main(scenario="blind_spots"):
    provider = build_provider(scenario)
    print("Scenario :", scenario)
    print("Provider :", type(provider).__name__)
    print("Artifact :", len(SOURCE.splitlines()), "lines\n")

    runs = [run_single_reviewer(SOURCE, provider),
            run_checks_plus_reviewer(SOURCE, provider),
            run_specialist_team(SOURCE, provider)]

    for run in runs:
        row = evaluate(run, GOLDEN)
        print("=" * 78)
        print(f"SYSTEM {run.system}")
        print(f"  found {row['found']}/{row['known_defects']} defects "
              f"(recall {row['recall']}) | model calls {row['model_calls']} | "
              f"tokens {row['tokens']} | duplicates merged {row['merged_duplicates']} | "
              f"dropped over cap {row['dropped_over_cap']}")
        print("  missed:", row["missed"] or "nothing")
        print("  trace:")
        for event in run.trace:
            print("   ", event)
        print("  findings:")
        for finding in run.findings:
            print(f"    {finding.severity:8} line {finding.line:>3}  {finding.title}  "
                  f"[{finding.reviewer}]")
    print("=" * 78)
    print("Recall is an observed result. Run evaluate_project.py to compare scenarios.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "blind_spots")
