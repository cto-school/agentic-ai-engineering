# Day 5 — AI Harness and Automation

**Project:** a Mini AI Harness — configuration, provider adapter, tool registry, policy, runtime,
events and checkpoints — with a **Website Maintenance Agent** running on top of it that changes a
real file only after a person approves the exact patch.

## The notebook

Students open **one** Google Colab notebook, `day_05_complete.ipynb`, and run it top to bottom.
It is self-contained: no repository clone, no `src/` imports, no `.env`. The API key comes from a
Colab secret named `OPENROUTER_API_KEY` (or is typed once when the setup cell asks). Without a key
the notebook runs on a built-in mock model *and* a deterministic mock provider, and every mechanism
that matters — scoped discovery, argument validation, the risk-to-decision table, the approval
pause, the step cap, retries, the event log — is real.

Every section is a step-by-step build: a short explanation, a code cell that does one thing and
prints what happened, and a two-question checkpoint with folded answers. The tool registry is the
day's one hands-on exercise: students write it, run a behavioural check, then read the commented
reference solution that the rest of the day uses. Day 1's `chat`, `make_strict`, `make_tool` and
`execute_tool_call` are carried over verbatim in one cell near the top; everything else — the
harness — is built in the notebook, piece by piece.

| Section | Lesson file (derived) | What is built |
|---|---|---|
| 5.1 | `01_what_is_a_harness.ipynb` | the Day 1–4 problem → component table; five dataclasses; agent configs written as JSON data |
| 5.2 | `02_model_configuration_and_runtime.ipynb` | `MockProvider` driven by `mock_plan`; `LiveProvider` wrapping `chat()`; `build_provider`; `EventStore`; bounded retry with backoff |
| 5.3 | `03_exercise_tool_registry.ipynb` | **exercise:** `ToolRegistry` — duplicate/unknown/ungranted/malformed all refused; four tools, four risk levels |
| 5.4 | `04_permissions_and_limits.ipynb` | `RISK_POLICY` + `decide` (fail-closed); `HarnessRuntime`; approval pause → `cancelled` → `completed`; `MAX_STEPS_HARD_CAP` |
| 5.5 | `05_events_logs_and_checkpoints.ipynb` | JSONL event log; `JSONCheckpointStore`; restart-and-resume; retry recovered then exhausted; per-run cost totals |
| 5.6 | `06_mcp_client.ipynb` | `FakeMCPClient` (same `.name`/`.description`/`.inputSchema` shape); local classification; a real `FastMCP` stdio server written and called |
| 5.7 | `07_project_mini_harness.ipynb` | the whole harness hosting two agents, one approval end to end, memory + MCP boundary, a third agent added as data |
| 5.8 | `08_project_website_maintenance_agent.ipynb` | capstone: `propose_update` (write) and `publish_update` (external) as harness tools, guardrails, change detection, poisoned source, live paths |

The files under `notebooks/` are generated from the day notebook by `split_day_notebooks.py`
for the course portal. Edit the day notebook, then re-run the split; do not edit the lesson files.

## Live versus mock

| Mode | When | What differs |
|---|---|---|
| Mock | no key found | `MockProvider` plans tool calls from each config's `mock_plan`; `deterministic_proposer` and a canned model reply write the capstone's text |
| Live | key found | `LiveProvider` calls `openai/gpt-oss-120b` through OpenRouter using the Day 1 `chat()`; `model_proposer` asks the real model for the website update |

Both modes run every cell. The one *required live observation* (section 5.8) compares the model's
proposal with the deterministic one and confirms that no guardrail and no policy decision changes.
Setting `RUN_LIVE_FETCH=1` additionally pulls three real public GitHub releases through the same
`UpdateItem` contract. Neither live path can publish anything: the run still stops at
`pending_approval`.

## Safety behaviour demonstrated in code

| Layer | Trigger | What the student sees |
|---|---|---|
| Registry | duplicate name, unknown tool, ungranted tool, missing/mistyped/undeclared argument | `ValueError` / `KeyError` / `PermissionError` / `TypeError` before any function body runs |
| Policy | `external` tool; allow-listed `destructive` tool; `risk="quantum"` | `pending_approval`; `deny` with a recorded `policy_decision`; `deny` by `RISK_POLICY.get(..., "deny")` |
| Limits | a model that never says "done"; a config asking for 500 steps | status `step_limit`, with the *effective* limit (10) in the event |
| Provider | one transient failure; a permanent one; a `ValueError` | `provider_retry` with doubling backoff; `provider_retry_budget_exhausted`; `provider_error_not_retried` |
| Durability | checkpoint deleted before `resume` | `failed` — the harness will not ask the model to invent the pending action again |
| Guardrails | a feed item containing "ignore all previous instructions"; a downgraded risk level | `tool_failed` before any draft exists; the human gate disappearing when `publish_update` becomes `write` |

Everything the notebook writes goes to `data/generated/day5_workspace/` (git-ignored): the agent
configs, the update feeds, one MCP server file, and a timestamped folder per run holding
`events.jsonl`, `checkpoints/`, `state.json` and the generated `site/`. Delete the folder to reset.

## Reference package (optional)

`src/mini_harness/` is a packaged version of the same design (schemas, registry, policy, providers,
runtime, events, MCP client, website agent) with tests in `tests/`. It is not used by the notebook;
it exists for instructors and for students who want the notebook's ideas as an installable module.
`instructor_mcp_server.py`, `run_project.py` and `run_website_agent.py` belong to that package.

```powershell
python -m pytest tests -q
python run_project.py
python run_website_agent.py
```

## Core principle

Tool discovery is not authorization. A capability being visible — locally or over MCP — does not
make it safe or permitted to call. Configuration proposes; the harness decides; a person approves
anything that leaves the machine.
