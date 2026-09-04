# LangChain Track — Building OpsPilot

**Project:** OpsPilot — an operations assistant for a fictional company, grown fourteen times from a plain model call to a guarded, approval-gated, multi-agent system.

This track is separate from the five course days. The days teach agentic AI from first principles in plain Python; this track teaches the same ideas through **LangChain 1.x** (`create_agent`, tools, middleware, structured output) and **LangGraph** (persistence, interrupts, explicit workflows). It can be studied after Day 1, or on its own by students who already know what a model call and a tool are.

## The notebook

Students open **one** Google Colab notebook, `langchain_complete.ipynb`, and run it top to bottom.
It is self-contained: the setup cell installs LangChain, reads the `OPENROUTER_API_KEY` Colab secret
(or asks once), and all data is created inside the notebook. Without a key it runs on a built-in
mock chat model (a real `BaseChatModel` subclass with rule-based tool calls), so every mechanism
can be studied for free; with the key every cell talks to `openai/gpt-oss-120b` through OpenRouter.

There are no exercises or checkpoints in this track: each section is theory, an architecture
sketch, runnable commented code, and a three-line recap. Evaluation and deployment are pointed to,
not taught in depth.

| Section | Lesson file (derived) | OpsPilot gains |
|---|---|---|
| L1 | `01_plain_model_call.ipynb` | a LangChain chat model, typed messages, `invoke()`, `stream()`, usage metadata |
| L2 | `02_tool_calling_by_hand.ipynb` | `@tool`, `bind_tools()`, `ToolMessage`, a hand-written agent loop with a step limit |
| L3 | `03_first_agent.ipynb` | `create_agent()` with four tools; the trajectory; the graph underneath |
| L4 | `04_production_ready_tools.ipynb` | AST calculator, Pydantic `args_schema`, error values, read vs write tools, the description experiment |
| L5 | `05_structured_output.ipynb` | `response_format=ToolStrategy(SupportTicket)` and `structured_response` driving routing code |
| L6 | `06_conversation_memory.ipynb` | `InMemorySaver` checkpointer, thread ids, `get_state()`, `SummarizationMiddleware` |
| L7 | `07_long_term_memory.ipynb` | `InMemoryStore`, `ToolRuntime`, `context_schema`; memory that survives across threads |
| L8 | `08_knowledge_rag.ipynb` | splitter, embeddings, `InMemoryVectorStore`, retriever; 2-step RAG and a `search_policies` tool |
| L9 | `09_research_and_planning.ipynb` | `web_search` and `fetch_page` tools; implicit loop versus planner + executor |
| L10 | `10_middleware_guardrails_permissions.ipynb` | logging, call limits, tool retry, model fallback, role-based tool filtering, a tool-boundary guard, prompt injection |
| L11 | `11_human_in_the_loop.ipynb` | `HumanInTheLoopMiddleware`, `__interrupt__`, `Command(resume=...)` with approve, reject and edit |
| L12 | `12_langgraph_workflow.ipynb` | `StateGraph`, conditional edges, `interrupt()`, checkpoints and state history |
| L13 | `13_multi_agent.ipynb` | specialists wrapped as tools under a supervisor; when one agent is better |
| L14 | `14_streaming_observability_production.ipynb` | `stream()` modes, a trace middleware with cost estimate, the assembled OpsPilot, the production shape |

The files under `notebooks/` are generated from the track notebook by `split_day_notebooks.py`
for the course portal. Edit the track notebook, then re-run the split; do not edit the lesson files.

## Live versus mock

| Mode | When | What differs |
|---|---|---|
| Mock | no key found | `make_model()` returns `MockChatModel`; tool calls and replies follow fixed rules; every LangChain mechanism runs unchanged |
| Live | key found | `make_model()` returns `ChatOpenAI` pointed at OpenRouter with `reasoning.effort=low`, `temperature=0`, `max_tokens=900` |

Section L8 downloads the `all-MiniLM-L6-v2` embedding model (about 90 MB) in both modes and falls back to a keyword embedding if the download is unavailable.

## Versions

The notebook installs `langchain>=1.2`, `langchain-openai>=1.1` and `langgraph>=1.0`. It was executed end to end with LangChain 1.4.0 and LangGraph 1.2.11 in mock mode. Older tutorials that use `langgraph.prebuilt.create_react_agent` or LCEL chains describe the previous generation of the API.
