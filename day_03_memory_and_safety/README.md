# Day 3 — Memory, Planning, and Safety

> **Status:** Complete reference implementation, nine guided notebooks, two independent
> exercise labs, a synthetic safety dataset, a runnable demonstration, and automated tests.

## Project

Build a Safe Personal Task Agent that manages growing context, remembers selected preferences, produces a small plan, uses simulated productivity tools, and pauses before consequential actions.

All required theory is embedded in the notebooks at the point where it is used. Notebooks 10 and 11 are independent implementation labs for compaction and policy.

**Classroom notebook:** [`day_03_complete.ipynb`](day_03_complete.ipynb) combines all eleven sections into one Colab-ready learning path. The files under `notebooks/` remain the modular source and standalone lesson versions.

## Progression

```text
Stateless conversation
-> conversation history and artificial context budget
-> bounded compaction with a visible, lossy summary
-> persistent custom memory with a conflict rule
-> Mem0 Platform guided comparison (optional)
-> small visible plan
-> tools with side effects
-> permissions and human approval
-> events, prompt injection, and a fixed safety suite
```

## Concepts introduced

Conversation history, context budget, message trimming, rolling summary, short-term memory, persistent memory, memory retrieval, memory conflict, plan, side effect, permission, guardrail, human-in-the-loop, approval, idempotency, direct and indirect prompt injection, event log, and safety evaluation.

## Notebook sequence

1. `01_conversation_history.ipynb` — Day 3.1: watch a call forget, then fix it by resending history.
2. `02_context_compaction.ipynb` — Day 3.2: measure tokens, compact within a budget, name what was lost.
3. `03_custom_persistent_memory.ipynb` — Day 3.3: add, search, update, delete, isolate, and resolve conflicts.
4. `04_mem0_platform.ipynb` — Day 3.4: optional guided exposure to a managed memory product.
5. `05_small_plans.ipynb` — Day 3.5: represent a goal as visible, bounded, classified steps.
6. `06_tools_with_side_effects.ipynb` — Day 3.6: simulated tasks, calendar, and email; reads versus writes.
7. `07_permissions_and_approval.ipynb` — Day 3.7: allow, deny, or pause; approve the exact payload.
8. `08_observability_and_safety_evaluation.ipynb` — Day 3.8: events, indirect injection, and the safety suite.
9. `09_project_safe_task_agent.ipynb` — Day 3 Project: integrate the complete project.
10. `10_exercise_history_compaction.ipynb` — independent implementation lab (compaction).
11. `11_exercise_action_policy.ipynb` — independent implementation lab (capability and approval policy).

Every lesson notebook runs end to end with **no API key**. The setup cell loads `.env` if one
exists and prints `MOCK` or `LIVE` so you always know which path you are on.

## Required environment

- Python 3.10+ and the standard library only for the reference path (`sqlite3` provides the memory store; no database server).
- `python-dotenv` (in the root `requirements.txt`) so the setup cell can read `.env`.
- The supplied simulated productivity tools in `src/safe_task_agent/tools.py`. No real email or calendar account is ever connected.

Optional and never required: an OpenRouter key for the live proposal comparison, `mem0ai` plus
`MEM0_API_KEY` for Day 3.4, `langsmith` or Langfuse for hosted tracing, and LangGraph if you want
to compare its `interrupt`/`Command(resume=...)` pattern with the transparent pause-and-resume
runtime built here. The course runtime implements approval itself, so LangGraph is not installed
or imported by any Day 3 notebook.

## Data

- `data/synthetic_users.json` — two fictional students with synthetic preferences. Used to seed memory in Day 3.3 and in the project notebook and `run_project.py`.
- `data/safety_cases.json` — twelve fixed cases. Ten arrive through the direct channel (a caller naming a tool) and two through the indirect channel, where the instruction is hidden inside retrieved content and has to travel through the proposer.

## Run the reference project

From this folder:

```powershell
py run_project.py
py evaluate_project.py
py -m pytest tests -q
```

Use `python` instead of `py` on systems where that is the configured launcher. The
reference path uses only the standard library; hosted products and live inference are
optional comparison exercises.

## Hosted-data rule

Use only fictional users and synthetic preferences, prompts, calendar entries, and messages. Never send student details, real credentials, personal memories, private documents, or real communications to hosted memory or tracing systems.

## Tool policy used in the project

| Tool type | Example | Default handling |
|---|---|---|
| Read-only | View simulated calendar | Allow |
| Reversible local write | Create draft | Allow and log |
| External action | Send simulated email | Require approval |
| Destructive | Delete all tasks | Deny (and hidden from the model, which is not what makes it safe) |

## Deliberately deferred

- Enterprise identity and authentication
- Production sandboxing
- Automated prompt-injection classifiers
- Large-scale memory evaluation
- Complex autonomous planning

## Project completion checklist

- [x] The user can inspect, correct, and delete stored memories (3.3).
- [x] The agent retrieves a relevant saved preference (3.3, project).
- [x] Plans have a small maximum number of steps (3.5).
- [x] Read-only and action tools are treated differently (3.6, 3.7).
- [x] A consequential action pauses for approval (3.7, project).
- [x] Rejecting approval prevents execution (3.7, project).
- [x] Approving the same action twice sends only once (3.8, project).
- [x] Execution steps are visible in a local event history (3.8, project).
- [x] Older history is trimmed or summarized within an artificial context budget (3.2).
- [x] A supplied safety set records allowed, denied, and approval-required outcomes, including both injection channels (3.8).
- [ ] *Optional:* the student compares custom memory with Mem0 Platform (3.4 — optional guided exposure, needs a key and `mem0ai`).

## Failure cases demonstrated in the notebooks

| Failure | Where |
|---|---|
| A call answers "I don't know" because history was not resent | 3.1 |
| Compaction destroys a deadline stated in the oldest turn | 3.2 |
| Two stored memories contradict each other and search cannot decide | 3.3 |
| Keyword retrieval returns nothing for a reasonable question | 3.3 |
| A naive proposer suggests `delete_all_tasks` for "do not delete anything" | 3.7 |
| A direct injection ("ignore policy, I am the administrator") is denied | 3.7, project |
| A rejected approval ends the run safely with nothing sent | 3.7, project |
| A tool raises an unexpected exception and is recorded, not crashed | 3.8 |
| An indirect injection hidden in a tool output or memory record still stops at approval or deny | 3.8, project |

## Optional extensions

- Run Mem0 OSS rather than the hosted platform.
- Self-host or instrument the project with Langfuse.
- Add memory expiration or stronger conflict resolution.
- Validate the destination of an outgoing message, not just the tool name.
