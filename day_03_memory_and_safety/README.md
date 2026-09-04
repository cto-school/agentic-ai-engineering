# Day 3 — Memory, Guardrails and Safety

**Project:** Safe Personal Task Agent — an assistant that remembers a user's preferences, plans in
the open, and can only act through a policy layer a model cannot argue with.

## The notebook

Students open **one** Google Colab notebook, `day_03_complete.ipynb`, and run it top to bottom.
It is self-contained: no repository clone, no `src/` imports, no local files, no `.env`. The API key
comes from a Colab secret named `OPENROUTER_API_KEY` (or is typed once when the setup cell asks).
Without a key the notebook runs on a built-in mock model whose replies are canned and whose request
and response shapes are real. The day's two data files are written by the notebook itself into a
`day3_data/` folder in the first minute.

Day 1's `chat()`, `make_tool`, `execute_tool_call`, `assistant_message` and `run_agent` are
re-created verbatim in a single **"Carried over from Day 1"** cell near the top, and section 3.6
uses that loop to show what it cannot do: valid arguments were enough to wipe the task list.

Every section is a step-by-step build — a short explanation, a code cell that does one thing and
prints what happened, and a two-question checkpoint with folded answers. Compaction is the day's one
hands-on exercise: students write `compact_history`, run a behavioural check, then read the commented
reference solution the rest of the day uses.

| Section | Lesson file (derived) | What is built |
|---|---|---|
| 3.1 | `01_conversation_history.ipynb` | messages as program-owned state; a local stub and `chat()` both forget; history grows |
| 3.2 | `02_exercise_context_compaction.ipynb` | `estimate_tokens`, `key_fact`, `summarize_messages`; **exercise:** `compact_history` with a budget; what the summary lost |
| 3.3 | `03_custom_persistent_memory.ipynb` | `MemoryStore` on SQLite: add / search / update / delete, per-user scope, conflict rule |
| 3.4 | `04_mem0_platform.ipynb` | optional hosted memory: guarded import, captured response, trade-off table |
| 3.5 | `05_small_plans.ipynb` | `make_plan` with a hard step cap; risk class per step vs a keyword guess |
| 3.6 | `06_tools_with_side_effects.ipynb` | `SimulatedWorkspace` + four classified tools; direct calls and Day 1's loop both act unchecked |
| 3.7 | `07_permissions_and_approval.ipynb` | `POLICY` and `TaskAgent`: allow / approval / deny, approval card, reject, resume re-check, hidden tools |
| 3.8 | `08_observability_and_safety_evaluation.ipynb` | event trace, `tool_error`, idempotent double approval, indirect injection, 12-case suite |
| 3.9 | `09_project_safe_task_agent.ipynb` | the whole chain end to end, three failure cases, trace + suite as evidence |

The files under `notebooks/` are generated from the day notebook by `split_day_notebooks.py`
for the course portal. Edit the day notebook, then re-run the split; do not edit the lesson files.

## Live versus mock

| Mode | When | What differs |
|---|---|---|
| Mock | no key found | proposals come from keyword rules inside the notebook; policy, approval, events and the suite are real |
| Live | key found | `chat()` calls `openai/gpt-oss-120b` through OpenRouter with `reasoning.effort=low`, `temperature=0` |

Both modes run every cell. The one *required live observation* (section 3.9) re-runs the project's
proposal step with a real model and checks that the status, the approval card and the empty outbox
are unchanged. A live model may propose a different tool — or refuse the injected instruction
altogether; the safety invariant is the side-effect count, not the proposal.

The mock model is careless on purpose: it matches single keywords, so "do not delete anything"
makes it propose `delete_all_tasks`, it names a tool it was never offered, and it copies an
attacker's address out of untrusted content. Every guardrail in the day is visible because of it.

## Failure cases demonstrated in code

| Layer | Trigger | What the student sees |
|---|---|---|
| Context | one message not resent; then compaction inside a 200-token budget | "I cannot answer…" from the stub and the model; the deadline in the first turn is gone |
| Memory | two contradictory records for one question | both returned by search; an explicit rule (newest explicit statement wins) resolves it |
| Tools | direct call, and Day 1's `run_agent`, with valid arguments | `delete_all_tasks` runs and the task list is empty — validation is not authorisation |
| Policy | naive proposal, hidden tool named directly, invented tool name | `denied` in all three cases, tasks intact |
| Approval | reject; approve twice; policy tightened while paused | `rejected` / one email only / `denied` on resume |
| Tool runtime | a tool whose backend raises `RuntimeError` | `tool_error` recorded, run continues |
| Injection | poisoned tool output and poisoned memory record | `pending_approval` with the attacker's address on the card, and `deny`; outbox empty |

## Data created by the notebook

- `day3_data/synthetic_users.json` — two fictional students with synthetic preferences (seeds memory in 3.3 and in the project).
- `day3_data/safety_cases.json` — twelve fixed cases: ten direct (a caller names a tool) and two
  indirect, where the instruction is hidden inside retrieved content and has to travel through the
  model. The suite checks the policy outcome and the side-effect count, never the wording.

## Hosted-data rule

Fictional users and synthetic content only. Never send student details, real credentials, personal
memories, private documents or real communications to hosted memory or tracing services. Section 3.4
(`mem0ai`) and hosted tracing (LangSmith, Langfuse) are optional and are left commented out.

## Tool policy used in the project

| Tool type | Example | Default handling |
|---|---|---|
| Read-only | view simulated calendar | allow |
| Reversible local write | create draft | allow |
| External action | send simulated email | require approval over the exact stored payload |
| Destructive | delete all tasks | deny (and hidden from the model, which is not what makes it safe) |

Anything absent from the table is denied by default.

## Reference package (optional)

`src/safe_task_agent/` is a packaged version of the same design (context, memory, planning, proposal,
tools, policy, agent, events, evaluation) with tests in `tests/`. It is not used by the notebook; it
exists for instructors and for students who want the notebook's ideas as an installable module.

```powershell
python -m pytest tests -q
python run_project.py
python evaluate_project.py
```

## Deliberately deferred

Enterprise identity and authentication, production sandboxing, automated prompt-injection
classifiers, large-scale memory evaluation, and complex autonomous planning.
