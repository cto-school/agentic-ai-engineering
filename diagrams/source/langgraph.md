# LangGraph track diagram sources

## D31 — State, nodes and edges

```mermaid
flowchart LR
    START --> A["add_ten (node)"]
    A -->|"state update"| B["double (node)"]
    B -->|"state update"| C["subtract_one (node)"]
    C --> END
```

Text alternative: a state dictionary enters at START, each node returns a partial update that is merged into it, and edges fix the order until END.

## D32 — Conditional edge and loop

```mermaid
flowchart LR
    START --> N["add_ten"]
    N --> Q{"value < 50?"}
    Q -->|"yes"| N
    Q -->|"no"| END
```

Text alternative: a routing function reads the state after a node and returns the name of the next node; pointing it back at the same node makes a loop that ends when the condition fails.

## D33 — The model as a node with a messages reducer

```mermaid
flowchart LR
    U["User message"] --> S["state.messages (add_messages reducer)"]
    S --> M["chatbot node: model.invoke(system + messages)"]
    M -->|"AIMessage appended"| S
    S --> END
```

Text alternative: the chatbot node reads the message list from state, calls the model, and returns the reply; the add_messages reducer appends it instead of replacing the list.

## D34 — The agent loop as a graph

```mermaid
flowchart LR
    START --> AG["agent node (model + bound tools)"]
    AG --> R{"tool calls?"}
    R -->|"yes"| T["tools node (runs the requests)"]
    T -->|"ToolMessages"| AG
    R -->|"no"| END
```

Text alternative: the agent node asks the model; if the reply requests tools the tools node executes them and control returns to the agent; otherwise the run ends.

## D35 — Structured output feeding a router

```mermaid
flowchart LR
    Q["User message"] --> T["triage: with_structured_output(Ticket)"]
    T -->|"category = faq"| F["faq desk"]
    T -->|"category = records"| RG["records desk: agent subgraph"]
    T -->|"category = smalltalk"| SM["smalltalk"]
    F --> END
    RG --> END
    SM --> END
```

Text alternative: the triage node makes the model fill in a validated Ticket object; a conditional edge reads its category and sends the message to the handbook desk, the records desk (a compiled agent graph used as a node) or a small-talk reply.

## D36 — Checkpointer, threads and context management

```mermaid
flowchart LR
    I["invoke(input, thread_id)"] --> L["load latest checkpoint of the thread"]
    L --> MC["manage_context: summarise old turns, RemoveMessage"]
    MC --> G["agent nodes"]
    G -->|"after every node"| C["save checkpoint"]
    C --> H["get_state / get_state_history"]
```

Text alternative: with a checkpointer each invocation loads the thread's saved state, a context-management node keeps the message list short, the nodes run, and a checkpoint is saved after each of them.

## D37 — Long-term memory through the store and runtime context

```mermaid
flowchart LR
    APP["application: context=Context(user_id, role)"] --> LP["load_profile node: runtime.store.get"]
    LP -->|"profile into state"| AG["agent node: facts in the system prompt"]
    AG -->|"remember_about_me tool"| ST["store: namespace (profiles, user_id)"]
    ST --> LP
```

Text alternative: the application passes the user identity as runtime context; a profile-loading node reads that user's facts from the store into the state, the agent puts them in its prompt, and a remember tool writes new facts back under the same namespace.

## D38 — Retrieval by meaning

```mermaid
flowchart LR
    D["documents"] --> CH["chunks"]
    CH --> E["embedding model"]
    E --> IX["index of unit vectors"]
    Q["question"] --> QE["embed"]
    QE --> CS["cosine similarity: top k"]
    IX --> CS
    CS -->|"excerpts with sources"| M["model with grounding instruction"]
    M --> A["grounded answer"]
```

Text alternative: documents are embedded once into an index; a question is embedded, the nearest chunks are found by cosine similarity, and the model answers only from those excerpts, either inside a fixed faq node or through a search tool the agent calls.

## D39 — Permissions, guard and approval on write tools

