# Day 4 — Multi-Agent Engineering Review and Evaluation

> **Status:** Complete reference implementation, seven guided notebooks, seeded
> artifact, golden defect set, comparative evaluator, and tests are included.

## Project

All required theory is embedded in the notebooks at the point where it is used. Notebook 08 is the independent supervisor-merge implementation lab.

Build an Engineering Design Review Team that examines a supplied Python artifact containing seeded defects. Compare a single reviewer, a deterministic analysis workflow, and specialized parallel reviewers with supervisor synthesis.

## Progression

```text
Seeded artifact and golden defect list
-> single-reviewer baseline
-> deterministic tests/static checks
-> parallel specialist reviewers
-> supervisor synthesis
-> measured A/B comparison
```

## Concepts introduced

Workflow, specialist role, handoff, supervisor, shared artifact, shared state, sequential execution, parallel fan-out/fan-in, defect recall, false positive, trace, and evaluation.

## Notebook sequence

1. `01_seeded_artifact_and_golden_set.ipynb` — understand the review task and known defects.
2. `02_single_reviewer_baseline.ipynb` — ask one agent to review every concern.
3. `03_deterministic_checks.ipynb` — run tests and static checks before model judgment.
4. `04_parallel_specialist_reviewers.ipynb` — correctness, security, and maintainability fan-out.
5. `05_supervisor_synthesis.ipynb` — merge, deduplicate, rank, and terminate.
6. `06_comparative_evaluation.ipynb` — measure defect discovery and system cost.
7. `07_project_engineering_review_team.ipynb` — integrate and demonstrate the system.
8. `08_exercise_supervisor_merge.ipynb` — independently implement deterministic aggregation and partial-failure handling.

## Required environment

- LangGraph
- Pytest
- Structured local logging
- Small, instructor-supplied Python artifact with seeded defects and tests

LangSmith is optional; all core inspection must work locally.

## Run the reference project

```powershell
py run_project.py
py evaluate_project.py
py -m pytest tests -q
```

Use `python` instead of `py` where that is the configured launcher. The required
offline path uses only the standard library; LangGraph, OpenRouter, and LangSmith are
guided extensions.

## Shared artifact policy

Agents exchange structured findings rather than unrestricted conversational transcripts. Each finding includes category, location, evidence, severity, and recommended correction.

## Comparison required

Run the same seeded artifact through:

1. A single-reviewer baseline
2. Deterministic tests/static checks plus one reviewer
3. Parallel specialist reviewers plus supervisor

Compare known defects discovered, false positives, duplicates, model calls, tokens, elapsed time, estimated cost, and ease of debugging. The single reviewer is allowed to win.

## Deliberately deferred

- Agent swarms
- Open-ended delegation
- Distributed workers
- Complex async programming
- Framework comparisons
- Fully autonomous software development

## Project completion checklist

- [x] The fixed workflow baseline runs.
- [x] Reviewers produce structured, evidenced findings.
- [x] Deterministic tools report objective results.
- [x] The supervisor deduplicates and synthesizes findings.
- [x] Fan-out/fan-in and supervisor execution are bounded.
- [x] At least one trace/run history is inspectable.
- [x] The student can defend with measurements whether multiple agents helped.

## Optional extensions

- Trace the graph in LangSmith.
- Run two independent reviews in parallel.
- Add a performance or documentation specialist without changing the core supervisor.
