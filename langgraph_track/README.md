# LangGraph Track — Building CampusAI

**Project:** CampusAI — a university helpdesk assistant grown fifteen times, from a three-node graph with no model in it to a persisted, permissioned, approval-gated, retrieval-backed, parallel, MCP-connected, supervised and evaluated system.

This track teaches **LangGraph from scratch** and, through it, how modern AI agents are built. It is fully self-contained: it assumes basic Python and nothing else from the course. Every graph is built by hand so that state, reducers, edges, checkpoints, stores, interrupts, retries, fan-out, subgraphs, MCP clients and supervisors are all visible, and the concepts every agentic system shares (context, tools, memory, knowledge, guardrails, observability) arrive one at a time.

## The notebook

Students open **one** Google Colab notebook, `langgraph_complete.ipynb`, and run it top to bottom.
It is self-contained: the setup cell installs LangGraph and LangChain (whose chat models and `@tool`
decorator LangGraph reuses), reads the `OPENROUTER_API_KEY` Colab secret (or asks once), and all data
is created inside the notebook. Without a key it runs on a built-in mock chat model (a real
`BaseChatModel` subclass with rule-based tool calls). Every code cell tags where each call comes from:
`# LangGraph`, `# LangChain`, `# Pydantic` or `# ours`.

There are no exercises or checkpoints: each section is concise theory, an architecture sketch,
runnable commented code, and a three-line recap. The opening cells give a map of the eight parts
of an agent and introduce the CampusAI scenario.

| Section | Lesson file (derived) | CampusAI gains | Graph idea | Agentic concept |
|---|---|---|---|---|
| G1 | `01_graphs_before_agents.ipynb` | keyword triage with no model | state, nodes, edges, conditional edges, loops | workflow vs agent |
| G2 | `02_model_as_a_node.ipynb` | a chatbot node | reducers, `add_messages`, system prompt | the context is the message list |
| G3 | `03_tools_and_the_agent_loop.ipynb` | tools and the ReAct loop, by hand then with `ToolNode`; validated tools | edge back to the model | tool design |
| G4 | `04_structured_output_and_routing.ipynb` | tickets and desks | `with_structured_output`, conditional routing, agent as subgraph | workflows that contain agents |
| G5 | `05_short_term_memory_and_context.ipynb` | remembers a conversation and keeps it short | checkpointer, thread ids, state history, `RemoveMessage` | short-term memory, context management |
| G6 | `06_long_term_memory.ipynb` | remembers the person across conversations | store, `Runtime` context, `get_runtime` in tools | long-term memory, identity |
| G7 | `07_knowledge_and_retrieval.ipynb` | knows the handbook, FAQ and catalogue | embeddings and cosine search in numpy, retrieval node and retrieval tool | RAG, grounding |
| G8 | `08_approval_permissions_and_injection.ipynb` | acts safely | role-filtered tools, guard node, `interrupt()`, `Command(resume)`, `interrupt_before` | human-in-the-loop, permissions, prompt injection |
| G9 | `09_reliability_and_limits.ipynb` | survives a flaky tool and a looping model | `RetryPolicy` with `retry_on`, `handle_tool_errors`, `recursion_limit` | reliability, bounded autonomy |
| G10 | `10_parallel_work.ipynb` | checks eligibility three ways at once | fan-out and fan-in, `operator.add` reducer, `Send` | parallelism, latency |
| G11 | `11_mcp_tools_from_servers.ipynb` | uses tools served by another process and by a public server | `FastMCP` server over HTTP, `MultiServerMCPClient`, `ainvoke`, DeepWiki with a timeout | tool ecosystems, trust boundaries |
| G12 | `12_multi_agent_supervisor.ipynb` | a supervisor delegating to two specialists, and a handoff between them | worker subgraphs, `Command(goto=...)`, `destinations`, a transfer tool | multi-agent orchestration |
| G13 | `13_streaming_tracing_and_evaluation.ipynb` | shows progress and is measured | stream modes, a trace from the updates stream, an evaluation harness, optional LangSmith tracing | observability, evaluation |
| G14 | `14_scheduled_runs.ipynb` | runs on a schedule without a user | one thread per tick, queued approvals, an idempotency ledger | triggers, idempotency |
| G15 | `15_the_full_system.ipynb` | everything assembled | one graph with profile loading, context management, triage, four desks, persistence, store, MCP tools | the production shape |

The files under `notebooks/` are generated from the track notebook by `split_day_notebooks.py`
for the course portal. Edit the track notebook, then re-run the split; do not edit the lesson files.

## Live versus mock

| Mode | When | What differs |
|---|---|---|
| Mock | no key found | `make_model()` returns `MockChatModel`; tool calls and replies follow fixed rules; every graph runs unchanged |
| Live | key found | `make_model()` returns `ChatOpenAI` pointed at OpenRouter with `reasoning.effort=low`, `temperature=0`, `max_tokens=900` |

Section G7 downloads the `all-MiniLM-L6-v2` embedding model (about 90 MB) and falls back to a keyword embedding if it cannot be loaded. Section G11 writes a small MCP server file, starts it as a background HTTP process, and also connects to DeepWiki's public MCP server (skipped with a message if unreachable). Section G13 traces one run in LangSmith only if a `LANGSMITH_API_KEY` secret is present.

## Versions

The notebook installs `langgraph>=1.0`, `langchain>=1.2`, `langchain-openai>=1.1`, and in later sections `sentence-transformers`, `mcp` and `langchain-mcp-adapters`. It was executed end to end with LangGraph 1.2.11, LangChain 1.4.0, mcp 1.29 and langchain-mcp-adapters 0.3 in mock mode. Version-specific details called out in the text: LangGraph's default retry predicate skips `OSError` subclasses (so `retry_on` must name transient errors), `ToolNode` converts only invalid-argument errors to messages unless `handle_tool_errors=True` is passed, and MCP tools are async-only, so graphs that contain them run with `ainvoke`.
