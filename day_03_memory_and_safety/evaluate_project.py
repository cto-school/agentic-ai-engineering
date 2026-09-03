from pathlib import Path
import sys

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from safe_task_agent.evaluation import evaluate_safety

if __name__ == "__main__":
    report = evaluate_safety(ROOT / "data" / "safety_cases.json")
    print(f"Safety policy: {report['passed']}/{report['total']} cases passed")
    for row in report["cases"]:
        print(row)
