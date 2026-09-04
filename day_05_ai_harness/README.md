# Day 5 — Build a Mini AI Harness

> **Status:** Complete reference harness, harness-driven website-maintenance capstone,
> instructor MCP server, offline fallbacks, and tests are included.

## Project

Days 1–4 each built one agent, and each quietly re-implemented the same chores: pick a
model, describe tools, run a loop, decide whether an action is allowed, remember something,
explain what happened. Day 5 pulls those chores out into a small reusable **harness** —
configuration, provider adapter, tool registry, policy, runtime, events and checkpoints.

The capstone then puts a real workflow on top of that harness. A Website Maintenance Agent
registers its two actions as harness tools with honest risk levels: drafting an update is
`write` (allowed automatically), publishing it is `external` (paused for a human). The
runtime, `policy.decide`, the event log and the checkpoint are exactly the ones built in
lessons 5.2–5.5; `WebsiteGuardrails` adds the domain checks — trusted host, no
instruction-like text in external data, target path inside the site folder.

Everything runs with **no API key**. Live paths are optional and always fall back.

**Classroom notebook:** [`day_05_complete.ipynb`](day_05_complete.ipynb) combines the
sections into one Colab-ready path. The files under `notebooks/` are the modular source.

## Progression

```text
Compare two application-specific agents
-> name the repeated project code
-> central model configuration and a provider adapter
-> reusable runtime with a hard step cap and a retry budget
-> tool registry with schemas and risk levels
-> permissions, approval checkpoints and limits
-> events, durable logs and resumable checkpoints
-> MCP client: discover, classify, then authorise
-> integrated harness hosting several agent configurations
-> a scheduled website-maintenance cycle running on that harness
```

## Concepts introduced

Runtime, harness, provider adapter, registry, risk level, policy, fail-closed, execution
limit, retry budget, exponential backoff, cost attribution, event, checkpoint, protocol,
MCP client, MCP server, automation trigger, change detection, guardrail.

## Notebook sequence

1. `01_what_is_a_harness.ipynb` — loads two agent configs and prints a table mapping each
   Day 1–4 pain point to the harness component that now owns it.
2. `02_model_configuration_and_runtime.ipynb` — reads a config as data, builds the matching
   provider adapter, runs it with a live fallback, and reads the usage fields in the events.
3. `03_tool_registry.ipynb` — registers four tools spanning four risk levels, scopes
   discovery per agent, and rejects four kinds of malformed call before any function runs.
4. `04_permissions_and_limits.ipynb` — prints the risk→decision table, pauses an external
   action on a checkpoint, resolves it to `cancelled` and then to `completed`, denies an
   allow-listed destructive tool, shows an unknown risk level failing closed, and holds a
   500-step config to the runtime's cap.
5. `05_events_logs_and_checkpoints.ipynb` — writes a JSONL event log, resumes a paused run
   from disk with a brand-new runtime, watches a bounded retry with exponential backoff
   recover and then exhaust its budget, and totals per-run cost.
6. `06_mcp_client.ipynb` — discovers a tool offline, classifies and authorises it locally,
   re-classifies it to flip the decision, then repeats the session against the real
   instructor stdio server when the SDK is installed.
7. `07_project_mini_harness.ipynb` — one runtime hosting several agents end to end, then
   adds a **third** agent configuration with zero changes to `src/mini_harness/`.
8. `08_exercise_tool_registry.ipynb` — independent implementation lab (capability-aware
   discovery and dispatch).
9. `09_project_website_maintenance_agent.ipynb` — the operational capstone described above.

## Required environment

- The course core dependencies (`requirements.txt` at the repository root).
- Optional: the MCP Python SDK, pinned in `requirements.txt` as `mcp>=1.27,<2`. Install it
  with `pip install "mcp>=1.27,<2"`. That range is the classroom pin — the SDK is evolving,
  so the course environment, not an unbounded latest install, defines the version.
- `instructor_mcp_server.py` is course infrastructure; students consume it, writing an MCP
  server is an optional extension.

Without the MCP SDK, notebook 06 runs entirely against `FakeMCPClient`, which returns
objects with the same `.name` / `.description` / `.inputSchema` attributes as the real SDK,
so no access pattern has to be unlearned. Writing an MCP server, FastAPI and Docker are
optional extensions rather than core lab requirements.

## Run the reference project

```powershell
py run_project.py           # the mini harness in mock mode: two agents, one approval
py run_website_agent.py     # one scheduled tick of the capstone; stops at pending_approval
py -m pytest tests -q
```

Use `python` instead of `py` where that is the configured launcher. `run_website_agent.py`
writes only under `data/generated/`, which is git-ignored; delete that folder to reset.

## Minimum harness responsibilities

- Load model configuration and select a provider adapter.
- Send model messages and optional tool schemas.
- Register tools with input schemas and risk levels.
- Validate requested tool arguments before execution.
- Allow, deny, or request approval according to application policy — failing closed on
  anything it does not recognise.
- Stop after a configured maximum number of steps, capped by the runtime.
- Retry transient provider failures a bounded number of times, and record every attempt.
- Record model, tool, approval, failure, and completion events.
- Expose a small memory interface.
- Discover and call one local MCP tool.
- Load several agent configurations without rewriting the runtime.

## Core principle

Tool discovery is not authorization. A capability being visible through MCP does not
automatically make it safe or permitted to call.

## Deliberately deferred

- Production authentication
- Remote MCP deployment
- Distributed execution
- Kubernetes
- Advanced isolation and operating-system sandboxes
- General-purpose coding-agent features

## Project completion checklist

- [x] Model routing is centralized and mock mode works offline.
- [x] Tools are registered rather than hardcoded into the loop.
- [x] Tool arguments are validated before execution.
- [x] Policy enforcement is performed by Python, not delegated to the model, and an
      unrecognised risk level denies rather than raising.
- [x] Runs terminate with completed, pending_approval, cancelled, failed, or step_limit.
- [x] A configuration cannot raise the runtime's hard step cap.
- [x] Transient provider failures are retried with bounded exponential backoff.
- [x] Events explain the sequence of execution and are durable as JSONL.
- [x] One local MCP capability can be discovered and invoked, with an offline fallback that
      has the same object shape.
- [x] The same runtime hosts the research agent, the task agent, a third agent written
      during lesson 7, and the website agent of the capstone.
- [x] The capstone's real file write happens only after an explicit human approval.
- [x] The student can explain the difference between an agent, framework, protocol,
      runtime, and harness.

## Optional extensions

- Expose the harness through FastAPI.
- Package the service with Docker.
- Write a trivial two-tool MCP server.
- Add a second hosted model configuration.
- Export traces to LangSmith or OpenTelemetry.
