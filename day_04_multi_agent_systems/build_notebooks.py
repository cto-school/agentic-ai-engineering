"""Build the seven Day 4 notebooks."""

import sys as _sys
if "--force" not in _sys.argv:  # pragma: no cover
    raise SystemExit(
        "ARCHIVED: the notebooks in notebooks/ are hand-maintained and are the source of truth. "
        "This generator predates the current content and would overwrite it. "
        "Run with --force only if you intend to regenerate from these definitions."
    )
import json
from pathlib import Path
ROOT=Path(__file__).parent; (ROOT/"notebooks").mkdir(exist_ok=True)
META={
"01_seeded_artifact_and_golden_set.ipynb":("Define an evidenced finding and establish a fair hidden-answer review task.","The artifact prints with line numbers; the golden set contains nine defects but should remain hidden until your first review.","Write two findings before revealing the golden file, each with category, line, evidence, severity, and correction.","A golden set makes comparison repeatable; it must not leak into the review prompt.","D12"),
"02_single_reviewer_baseline.ipynb":("Run one general reviewer through a provider contract and preserve its telemetry.","Mock mode deterministically finds a subset; OpenRouter wording and counts may vary while the finding schema remains fixed.","Inspect one missed defect and improve only the prompt or schema—not the answer key.","A baseline must exist before adding roles or orchestration.","D12"),
"03_deterministic_checks.ipynb":("Use AST checks for objective facts and combine them with model judgment.","The checker finds eval, a mutable default, and a broad exception; synthesis removes overlaps.","Add one AST check for string-built SQL or explain why a dedicated security tool may be preferable.","Use deterministic tools where possible and models where judgment is useful.","D15"),
"04_parallel_specialist_reviewers.ipynb":("Scope three reviewer roles, compare sequential clarity with parallel fan-out, and preserve structured handoffs.","Three role traces appear and the supervisor receives only Finding objects.","Run the same roles sequentially first; then compare calls, results, and wall time with fan-out.","Multi-agent means bounded decomposition, not unrestricted agent conversation.","D13"),
"05_supervisor_synthesis.ipynb":("Validate, deduplicate, rank, cap, and terminate specialist findings.","Duplicate stable IDs collapse and critical findings appear before medium ones.","Create two differently worded findings at the same line and document why stable-ID deduplication is insufficient.","A supervisor has a narrow aggregation contract and a stopping condition.","D14"),
"06_comparative_evaluation.ipynb":("Calculate recall, false positives, calls, tokens, latency, and cost on the same artifact.","Offline orchestration yields 5/9, 6/9, and 9/9; live model results may vary and must be preserved.","Hand-calculate recall for one run, then repeat a model A/B twice and report variance.","Choose the smallest system that meets measured quality requirements.","D15"),
"07_project_engineering_review_team.ipynb":("Integrate provider-backed roles, deterministic checks, supervisor synthesis, traces, and a decision memo.","Both single and specialist systems terminate with structured findings and comparable telemetry.","Submit one choice and one condition that would reverse it; include raw trace evidence.","More agents are justified only by measured benefit.","D12–D15"),
}
def md(s): return {"cell_type":"markdown","metadata":{},"source":s.splitlines(True)}
def code(s): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":s.splitlines(True)}
def write(name,cells):
    goals,expected,exercise,recap,diagram=META[name]
    guide=md(f'''## Before you begin

**Choose one:** use the structured mock reviewer for deterministic classroom work, or OpenRouter when the issued key is available. Never send private code.

### Learning outcomes

{goals}

Architecture reference: [Day 4 diagrams {diagram}](../../diagrams/source/day_04.md).

### Expected observation

{expected}''')
    finish=md(f'''## Your turn

{exercise}

## Recap

{recap}''')
    cells=[cells[0],guide,*cells[1:],finish]
    nb={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.11"}},"nbformat":4,"nbformat_minor":5}
    (ROOT/"notebooks"/name).write_text(json.dumps(nb,indent=1),encoding="utf-8")
setup=code('''from pathlib import Path
import sys, json
DAY=Path.cwd()
if (DAY/"day_04_multi_agent_systems").exists(): DAY=DAY/"day_04_multi_agent_systems"
elif DAY.name=="notebooks": DAY=DAY.parent
if not (DAY/"src"/"review_team").exists(): raise RuntimeError("Launch Jupyter from the repository, day folder, or notebooks folder.")
sys.path.insert(0,str(DAY/"src"))
SOURCE=(DAY/"data"/"seeded_artifact"/"order_service.py").read_text(encoding="utf-8")
GOLDEN=DAY/"data"/"golden_defects.json"
print("Artifact lines:",len(SOURCE.splitlines()))''')

write("01_seeded_artifact_and_golden_set.ipynb",[
md('''# 1. A review task we can measure

“The review sounds good” is not evaluation. This supplied synthetic artifact contains seeded correctness, security, and maintainability defects. First review it without the answer key; later the golden set lets us measure recall and false positives.

The artifact is intentionally unsafe and must never be reused.'''),setup,
code('''for number,line in enumerate(SOURCE.splitlines(),1): print(f"{number:>2}: {line}")'''),
md('''## Your independent review

Record each suspected defect as category, line, evidence, severity, and correction. Evidence must point to the artifact; vague style opinions do not count. Only after this attempt, reveal the golden set.'''),
code('''golden=json.loads(GOLDEN.read_text(encoding="utf-8"))
print("Known defects by category:")
for category in ("correctness","security","maintainability"):
    print(category,[x["id"] for x in golden if x["category"]==category])''')])

write("02_single_reviewer_baseline.ipynb",[
md('''# 2. Single-reviewer baseline

One reviewer sees the whole artifact and all concerns. Both routes use the same provider contract: the structured mock keeps class reliable, while OpenRouter supplies the live experiment.'''),setup,
code('''import os
from review_team import MockStructuredReviewer,OpenRouterReviewer,run_model_review,evaluate
provider=OpenRouterReviewer() if os.getenv("OPENROUTER_API_KEY") else MockStructuredReviewer()
single=run_model_review(SOURCE,provider,"general")
for finding in single.findings: print(finding.as_dict())
print(evaluate(single,GOLDEN))'''),
md('''## Inspect the provider boundary

`OpenRouterReviewer` asks for bounded JSON, validates every finding, and records tokens and cost. `MockStructuredReviewer` exercises the same role contract without inference. Neither receives the golden set. Repeat live runs may vary, so preserve each trace.'''),
md('''### Inspect before improving

Which categories were missed? Were claims evidenced? A larger prompt is not automatically a better system; establish the baseline first.''')])

write("03_deterministic_checks.ipynb",[
md('''# 3. Deterministic tools before model judgment

Parsers, tests, linters, and type checkers provide reproducible evidence. Use them for facts they can establish; reserve model judgment for ambiguity and explanation.'''),setup,
code('''from review_team import deterministic_checks,run_augmented,evaluate
checks=deterministic_checks(SOURCE)
for finding in checks: print(finding.as_dict())
augmented=run_augmented(SOURCE)
print(evaluate(augmented,GOLDEN))
print("Trace:",augmented.trace)'''),
md('''## Boundary

Our small AST checker detects `eval`, mutable defaults, and broad exceptions. It does not prove exploitability or business correctness. In a larger course, pytest, Ruff, Bandit, and mypy could supply additional objective signals—but adding tools without teaching their output would overload this course.''')])

write("04_parallel_specialist_reviewers.ipynb",[
md('''# 4. Parallel specialist reviewers

Multi-agent is useful when work decomposes into independent perspectives. Correctness, security, and maintainability reviewers receive the same immutable artifact and return the same structured contract. Fan-out is capped at three; no reviewer can delegate.'''),setup,
code('''from review_team import specialist_review
categories=["correctness","security","maintainability"]
groups={category:specialist_review(SOURCE,category) for category in categories}
for category,findings in groups.items():
    print("\\n",category)
    for finding in findings: print(finding.as_dict())'''),
md('''## Why parallel?

These branches do not depend on one another, so they may run concurrently and later fan in. Parallelism can reduce wall time with hosted APIs, but raises calls, tokens, rate-limit pressure, and debugging complexity. Local code may be too fast for timing differences to matter.'''),
code('''import os
from review_team import MockStructuredReviewer,OpenRouterReviewer,run_model_multi
provider=OpenRouterReviewer() if os.getenv("OPENROUTER_API_KEY") else MockStructuredReviewer()
multi=run_model_multi(SOURCE,provider)
print("Calls:",multi.model_calls,"tokens (input estimate):",multi.estimated_tokens)
print("Trace:",multi.trace)'''),
md('''## Optional direct LangGraph

Represent state as artifact plus lists of structured findings. Add three reviewer nodes from `START`, connect all to one supervisor, and compile. Use a reducer for concurrently returned lists. LangGraph coordinates state; it does not make reviewer judgment correct.''')])

write("05_supervisor_synthesis.ipynb",[
md('''# 5. Supervisor synthesis

Fan-out creates duplicates and inconsistent severity. The supervisor’s narrow job is to validate fields, deduplicate by stable identity, rank, cap output, and terminate. It does not start another open-ended conversation.'''),setup,
code('''from review_team import deterministic_checks,specialist_review,synthesize
groups=[deterministic_checks(SOURCE)] + [specialist_review(SOURCE,c) for c in ("correctness","security","maintainability")]
print("Before fan-in:",sum(map(len,groups)))
final=synthesize(groups,max_findings=20)
print("After deduplication:",len(final))
for finding in final: print(finding.severity,finding.id,finding.title)'''),
md('''## Handoffs are contracts

Only `Finding` objects cross the boundary—not personas, hidden chain-of-thought, or full conversations. Stable IDs make deduplication easy in this seeded lab. Real systems need a similarity rule plus human review because two differently worded findings may describe one root cause.''')])

write("06_comparative_evaluation.ipynb",[
md('''# 6. Comparative evaluation

Run all systems on the same artifact and answer with measurements: Did specialization improve defect recall enough to justify extra calls, tokens, latency, cost, and operational complexity? The single reviewer is allowed to win.'''),setup,
code('''import os
from review_team import *
provider=OpenRouterReviewer() if os.getenv("OPENROUTER_API_KEY") else MockStructuredReviewer()
runs=[run_model_review(SOURCE,provider,"general"),run_augmented(SOURCE),run_model_multi(SOURCE,provider)]
rows=[evaluate(run,GOLDEN,price_per_million_tokens=0.0) for run in runs]
headers=["system","found","recall","false_positives","duplicates","model_calls","estimated_tokens","elapsed_ms","estimated_cost_usd"]
print(" | ".join(headers))
for row in rows: print(" | ".join(str(row[h]) for h in headers))'''),
md('''## Interpret carefully

Our offline specialists encode known category patterns, so their 100% result validates orchestration—not general model intelligence. A live A/B should hide the golden set, repeat trials, pin model/configuration, and report variance. Token counts here approximate repeated source input; provider usage is preferable for live runs.'''),
code('''for row in rows: print(row["system"],"missed:",row["missed"])
best=max(rows,key=lambda r:(r["recall"],-r["model_calls"]))
print("Best under recall-then-fewer-calls rule:",best["system"])''')])

write("07_project_engineering_review_team.ipynb",[
md('''# 7. Project: Engineering Design Review Team

Demonstrate three bounded systems, inspect their traces, and defend a deployment choice. The goal is not “more agents”; it is the smallest system whose measured quality meets the requirement.'''),setup,
code('''import os
from review_team import *
provider=OpenRouterReviewer() if os.getenv("OPENROUTER_API_KEY") else MockStructuredReviewer()
systems=[run_model_review(SOURCE,provider,"general"),run_augmented(SOURCE),run_model_multi(SOURCE,provider)]
reports=[]
for run in systems:
    report=evaluate(run,GOLDEN); reports.append(report)
    print("\\nSYSTEM",run.system,report)
    for event in run.trace: print(" ",event)'''),
code('''assert reports[0]["model_calls"]==1 and reports[2]["model_calls"]==3
assert all(0.0<=r["recall"]<=1.0 for r in reports)
print("Structural comparison checks passed; quality is an observed result, not an assertion.")'''),
md('''## Decision memo

Submit one paragraph naming your chosen system and evidence. Include recall, false positives, calls/tokens, latency caveats, cost assumption, and debugging burden. Then describe one condition that would reverse your choice.

### Repeat the experiment

When using OpenRouter, repeat both provider-backed systems with the same model and configuration. Keep prompts scoped, output bounded, and raw traces saved locally or optionally in LangSmith using only the supplied artifact. Report variance rather than selecting the best single run.''')])
print("Built 7 Day 4 notebooks")
