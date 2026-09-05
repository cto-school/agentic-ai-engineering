# Mem0 module diagram sources

## D65 — Where a memory layer sits beside the agent loop

```mermaid
flowchart LR
    U["User message"] --> A["Agent loop"]
    A -->|"search: latest message + user_id"| M["Memory layer: Mem0"]
    M -->|"relevant facts"| A
    A -->|"system prompt with facts"| L["Model"]
    L -->|"reply"| A
    A -->|"add: the turn + user_id"| M
    A --> R["Reply to user"]
```

Text alternative: the agent searches the memory layer with the latest message and the user id, places the returned facts in the system prompt, calls the model, returns the reply, and adds the turn to the memory layer so that later conversations can use it.

## D66 — What add does to a conversation

```mermaid
flowchart LR
    T["Messages of one turn"] --> C["Context lookup: what is already known"]
    C --> E["LLM fact extraction: third-person facts"]
    E --> D["Deduplicate and embed"]
    D --> N["Entity extraction"]
    N --> S["SQL: text, ids, metadata, history"]
    N --> V["Vector store: embeddings"]
    N --> G["Entity store: people, places, concepts"]
```

Text alternative: add looks up existing memories for the scope, extracts short third-person facts with a model, drops duplicates and embeds the rest, extracts entities, and writes the fact text to SQL, the embedding to the vector store and the entities to the entity store; storage is additive.

## D67 — Search fuses four signals

```mermaid
flowchart LR
    Q["Query + filters: user_id, agent_id, run_id"] --> F["Eligible memories"]
    F --> S1["Semantic similarity"]
    F --> S2["Keyword match"]
    F --> S3["Entity overlap"]
    F --> S4["Temporal intent"]
    S1 --> R["Fused score"]
    S2 --> R
    S3 --> R
    S4 --> R
    R -->|"top_k, threshold, optional rerank"| O["Ranked results"]
```

Text alternative: filters decide which memories are eligible, four signals score them, the scores fuse into one, and top_k, threshold and an optional reranker shape the returned list.

## D68 — Memory inside a LangGraph node

```mermaid
flowchart LR
    ST["State: messages + mem0_user_id"] --> N["chatbot node"]
    N -->|"1 search latest message"| M["Mem0"]
    M -->|"facts"| N
    N -->|"2 system prompt + messages"| L["Model"]
    L -->|"3 reply"| N
    N -->|"4 add user + assistant turn"| M
    N -->|"messages updated"| ST
```

Text alternative: the node reads the messages and the user id from the state, searches Mem0, builds the system prompt with the facts, calls the model, adds the turn to Mem0, and returns the reply into the state; the checkpointer still owns the conversation itself.

## D69 — Three ways to run Mem0

```mermaid
flowchart TD
    A["Your agent"] -->|"API key"| P["Mem0 Platform: hosted API + dashboard"]
    A -->|"in-process"| L["Open-source library: Ollama model + embedder, Qdrant on disk, SQLite history"]
    A -->|"X-API-Key"| S["Self-hosted server: REST on 8888, dashboard on 3000, Postgres + pgvector"]
    T["Coding assistant"] -->|"MCP tools"| P
```

Text alternative: the same agent can use the hosted Platform with an API key, the open-source library inside its own process with Ollama and a local vector store, or a self-hosted server stack with its own REST API and dashboard; coding assistants reach the Platform through MCP tools.
