# Day 4 — Multi-Agent Engineering Review and Evaluation

> **Status:** Complete reference implementation, six guided lesson notebooks, one project
> notebook, one exercise notebook, seeded artifact, golden defect set, comparative
> evaluator, and tests.

## Project

Build an Engineering Design Review Team that examines a supplied Python artifact
containing nine seeded defects, then decide **with measurements** whether the team was
worth building.

All required theory is embedded in the notebooks at the point where it is used. Notebook
08 is the independent supervisor-merge implementation lab.

**Classroom notebook:** [`day_04_complete.ipynb`](day_04_complete.ipynb) combines all
sections into one Colab-ready learning path. The files under `notebooks/` remain the
modular source and standalone lesson versions.

## Progression

```text
Seeded artifact and golden defect list
-> single-reviewer baseline
-> deterministic AST checks before model judgment
-> parallel specialist reviewers (fan-out)
-> supervisor synthesis (fan-in)
-> measured A/B comparison across two scenarios
```

## Concepts introduced

Workflow, specialist role, handoff, supervisor, shared artifact, shared state, sequential
execution, parallel fan-out/fan-in, defect recall, false positive, duplicate, false merge,
trace, telemetry, and evaluation.

## Notebook sequence

1. `01_seeded_artifact_and_golden_set.ipynb` — the review task and the hidden answer key.
2. `02_single_reviewer_baseline.ipynb` — one reviewer through a provider contract.
3. `03_deterministic_checks.ipynb` — AST facts before model judgment.
4. `04_parallel_specialist_reviewers.ipynb` — fan-out, shared state, sequential vs threaded timing.
5. `05_supervisor_synthesis.ipynb` — fan-in: merge, rank, cap, report what was dropped.
6. `06_comparative_evaluation.ipynb` — both scenarios, one table, read which system won.
7. `07_project_engineering_review_team.ipynb` — integrate, trace, and defend a choice.
8. `08_exercise_supervisor_merge.ipynb` — independently implement deterministic aggregation
   and partial-failure handling.

## The three systems (one naming scheme)

| Function | Model calls | What it adds |
| --- | --- | --- |
| `run_single_reviewer(source, provider)` | 1 | nothing; the baseline |
| `run_checks_plus_reviewer(source, provider)` | 1 | deterministic AST checks (0 tokens) + supervisor |
| `run_specialist_team(source, provider, parallel=False)` | 3 | AST checks + 3 specialists + supervisor |

All three take the same `provider`, so the comparison changes the architecture while
holding the reviewer constant. Providers satisfy one contract:
`findings, usage = provider.review(source, role)` — see `MockStructuredReviewer`,
`OpenRouterReviewer`, and `FallbackReviewer` (live with a mock safety net).

## Two scenarios, two different winners

`MockStructuredReviewer(scenario=...)` chooses which blind spots the reviewer has:

| Scenario | single | checks + single | specialist team | verdict |
| --- | --- | --- | --- | --- |
| `blind_spots` | 5/9, 1 call | 6/9, 1 call | **9/9, 3 calls** | the team earns its cost |
| `strong_generalist` | **8/9, 1 call** | 8/9, 1 call | 8/9, 3 calls | the team costs 3x for nothing |

Students must read the table to say which system won. The single reviewer is allowed to
win, and in the second scenario it does.

## Required environment

- Python 3.10+ and the standard library (the whole offline path uses nothing else)
- Pytest
- Structured local logging via each run's `trace`
- The instructor-supplied Python artifact with seeded defects, under `data/`

OpenRouter is optional and only enables the live experiment. LangGraph and LangSmith are
**not** used on Day 4; the fan-out here is a bounded `ThreadPoolExecutor` so the mechanism
stays visible. All core inspection works offline.

## Run the reference project

```powershell
py run_project.py                     # traces + findings, blind_spots scenario
py run_project.py strong_generalist   # the scenario where one reviewer is enough
py evaluate_project.py                # the comparison table for BOTH scenarios
py evaluate_project.py --write        # also refresh data/captured_comparison.json
py -m pytest tests -q
```

Use `python` instead of `py` where that is the configured launcher.

## Shared artifact policy

Agents exchange structured `Finding` records rather than unrestricted conversational
transcripts. Each finding carries category, location, evidence, severity, recommended
correction, and the role that produced it.

## Honest measurement rules

- Token and cost figures come from the provider's own usage report. A step that makes no
  model call reports zero and is labelled `no model call` in the trace.
- Each known defect counts **once**. Extra reports of the same defect are `duplicates`.
- The supervisor reports `merged_duplicates` and `dropped_over_cap`; nothing is truncated
  silently.
- Deduplication by category + line proximity is live, and it can **falsely merge** two
  different defects on adjacent lines. Notebook 05 demonstrates that failure.
- Tests assert bounds, telemetry and reproducibility. They never assert that the
  multi-agent system wins.

## Deliberately deferred

- Agent swarms
- Open-ended delegation
- Distributed workers
- Complex async programming
- Framework comparisons
- Fully autonomous software development

## Project completion checklist

- [x] 1. The fixed workflow baseline runs offline with no API key.
- [x] 2. Reviewers produce structured, evidenced findings through one provider contract.
- [x] 3. Deterministic AST checks report objective results at zero model cost.
- [x] 4. Fan-out is bounded at three branches and can run sequentially or in threads.
- [x] 5. The supervisor deduplicates, ranks, caps, and reports what it merged and dropped.
- [x] 6. At least one trace/run history is inspectable for every system.
- [x] 7. The evaluator credits each defect once and separates duplicates from finds.
- [x] 8. The student can defend with measurements whether multiple agents helped — in
      both scenarios, including the one where they did not.

## Optional extensions

- Add a performance or documentation specialist without changing the supervisor.
- Add a third scenario in `reviewers.SCENARIOS` and predict the winner before running it.
- Replace line-proximity merging with an embedding similarity rule and measure the change
  in duplicates and false merges.
