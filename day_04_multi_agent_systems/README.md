# Day 4 — Multi-Agent Systems

**Project:** Engineering Design Review Team — three review architectures over one seeded artifact,
scored against a hidden defect list, with a memo that says which one to deploy.

## The notebook

Students open **one** Google Colab notebook, `day_04_complete.ipynb`, and run it top to bottom.
It is self-contained: no repository clone, no local files, no `.env`. The API key comes from a
Colab secret named `OPENROUTER_API_KEY` (or is typed once when the setup cell asks). Without a key
the notebook runs on a built-in mock model whose replies are *scripted reviewer* rules but whose
request and reply shapes — a strict JSON schema, validated into `Finding` records — are exactly
what the live model goes through. The artifact under review and the golden defect set are written
to `day_04_data/` by the notebook itself.

Every section is a step-by-step build: a short explanation, a code cell that does one thing and
prints what happened, and a two-question checkpoint with folded answers. The supervisor merge is
the day's one hands-on exercise: students write `merge_findings`, run a four-case check, then read
the commented reference solution — which is the supervisor the rest of the day uses.

| Section | Lesson file (derived) | What is built |
|---|---|---|
| 4.1 | `01_seeded_artifact_and_golden_set.ipynb` | seeded artifact written to disk; Pydantic `Finding` contract; predict two defects, then the golden set; `match_to_golden` / `score` (each defect credited once) |
| 4.2 | `02_single_reviewer_baseline.ipynb` | one request shape + strict schema; `parse_findings` with the role contract; scripted reviewer with two blind-spot scenarios; `ReviewRun` telemetry; `review_with_fallback` |
| 4.3 | `03_deterministic_checks.ipynb` | AST checks (eval, mutable default, broad except) at 0 tokens; `AST-…` ids matched by location; recall 5/9 → 6/9 with unmerged duplicates |
| 4.4 | `04_parallel_specialist_reviewers.ipynb` | fan-out, shared state, handoff, fan-in named on this example; `fan_out` sequential vs `ThreadPoolExecutor`, timed |
| 4.5 | `05_exercise_supervisor_synthesis.ipynb` | **exercise:** `merge_findings` — failed branches, id vs location merging, severity ranking, cap with `dropped_over_cap`; false-merge demonstration |
| 4.6 | `06_comparative_evaluation.ipynb` | `run_checks_plus_reviewer`, `run_specialist_team`; `evaluate`; two scenario tables; when multi-agent is **not** worth it; captured comparison |
| 4.7 | `07_project_engineering_review_team.ipynb` | both scenarios end to end, full trace, structural bound assertions, quality bar that flips the recommendation, decision memo |

The files under `notebooks/` are generated from the day notebook by `split_day_notebooks.py`
for the course portal. Edit the day notebook, then re-run the split; do not edit the lesson files.

## The three systems (one naming scheme)

| Function | Model calls | What it adds |
|---|---|---|
| `run_single_reviewer(source, model)` | 1 | nothing; the baseline |
| `run_checks_plus_reviewer(source, model)` | 1 | deterministic AST checks (0 tokens) + supervisor |
| `run_specialist_team(source, model, parallel=True)` | 3 | AST checks + 3 specialists + supervisor |

All three take the same `model` (any function with `chat`'s signature), so the comparison changes
the **architecture** while holding the reviewer constant. Every reviewer — live, scripted, or
deliberately broken — goes through `call_reviewer(source, role, model)`: build the request,
send it, validate the reply into `Finding` records.

## Two scenarios, two different winners

`make_mock_model(scenario)` chooses which blind spots the scripted reviewer has:

| Scenario | single | checks + single | specialist team | verdict |
|---|---|---|---|---|
| `blind_spots` | 5/9, 1 call, 609 tok | 6/9, 1 call, 609 tok | **9/9, 3 calls, 1448 tok** | the team earns its cost |
| `strong_generalist` | **8/9, 1 call, 789 tok** | 8/9, 1 call, 789 tok | 8/9, 3 calls, 1393 tok | the team costs 3x for nothing |

Students read the table and say which system won. The single reviewer is allowed to win, and in
the second world it does. At a quality bar of 1.0 that world has **no** deployable system: the
missed defect is a capability gap that no orchestration can close.

## Live versus mock

| Mode | When | What differs |
|---|---|---|
| Mock | no key found | the reviewer is a scripted rule table with chosen blind spots; the schema, validation, fan-out, supervisor and scoring are real; usage is an honest ~4-characters-per-token estimate |
| Live | key found | `chat()` calls `openai/gpt-oss-120b` through OpenRouter with `reasoning.effort=low`, `temperature=0`, a strict findings schema, and real usage numbers |

Both modes run every cell. The scenario A/B stays scripted on purpose — a real model cannot be
given chosen blind spots — and the one *required live observation* (section 4.6) asks for the live
reviewer's findings and usage next to the mock baseline, or the captured table if the provider is down.

## Failure cases demonstrated in code

| Layer | Trigger | What the student sees |
|---|---|---|
| Contract | a finding with empty evidence; a security reviewer returning a correctness finding; a non-integer line | `ValidationError` / `ValueError` before anything is merged |
| Provider | a model that raises on every call | one printed fallback line, then the scripted reviewer completes the run |
| Branch | a branch arriving as `{"status": "error"}` | the supervisor announces it and merges the survivors |
| Merge | two different security defects one line apart | a **false merge**: the second defect is deleted by the deduplication rule |
| Cap | `max_findings=4` on nine findings | `dropped_over_cap = 5`, never a silent truncation |

## Honest measurement rules

- Token figures come from the model's own usage report. A step that makes no model call reports
  zero and is labelled `no model call` in the trace.
- Each known defect counts **once**; extra reports are `duplicates`. Matching is by category plus
  line proximity, because real reviewers invent their own ids.
- The supervisor reports `merged_duplicates` and `dropped_over_cap`.
- Assertions cover structure (bounds, evidence, cap). Nothing asserts that the team wins.

## Reference package (optional)

`src/review_team/` is a packaged version of the same design (contracts, scripted and live
reviewer providers, AST checks, supervisor, the three workflows, evaluator) with tests in
`tests/`. It is not used by the notebook; it exists for instructors and for students who want the
notebook's ideas as an installable module.

```powershell
python -m pytest tests -q
python run_project.py                     # traces + findings, blind_spots scenario
python run_project.py strong_generalist   # the world where one reviewer is enough
python evaluate_project.py                # the comparison table for BOTH scenarios
```
