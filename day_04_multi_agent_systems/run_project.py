from pathlib import Path
import sys
ROOT=Path(__file__).parent; sys.path.insert(0,str(ROOT/"src"))
from review_team import evaluate,run_augmented,run_multi,run_single

source=(ROOT/"data"/"seeded_artifact"/"order_service.py").read_text(encoding="utf-8")
golden=ROOT/"data"/"golden_defects.json"
for run in (run_single(source),run_augmented(source),run_multi(source)):
    print(evaluate(run,golden))
    print("trace:",run.trace)
    for finding in run.findings: print(" ",finding.as_dict())