```mermaid
flowchart LR
    AG["agent (tools filtered by role)"] --> Q{"read or write tool?"}
    Q -->|"read"| T["tools"]
    Q -->|"write"| GD["guard: role re-check"]
    GD -->|"allowed"| AP["approval: interrupt()"]
    GD -->|"blocked"| AG
    AP -->|"Command(resume=True)"| T
    AP -->|"Command(resume=False)"| AG
    T --> AG
```

Text alternative: the model only sees the tools its caller's role allows; write requests pass a guard node that re-checks the role and an approval node that pauses with interrupt; a rejection at either point returns rejection messages to the agent instead of running the tool.

## D40 — Retries, error messages and the recursion limit

```mermaid
flowchart LR
    T["tools node"] -->|"tool raises"| RP{"RetryPolicy: retry_on matches?"}
    RP -->|"yes, attempts left"| T
    RP -->|"no"| E["handle_tool_errors: error ToolMessage"]
    E --> AG["agent reads the error"]
    AG --> RL{"recursion_limit reached?"}
    RL -->|"yes"| X["GraphRecursionError: stop safely"]
```

Text alternative: a node retry policy re-runs the tools node for transient errors, remaining errors become messages the model can read, and the recursion limit stops any run that keeps looping.

## D41 — Fan-out, reducer and Send

```mermaid
flowchart LR
    START --> A["attendance_check"]
    START --> C["credit_check"]
    START --> P["prerequisite_check"]
    A -->|"findings (operator.add)"| V["verdict"]
    C -->|"findings (operator.add)"| V
    P -->|"findings (operator.add)"| V
    V --> END
```

Text alternative: three nodes run at the same time from START and each appends to the findings key through a reducer; the verdict node runs once all three have finished, and Send creates such branches dynamically.

## D42 — Tools served by an MCP server

```mermaid
flowchart LR
    AG["agent node"] -->|"tool call"| T["ToolNode (local + MCP tools)"]
    T -->|"local"| L["Python function in the notebook"]
    T -->|"MCP client, stdio"| S["library server process: library_hours, search_library"]
    S -->|"result"| T
    L -->|"result"| T
    T -->|"ToolMessages"| AG
```

Text alternative: the client lists a server's tools and hands them to the same tools node as local functions; a call to an MCP tool travels to the server process and its result comes back as an ordinary tool message.

## D43 — Supervisor with worker subgraphs

```mermaid
flowchart LR
    START --> S["supervisor (structured decision, Command goto)"]
    S -->|"records_worker"| R["records worker: agent subgraph"]
    S -->|"handbook_worker"| H["handbook worker: agent subgraph"]
    R -->|"named report"| S
    H -->|"named report"| S
    S -->|"FINISH"| F["final answer"]
    F --> END
```

Text alternative: the supervisor node chooses the next worker with a structured decision and Command routing; each worker runs its own agent subgraph and reports back until the supervisor finishes.

## D44 — The assembled CampusAI

```mermaid
flowchart LR
    START --> LP["load_profile"]
    LP --> MC["manage_context"]
    MC --> T["triage"]
    T -->|"faq"| F["faq desk: retrieval, grounded"]
    T -->|"records"| R["records desk: role filter, guard, approval, retries, local + MCP tools"]
    T -->|"eligibility"| E["eligibility desk: parallel checks"]
    T -->|"smalltalk"| S["smalltalk"]
    F --> END
    R --> END
    E --> END
    S --> END
```

Text alternative: every turn loads the user's profile and trims the context, then triage routes it to a grounded faq desk, an approval-gated records agent with local and MCP tools, a parallel eligibility check or a small-talk reply, all persisted on one thread with a store for people.

## D45 — Scheduled runs with queued approvals

```mermaid
flowchart LR
    CRON["scheduler tick (tick_id)"] --> LEDGER{"tick already processed?"}
    LEDGER -->|"yes"| SKIP["skip: idempotent"]
    LEDGER -->|"no"| FIND["find_at_risk (deterministic)"]
    FIND --> DRAFT["draft_emails (model)"]
    DRAFT --> AP["approval: interrupt, waits in the checkpoint"]
    AP -->|"staff resumes later"| SEND["send"]
    SEND --> END
```

Text alternative: a scheduler tick with its own id and thread is skipped if already processed; otherwise the watcher reads, drafts with the model, and pauses at an approval that waits in the checkpoint until a staff member resumes it, at which point the emails are sent.
