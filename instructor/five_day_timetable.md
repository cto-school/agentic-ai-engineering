# Five-Day Classroom Timetable

This is a teaching plan, not a race through every notebook. Each day uses the same rhythm: explain a small idea, demonstrate it, let students build it, deliberately break it, and then improve it.

Times are adjustable. The essential distinction is between **core**, **optional demonstration**, and **fallback** work.

## Day 1 — Model, Tool, and Agent

| Block | Classroom activity | Status |
|---|---|---|
| 09:30–10:15 | Course mental model; run the mock path; configure the issued OpenRouter key | Core |
| 10:15–11:00 | First model call; inspect messages, response, latency, and usage | Core |
| 11:15–12:15 | Structured output and validation; break malformed outputs | Core |
| 13:00–14:00 | Tool schemas, dispatch, and tool results | Core |
| 14:00–15:00 | Complete and test the bounded manual agent loop | Core |
| 15:15–16:15 | Assemble Project 1; compare workflow and agent; recap | Core |

Instructor fallback: if the provider is unavailable, use mock mode for every exercise and show one previously captured live trace.

## Day 2 — Knowledge, Retrieval, and State

| Block | Classroom activity | Status |
|---|---|---|
| 09:30–10:15 | Documents, chunks, metadata, and keyword retrieval | Core |
| 10:15–11:00 | Embeddings and semantic retrieval | Core |
| 11:15–12:15 | Assemble a RAG context and generate a grounded answer | Core |
| 13:00–14:00 | Citations, abstention, and context limits | Core |
| 14:00–15:00 | Diagnose retrieval-versus-generation failures with the golden set | Core |
| 15:15–16:15 | Retrieval as a tool; visible state; assemble Project 2 | Core |

Instructor fallback: use the deterministic embedder if the local embedding model cannot be downloaded. Treat its poorer retrieval as a diagnosis exercise.

## Day 3 — Memory, Planning, and Safety

| Block | Classroom activity | Status |
|---|---|---|
| 09:30–10:15 | Context versus state versus memory; inspect conversation growth | Core |
| 10:15–11:00 | Implement bounded-history compaction | Core |
| 11:15–12:00 | Durable preferences and memory lifecycle | Core |
| 12:00–12:20 | Mem0 hosted-product demonstration using synthetic data | Optional demo |
| 13:00–14:00 | Plans, proposed actions, and named input/context/output/tool guardrails | Core |
| 14:00–15:00 | Policy, human approval, denial, idempotency, and audit events | Core |
| 15:15–15:35 | LangSmith trace demonstration using synthetic data | Optional demo |
| 15:35–16:15 | Assemble and challenge Project 3 | Core |

Instructor fallback: skip both hosted demonstrations. The local event log and local memory implementation teach the required concepts.

## Day 4 — Workflows and Multi-Agent Systems

| Block | Classroom activity | Status |
|---|---|---|
| 09:30–10:15 | When one agent is enough; establish a single-agent baseline | Core |
| 10:15–11:00 | Specialists and explicit task contracts | Core |
| 11:15–12:15 | Sequential and parallel orchestration | Core |
| 13:00–14:00 | Supervisor routing and deterministic result merging | Core |
| 14:00–15:00 | Trace both systems; handle partial failure and duplicates | Core |
| 15:15–16:15 | Evaluate quality, latency, calls, and cost; justify the architecture | Core |

Instructor fallback: use mock specialists for a fully deterministic run, then show how nondeterminism changes evaluation rather than the architecture.

## Day 5 — AI Harness

| Block | Classroom activity | Status |
|---|---|---|
| 09:30–10:15 | Extract reusable runtime and provider configuration | Core |
| 10:15–11:00 | Tool registry and capability-based permissions | Core |
| 11:15–12:15 | Events, traces, checkpoints, and resume | Core |
| 13:00–14:00 | Timeouts, retries, idempotency, and budget enforcement | Core |
| 14:00–14:35 | MCP concepts and bounded real-server demonstration | Core concept; demo may be skipped |
| 14:35–15:30 | Website Maintenance Agent: cached/public update, memory, proposal, guardrails, approval and real local file update | Core |
| 15:30–16:15 | Injection challenge, optional LLM judge, scheduler boundary and course synthesis | Core |

Instructor fallback: use the supplied mock MCP client, cached update feed and captured live traces. Do not spend classroom time debugging external servers.

## Teaching controls

- Keep at least 15 minutes of unallocated recovery time per day.
- Stop optional demonstrations when they threaten the core build.
- Pair students temporarily during installation failures; do not let setup consume the lesson.
- Require a prediction before each deliberate failure and a diagnosis afterward.
- Use the same questions repeatedly: What entered this layer? What left it? What evidence do we have? What should happen when it fails?
