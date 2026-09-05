# Mem0 module — A memory layer for your agents

**Outcome:** you understand what a memory layer does for an agent and what it leaves to you, you
have a Mem0 Platform account with your first memories stored, searched, inspected and deleted, you
know the pattern for wiring memory into any agent loop (with a LangGraph example), you can shape
what gets remembered, you can run Mem0 yourself on a laptop with Ollama or as a self-hosted server,
and you know how to evaluate and operate memory responsibly.

Day 3 section 3.3 builds a small memory store by hand and section 3.4 shows Mem0 for a few cells.
This module is the longer road: it assumes nothing from the days, and it is where the questions
students ask after Day 3 ("what does the service actually do with my messages?", "can I run it
locally?", "how do I test it?") are answered.

| Chapter | File | You learn | You do |
|---|---|---|---|
| M1 | `01_why_agents_need_a_memory_layer.md` | the three kinds of memory, what a memory layer is, Platform versus open source, what stays your job | decide which deployment you will use |
| M2 | `02_open_an_account_and_store_first_memories.md` | the dashboard, API keys, the add and search calls, asynchronous adds | store, search, inspect and delete memories for a fictional user |
| M3 | `03_how_add_and_search_work.md` | extraction, deduplication, the three stores, additive semantics, scoping ids, multi-signal retrieval | read a search result field by field |
| M4 | `04_wire_memory_into_an_agent.md` | the search-then-add pattern, prompt formatting, user and run scoping, the LangGraph node | add memory to an agent loop |
| M5 | `05_shape_what_is_remembered.md` | custom instructions, categories, metadata, expiration, update and delete, export, webhooks | tune extraction for a domain |
| M6 | `06_run_mem0_yourself.md` | the open-source library with Ollama, the self-hosted server, Mem0 over MCP | run memory on your laptop with no cloud |
| M7 | `07_privacy_evaluation_and_operations.md` | consent and isolation, failure modes, a recall test set, cost and latency | write a memory evaluation and a retention rule |

Diagrams D65 to D69 in [`diagrams/source/mem0.md`](../../diagrams/source/mem0.md).

Mem0 changes quickly; commands and behaviour in this module were checked against
[docs.mem0.ai](https://docs.mem0.ai) in September 2026. Use only fictional identities and synthetic
content with the hosted service, as everywhere in this course.
