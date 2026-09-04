# LangChain track diagram sources

## D20 — A LangChain chat model call

```mermaid
flowchart LR
    U["User"] --> A["Application"]
    A -->|"list of messages"| M["Chat model (ChatOpenAI via OpenRouter)"]
    M -->|"AIMessage + usage metadata"| A
    A --> U
```

Text alternative: the application sends a typed message list to the chat model and receives one AIMessage; nothing persists between calls.

## D21 — Tool calling and the hand-written agent loop

```mermaid
flowchart TD
    S["Messages + tool schemas"] --> M["Model"]
    M --> Q{"Reply contains tool_calls?"}
    Q -->|"yes"| T["Your code validates and executes the tool"]
    T -->|"ToolMessage appended"| M
    Q -->|"no"| E["Final answer"]
```

Text alternative: the model requests a tool by name and arguments; the application executes it and appends the ToolMessage; the loop repeats until the model answers or the step limit is hit.

## D22 — The create_agent graph

```mermaid
flowchart LR
    START --> MODEL["model node"]
    MODEL --> R{"route"}
    R -->|"tool calls"| TOOLS["tools node"]
    TOOLS --> MODEL
    R -->|"final answer"| END
```

Text alternative: create_agent compiles the agent loop as a LangGraph graph with a model node, a tools node and a conditional edge between them.

## D23 — Structured output as a tool call

```mermaid
flowchart LR
    P["Prompt + Pydantic schema"] --> M["Model"]
    M --> J["Schema tool call"]
    J --> V{"Validates?"}
    V -->|"yes"| D["structured_response object"]
    V -->|"no"| R["Error returned to the model, retry"]
```

Text alternative: with ToolStrategy the schema becomes a tool; the model's call is validated by Pydantic and exposed as structured_response, or returned as an error for another attempt.

## D24 — Memory layers around the agent

```mermaid
flowchart LR
    U["User turn"] --> C["Checkpointer loads the thread"]
    C --> A["Agent run"]
    A -->|"ToolRuntime"| S["Store: namespace per user"]
    A --> W["Checkpointer saves the new checkpoint"]
```

Text alternative: short-term memory is the thread checkpoint loaded and saved around each run; long-term memory is a store keyed by user that tools reach through ToolRuntime.

## D25 — Retrieval and RAG

```mermaid
flowchart LR
    D["Documents"] --> SP["Text splitter"]
    SP --> E["Embeddings"]
    E --> V["Vector store"]
    Q["Question"] --> RT["Retriever"]
    V --> RT
    RT -->|"relevant chunks"| M["Model or agent tool"]
    M --> A["Grounded answer"]
```

Text alternative: documents are split, embedded and stored once; at query time the retriever returns the nearest chunks, which are given to the model directly (2-step RAG) or through a search tool (agentic RAG).

## D26 — Middleware around the model and the tools

```mermaid
flowchart TD
    I["Agent state"] --> BM["before_model"]
    BM --> WM["wrap_model_call: permissions, fallback, tracing"]
    WM --> M["Model"]
    M --> AM["after_model"]
    AM --> WT["wrap_tool_call: guard, retry, logging"]
    WT --> T["Tool"]
```

Text alternative: middleware hooks run before and around the model call and around each tool call, which is where logging, limits, retries, fallbacks and authorisation live.

## D27 — Human-in-the-loop approval

```mermaid
flowchart LR
    A["Agent"] -->|"tool call"| H{"interrupt_on policy"}
    H -->|"read tool"| T["Execute automatically"]
    H -->|"write tool"| P["Interrupt: human reviews"]
    P -->|"approve, edit or reject"| R["Resume from checkpoint"]
    R --> A
```

Text alternative: tools listed in the approval policy pause the run at a checkpoint; the human's decision resumes it, so the write happens only after approval or edit.

## D28 — An explicit LangGraph workflow

```mermaid
flowchart LR
    START --> C["classify"]
    C -->|"faq"| F["faq: policy search"]
    C -->|"billing"| B["billing: order lookup"]
    F --> D["draft"]
    B --> D
    D --> AP["approve (interrupt)"]
    AP --> S["send"]
    S --> END
```

Text alternative: a fixed support workflow as a graph: classify, branch to the right evidence node, draft, pause for approval, send.

## D29 — Supervisor with specialists as tools

```mermaid
flowchart LR
    U["User"] --> S["Supervisor agent"]
    S -->|"billing_agent(query)"| B["Billing specialist"]
    S -->|"policy_agent(query)"| P["Policy specialist"]
    B --> S
    P --> S
    S --> U
```

Text alternative: the supervisor sees each specialist as one tool, delegates self-contained questions, and combines the replies.

## D30 — The production shape

```mermaid
flowchart TD
    U["User"] --> API["API / frontend (streaming)"]
    API --> AUTH["Auth / identity (context)"]
    AUTH --> MW["Middleware: permissions, guardrails, limits, approval, tracing"]
    MW --> AG["Agent or LangGraph workflow"]
    AG --> T["Tools, retrieval, sub-agents"]
    AG --> PS["Persistence: checkpointer + store"]
    AG --> OB["Observability: traces and cost"]
```

Text alternative: user requests pass through the API, identity and a middleware stack before reaching the agent, which uses tools, retrieval and sub-agents while persistence and observability sit alongside.
