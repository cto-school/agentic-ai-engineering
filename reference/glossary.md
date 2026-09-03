# Glossary

Terms are written first for a beginner, then more precisely. This document should grow alongside the notebooks.

| Term | Beginner explanation | More precise meaning | First used |
|---|---|---|---|
| Model | The AI component that generates a response | A trained probabilistic system that maps input context to generated output | Day 1 |
| Prompt | Instructions or information sent to a model | Input content placed into one or more messages in the model context | Day 1 |
| Message | One item in a model conversation | Structured content associated with a role such as system, user, assistant, or tool | Day 1 |
| Context | Information currently available to the model | The messages, instructions, tool definitions, and retrieved data supplied for a model call | Day 1 |
| Structured output | A response with a predictable shape | Model output constrained or validated against a schema | Day 1 |
| Schema | A description of expected data | A machine-readable contract specifying fields, types, and constraints | Day 1 |
| Tool | A capability the model can request | A schema-described operation selected by a model and executed by the host application | Day 1 |
| Agent loop | A repeated model-and-tool process | A bounded execution cycle in which the model selects actions, observes results, and decides whether to continue | Day 1 |
| Agent | A system that can choose actions toward a goal | A model-driven application combining instructions, state, tools, and an execution loop | Day 1 |
| State | Information carried while a task is running | Application-owned data passed and updated across workflow steps | Day 1–2 |
| Chunk | A smaller piece of a document | A retrieval unit created during document preprocessing | Day 2 |
| Embedding | Numbers representing approximate meaning | A dense vector used to compare semantic similarity | Day 2 |
| Vector index | A searchable collection of embeddings | A data structure or database that retrieves vectors near a query vector | Day 2 |
| Similarity score | A number estimating how closely two representations match | A retrieval ranking signal such as cosine similarity; it is not proof of relevance | Day 2 |
| Retrieval | Finding useful information for a question | Selecting relevant records or chunks from an external knowledge source | Day 2 |
| RAG | Letting the model answer using retrieved information | Retrieval-Augmented Generation: retrieve evidence, place it in context, and generate a grounded response | Day 2 |
| Grounding | Basing an answer on supplied evidence | Constraining generation to relevant, attributable source content | Day 2 |
| Memory | Information deliberately saved for later | Persisted information selected and retrieved across interactions or runs | Day 3 |
| Short-term memory | Recent information available during a session | Conversation history or running state carried into later steps | Day 3 |
| Persistent memory | Selected information retained across sessions | User-scoped records stored outside the model with lifecycle and provenance controls | Day 3 |
| Provenance | Where a piece of information came from | Metadata describing a record's source, time, and derivation | Day 3 |
| Context compaction | Keeping active conversation small enough to use | Trimming or summarizing older messages while preserving information needed for later turns | Day 3 |
| Guardrail | A check intended to keep behavior within rules | An input, output, policy, or execution control that detects or prevents disallowed behavior | Day 3 |
| Policy | Rules that decide what execution is permitted | Application-owned logic that allows, denies, or pauses a requested action | Day 3 |
| Side effect | A change outside a function's returned value | A write, message, deletion, transaction, or other observable change to state or the external world | Day 3 |
| Approval | Explicit permission to continue a pending action | A fresh human decision over displayed tool arguments before a consequential side effect | Day 3 |
| Interrupt | A deliberate pause in workflow execution | A checkpointed suspension that awaits external input before resuming | Day 3 |
| Human-in-the-loop | Asking a person before continuing | A workflow interrupt requiring human input or approval before execution resumes | Day 3 |
| Workflow | A defined sequence of steps | Deterministic or conditional orchestration of functions, models, and tools | Day 4 |
| Handoff | Passing work to another role | Transfer of a structured task or artifact between agent nodes | Day 4 |
| Fan-out/fan-in | Split independent work and combine it later | Parallel dispatch of bounded subtasks followed by deterministic or model-assisted aggregation | Day 4 |
| Supervisor | A component that decides who works next | An orchestration node that routes tasks, requests revision, or terminates execution | Day 4 |
| Observability | Seeing what happened inside a run | Logs, traces, events, metrics, and artifacts used to inspect system behavior | Day 4 |
| Evaluation | Checking whether the system works | Repeatable measurement of outputs, decisions, retrieval, safety, or task success | Day 4 |
| Golden set | Supplied examples with expected outcomes | A versioned evaluation dataset used to compare actual and expected behavior | Days 2–4 |
| Defect recall | How many known defects were found | The fraction of golden defects matched by system findings | Day 4 |
| False positive | A reported problem not present in the answer key | A finding predicted by the system that does not match a known relevant defect | Day 4 |
| Trace | A connected history of work inside one run | Ordered spans or events containing inputs, outputs, timing, errors, and metadata | Days 3–5 |
| Runtime | The code that executes an agent | Infrastructure that manages model calls, tools, state, policies, errors, and lifecycle | Day 5 |
| Provider adapter | A common interface over a model service | Code translating harness requests and responses to a provider-specific API | Day 5 |
| Tool discovery | Learning which capabilities are available | Obtaining tool names, descriptions, and schemas from a registry or protocol endpoint | Day 5 |
| Tool registry | A catalog of available tools | A component that stores tool metadata, schemas, executors, and policy information | Day 5 |
| Event | A structured fact recorded during execution | An append-only observation such as model requested, policy decided, or tool completed | Day 5 |
| Checkpoint | Saved continuation state | State persisted so a paused or interrupted run can resume consistently | Day 5 |
| Harness | The environment surrounding an agent | A reusable runtime combining model access, tools, state, memory, policy, approval, and observability | Day 5 |
| MCP | A common way to expose tools and context | Model Context Protocol, a protocol through which clients discover and use server capabilities | Day 5 |
| MCP client | The application side of an MCP connection | A component that initializes a session, discovers capabilities, and makes protocol calls | Day 5 |
| MCP server | A process that publishes MCP capabilities | A protocol endpoint exposing tools, resources, or prompts through a supported transport | Day 5 |

## Commonly confused concepts

### Model versus agent

A model generates output. An agent is an application that uses a model to choose and perform actions within controls.

### Context versus state versus memory

- Context is what the model can see in one call.
- State is what the application carries during execution.
- Memory is selected information persisted for later interactions.

Context compaction changes what remains in active context; it is not automatically long-term memory.

### Knowledge versus memory

Knowledge usually comes from an external corpus such as manuals. Memory usually records information derived from interactions, preferences, and prior activity.

### Workflow versus agent

A workflow follows application-defined steps. An agent delegates some decision about the next action to a model. A useful system may combine both.

### Tool versus MCP server

A tool is one callable capability. An MCP server can expose one or more tools and other capabilities through a common protocol.

### Guardrail versus permission

A guardrail detects or shapes behavior. A permission check authoritatively allows, denies, or pauses an action. Asking a model whether an action is permitted is not enforcement.

### Tool discovery versus authorization

Discovery describes what a registry or MCP server advertises. Authorization is the
local decision that a particular agent and user may invoke it. Discovery must never
silently grant permission.

### Log versus trace versus checkpoint

- A log is a recorded message or event.
- A trace connects events or spans belonging to one run.
- A checkpoint stores continuation state so execution can resume.

Deleting a checkpoint does not necessarily delete audit events, and deleting a trace
does not necessarily delete application memory.
