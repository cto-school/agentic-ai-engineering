# Day 1 diagram sources

## D01 — Basic LLM application

```mermaid
flowchart LR
    U["User"] --> A["Host application"]
    A -->|"messages"| M["Model"]
    M -->|"generated response"| A
    A --> U
```

Text alternative: the host sends user messages to the model and returns the model response.

## D02 — Structured output and validation

```mermaid
flowchart LR
    P["Prompt + schema"] --> M["Model"] --> J["Candidate JSON"]
    J --> V{"Schema valid?"}
    V -->|"yes"| D["Typed application data"]
    V -->|"no"| E["Controlled error or retry"]
```

## D03 — Tool-calling sequence

```mermaid
sequenceDiagram
    participant H as Host
    participant M as Model
    participant T as Python tool
    H->>M: Messages + tool schemas
    M-->>H: Tool name + arguments
    H->>H: Validate request
    H->>T: Execute function
    T-->>H: Tool result
    H->>M: Append tool result
    M-->>H: Final answer
```

## D04 — Manual bounded agent loop

```mermaid
flowchart TD
    S["Start with messages"] --> C["Call model"]
    C --> Q{"Final answer?"}
    Q -->|"yes"| X["Complete"]
    Q -->|"tool request"| V["Validate and execute tool"]
    V --> L{"Step limit reached?"}
    L -->|"no"| C
    L -->|"yes"| F["Stop safely"]
```

## D05 — Small LangGraph state flow

```mermaid
flowchart LR
    START --> MODEL["Model node"]
    MODEL --> R{"Route from state"}
    R -->|"tool call"| TOOL["Tool node"] --> MODEL
    R -->|"final"| END
```
