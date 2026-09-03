# Day 3 — Memory, Planning, and Safety

> **Status:** Complete reference implementation, nine guided notebooks, synthetic
> safety dataset, runnable demonstration, and automated tests are included.

## Project

Build a Safe Personal Task Agent that manages growing context, remembers selected preferences, produces a small plan, uses simulated productivity tools, and pauses before consequential actions.

All required theory is embedded in the notebooks at the point where it is used. Notebooks 10 and 11 are independent implementation labs for compaction and policy.

## Progression

```text
Stateless conversation
-> conversation history and artificial context budget
-> trimming and rolling summarization
-> persistent custom memory
-> Mem0 Platform guided comparison
-> small visible plan
-> tools with side effects
-> permissions and approval
-> execution history
```

## Concepts introduced

Conversation history, context budget, message trimming, rolling summary, short-term memory, persistent memory, memory retrieval, plan, side effect, permission, guardrail, human-in-the-loop, interrupt, and resume.

## Notebook sequence

1. `01_conversation_history.ipynb` — experience and fix a forgetting chatbot.
2. `02_context_compaction.ipynb` — trim messages and create a rolling summary.
3. `03_custom_persistent_memory.ipynb` — save, search, inspect, update, and delete memory.
4. `04_mem0_platform.ipynb` — compare the transparent store with a managed memory product.
5. `05_small_plans.ipynb` — represent a goal as visible, bounded steps.
6. `06_tools_with_side_effects.ipynb` — simulated tasks, calendar, and email.
7. `07_permissions_and_approval.ipynb` — allow, deny, or pause actions.
8. `08_observability_and_safety_evaluation.ipynb` — local events, LangSmith, and safety cases.
9. `09_project_safe_task_agent.ipynb` — integrate the complete project.
10. `10_exercise_history_compaction.ipynb` — independently implement and test compaction.
11. `11_exercise_action_policy.ipynb` — independently implement and test capability and approval policy.

## Required environment

- Local SQLite or supplied JSON memory store
- Simulated productivity tools
- LangGraph interrupt/resume support
- No real email or calendar account

Mem0 Platform and LangSmith are guided hosted-product exposures using synthetic data. Local memory and structured logs remain fully functional fallbacks. Langfuse is shown as an open/self-hostable observability alternative.

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
| Destructive | Delete all tasks | Deny or require explicit scoped approval |

## Deliberately deferred

- Enterprise identity and authentication
- Production sandboxing
- Automated prompt-injection classifiers
- Large-scale memory evaluation
- Complex autonomous planning

## Project completion checklist

- [x] The user can inspect and delete stored memories.
- [x] The agent retrieves a relevant saved preference.
- [x] Plans have a small maximum number of steps.
- [x] Read-only and action tools are treated differently.
- [x] A consequential action pauses for approval.
- [x] Rejecting approval prevents execution.
- [x] Execution steps are visible in a local history.
- [x] Older history is trimmed or summarized within an artificial context budget.
- [x] The student compares custom memory with Mem0 Platform.
- [x] A supplied safety set records allowed, denied, and approval-required outcomes.

## Failure cases to demonstrate

- Incorrect or conflicting memory
- Irrelevant memory retrieval
- A prompt asking the model to bypass permission checks
- A destructive request
- A rejected approval followed by safe termination

## Optional extensions

- Run Mem0 OSS rather than the hosted platform.
- Self-host or instrument the project with Langfuse.
- Add memory expiration or stronger conflict resolution.
