"""Compare the three review systems under BOTH scenarios and let the numbers decide.

The point of Day 4: the answer changes with the reviewer. In one world the specialist
team finds defects one reviewer cannot. In the other it finds nothing extra and bills
three times as much. Read the table; do not assume.

    python evaluate_project.py            # print the table
    python evaluate_project.py --write    # also refresh data/captured_comparison.json
"""
import json
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
SCENARIOS = ("blind_spots", "strong_generalist")
COLUMNS = ["system", "found", "recall", "false_positives", "duplicates",
           "merged_duplicates", "model_calls", "tokens", "elapsed_ms"]
# Illustrative catalogue price so the cost column is arithmetic students can redo.
PRICE_PER_MILLION_TOKENS = 0.15


def build_provider(scenario, live=None):
    live = os.getenv("OPENROUTER_API_KEY") if live is None else live
    if live:
        return FallbackReviewer(OpenRouterReviewer(), MockStructuredReviewer(scenario))
    return MockStructuredReviewer(scenario)


def rows_for(scenario):
    provider = build_provider(scenario)
    runs = [run_single_reviewer(SOURCE, provider),
            run_checks_plus_reviewer(SOURCE, provider),
            run_specialist_team(SOURCE, provider)]
    return [evaluate(run, GOLDEN, price_per_million_tokens=PRICE_PER_MILLION_TOKENS)
            for run in runs]


def print_table(scenario, rows):
    widths = [max(len(str(row[col])) for row in rows + [{c: c for c in COLUMNS}])
              for col in COLUMNS]
    print(f"\nScenario: {scenario}")
    print(" | ".join(col.ljust(w) for col, w in zip(COLUMNS, widths)))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(" | ".join(str(row[col]).ljust(w) for col, w in zip(COLUMNS, widths)))
    best = max(rows, key=lambda r: (r["found"], -r["model_calls"]))
    cheapest_at_best = min([r for r in rows if r["found"] == best["found"]],
                           key=lambda r: r["model_calls"])
    print(f"  Most defects found : {best['found']}/{best['known_defects']}")
    print(f"  Smallest system that reaches it: {cheapest_at_best['system']} "
          f"({cheapest_at_best['model_calls']} model call(s), "
          f"{cheapest_at_best['tokens']} tokens, "
          f"${cheapest_at_best['estimated_cost_usd']:.6f})")


def main():
    all_rows = {}
    for scenario in SCENARIOS:
        rows = rows_for(scenario)
        all_rows[scenario] = rows
        print_table(scenario, rows)
    print("\nThe winner is not the same in both scenarios. That is the lesson: "
          "measure before you add agents.")

    if "--write" in sys.argv:
        target = ROOT / "data" / "captured_comparison.json"
        target.write_text(json.dumps({
            "note": ("Captured offline with MockStructuredReviewer (no model was called). "
                     "Used by notebook 06 when no API key is available. "
                     "Regenerate with: python evaluate_project.py --write"),
            "source": "day_04_multi_agent_systems/evaluate_project.py",
            "provider": "MockStructuredReviewer",
            "price_per_million_tokens": PRICE_PER_MILLION_TOKENS,
            "scenarios": all_rows,
        }, indent=2), encoding="utf-8")
        print("wrote", target)


if __name__ == "__main__":
    main()
