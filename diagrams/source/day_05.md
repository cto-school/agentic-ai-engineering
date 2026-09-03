# Day 5 diagram sources

## D16 — Reusable two-agent harness

```mermaid
flowchart TB
    RCFG["Research agent config"] --> H["Shared harness runtime"]
    TCFG["Safe task agent config"] --> H
    H --> P["Model provider"]
    H --> REG["Tool registry + schemas"]
    H --> POL["Policy + approval"]
    H --> STATE["Memory + checkpoints"]
    H --> EVT["Events + evaluation"]
```

## D17 — MCP client consuming an instructor server

```mermaid
sequenceDiagram
    participant H as Harness MCP client
    participant S as Instructor MCP server
    H->>S: Initialize session
    H->>S: List tools
    S-->>H: Names + descriptions + schemas
    H->>H: Classify risk and apply local policy
    H->>S: Call permitted tool with validated arguments
    S-->>H: Structured result or error
    H->>H: Validate output and record event
```

## D18 — Complete course layer map

```mermaid
flowchart LR
    MODEL["Model"] --> TOOL["Tool"] --> AGENT["Agent loop"]
    KNOW["Knowledge / RAG"] --> AGENT
    MEM["Memory"] --> AGENT
    AGENT --> SAFE["Safety / approval"]
    SAFE --> OBS["Observability / evaluation"]
    OBS --> MULTI["Bounded multi-agent workflow"]
    MULTI --> HARNESS["Reusable AI harness"]
    MCP["MCP-discovered capabilities"] --> HARNESS
```

Text alternative: the course grows from model calls to reusable infrastructure; safety and observability govern execution rather than appearing as optional add-ons.

## D19 — Recurring website-maintenance cycle

```mermaid
flowchart LR
    S["Daily scheduler"] --> F["Public or cached update source"]
    F --> D["Change detector + durable state"]
    D --> M["Model or deterministic proposal"]
    M --> G["Input, context, output and tool guardrails"]
    G --> A["Human approval"]
    A --> W["Write allowed local website file"]
    W --> V["Deterministic verification"]
    V --> E["Events + processed-item checkpoint"]
    E --> S
    G -->|"blocked"| E
    A -->|"rejected"| E
```

Text alternative: scheduling only triggers a bounded check. External content is validated, the proposal is guarded, a human approves the exact patch, and only then does a verified persistent change occur.
