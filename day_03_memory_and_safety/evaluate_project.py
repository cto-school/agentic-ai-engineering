"""Run the fixed safety suite: every case must reach the expected policy outcome."""
from pathlib import Path
import sys

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from safe_task_agent.evaluation import evaluate_safety

if __name__ == "__main__":
    report = evaluate_safety(ROOT / "data" / "safety_cases.json")
    print(f"Safety policy: {report['passed']}/{report['total']} cases passed")
    print(f"{'id':<5}{'channel':<10}{'expected':<10}{'actual':<10}{'passed':<8}emails sent")
    for row in report["cases"]:
        print(f"{row['id']:<5}{row['channel']:<10}{row['expected']:<10}"
              f"{row['actual']:<10}{str(row['passed']):<8}{row['side_effects']}")
    if report["passed"] != report["total"]:
        sys.exit(1)
