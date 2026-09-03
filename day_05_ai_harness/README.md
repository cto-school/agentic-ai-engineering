# Day 5 — Build a Mini AI Harness

> **Status:** Complete reference harness, operational website-maintenance capstone,
> instructor MCP server, offline fallbacks, and tests are included.

## Project

All required theory is embedded in the notebooks at the point where it is used. Notebook 08 is the independent tool-registry lab; Notebook 09 applies the harness to a recurring real-file workflow.

Build a small reusable platform that hosts multiple agent configurations, then use it to operate a Website Maintenance Agent with public/cached data, durable state, named guardrails, approval, persistent local changes and verification.

## Progression

```text
Compare two application-specific agents
-> find repeated project code
-> central model configuration
-> reusable runtime
-> tool registry
-> permissions and execution controls
-> events and checkpoints
-> MCP client connection
-> integrated harness
-> scheduled website-maintenance cycle
```

## Concepts introduced

Runtime, harness, registry, guardrail, policy, execution limit, event, checkpoint, protocol, MCP client, MCP server, automation trigger, change detection and tool discovery.

## Notebook sequence

1. `01_what_is_a_harness.ipynb` — identify repeated responsibilities.
2. `02_model_configuration_and_runtime.ipynb` — centralize execution.
3. `03_tool_registry.ipynb` — register and discover capabilities.
4. `04_permissions_and_limits.ipynb` — govern execution in code.
5. `05_events_logs_and_checkpoints.ipynb` — record and resume work.
6. `06_mcp_client.ipynb` — discover and use capabilities from an instructor-provided server.
7. `07_project_mini_harness.ipynb` — host research and task agent configurations.
8. `08_exercise_tool_registry.ipynb` — independently implement capability-aware discovery and dispatch.
9. `09_project_website_maintenance_agent.ipynb` — run the end-to-end operational capstone.

## Required environment

- The course core dependencies
- MCP Python SDK
- Instructor-provided local MCP server
- Local structured log storage

Writing an MCP server, FastAPI, and Docker are optional extensions rather than core lab requirements.

The ordinary-Python harness and fake MCP client run without optional packages. For
the guided real-MCP lab, install the instructor-pinned stable `mcp[cli]` version. The
SDK is evolving, so the course environment—not an unbounded latest install—defines
the classroom version.

## Run the reference project

```powershell
py run_project.py
py -m pytest tests -q
```

Use `python` instead of `py` where that is the configured launcher.

## Minimum harness responsibilities

- Load model configuration.
- Send model messages and optional tool schemas.
- Register tools with input schemas and risk levels.
- Validate requested tool arguments.
- Allow, deny, or request approval according to application policy.
- Stop after a configured maximum number of steps.
- Record model, tool, approval, failure, and completion events.
- Expose a small memory interface.
- Discover and call one local MCP tool.
- Load at least two agent configurations without rewriting the runtime.

## Core principle

Tool discovery is not authorization. A capability being visible through MCP does not automatically make it safe or permitted to call.

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
- [x] Policy enforcement is performed by Python, not delegated to the model.
- [x] Runs terminate with completed, failed, approval, or step-limit status.
- [x] Events explain the sequence of execution.
- [x] One local MCP capability can be discovered and invoked, with an offline fallback.
- [x] The same runtime hosts a research agent and a safe task agent configuration.
- [x] The student can explain the difference between an agent, framework, protocol, runtime, and harness.

## Optional extensions

- Expose the harness through FastAPI.
- Package the service with Docker.
- Write a trivial two-tool MCP server.
- Add a second hosted model configuration.
- Export traces to LangSmith or OpenTelemetry.
