# n8n module diagram sources

## D53 — Anatomy of an n8n workflow

```mermaid
flowchart LR
    T["Trigger: chat, form, schedule, webhook"] -->|"items"| N1["Node: does one thing"]
    N1 -->|"items"| N2["IF node"]
    N2 -->|"true"| A["Gmail node"]
    N2 -->|"false"| B["Google Sheets node"]
    A --> X["Execution recorded"]
    B --> X
```

Text alternative: a trigger starts the workflow and emits items; each node receives items, does one thing and passes them on; an IF node splits the path; every run is recorded as an execution with the data at each node.

## D54 — The AI Agent node and its sub-nodes

```mermaid
flowchart TD
    U["User message"] --> AG["AI Agent node: the tool loop"]
    AG --> O["Final answer"]
    CM["Chat Model: Gemini"] -->|"model socket"| AG
    ME["Simple Memory: session id"] -->|"memory socket"| AG
    T1["Tool: Wikipedia"] -->|"tool socket"| AG
    T2["Tool: HTTP Request"] -->|"tool socket"| AG
    OP["Structured Output Parser"] -->|"output parser socket"| AG
```

Text alternative: the AI Agent node receives the user message and emits the final answer; a chat model, a memory, any number of tools and an optional output parser plug into sockets underneath it and are used by the loop inside the node.

## D55 — Ticket triage: structured output then deterministic routing

```mermaid
flowchart LR
    F["Form submission"] --> AG["AI Agent + Structured Output Parser"]
    AG -->|"category, urgency, summary, reply_draft"| I{"urgency = high?"}
    I -->|"yes"| G["Gmail: alert"]
    I -->|"no"| S["Google Sheets: append row"]
```

Text alternative: a form submission goes to an agent whose output parser guarantees a JSON object with fixed fields; an IF node reads the urgency enum and routes urgent tickets to an email alert and the rest to a spreadsheet row.

## D56 — Supervisor delegating to specialist workflows

```mermaid
flowchart LR
    U["Chat message"] --> SV["Supervisor agent"]
    SV -->|"Call n8n Workflow Tool"| R["Researcher workflow: agent + Wikipedia + Calculator"]
    SV -->|"Call n8n Workflow Tool"| W["Writer workflow: agent, no tools"]
    R -->|"facts"| SV
    W -->|"message text"| SV
    SV --> O["Reply to user"]
```

Text alternative: the supervisor agent treats two other workflows as tools; each starts with a When Executed by Another Workflow trigger, runs its own agent, and returns its output to the supervisor, which composes the reply.
