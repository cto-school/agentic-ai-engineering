# Course Syllabus

## Course title

Agentic AI Engineering: From Model Calls to AI Harnesses

## Audience

Final-year engineering students with Python fundamentals but no prior agentic AI experience.

## Prerequisites

Students should be able to:

- Read and modify basic Python.
- Use functions, lists, dictionaries, and classes at a basic level.
- Install a Python package and run a notebook.
- Understand the basic idea of an HTTP API.
- Navigate files and folders.

Git experience is helpful but will not be assumed for the core labs.

## Teaching philosophy

The course follows this sequence:

```text
Use it -> observe it -> understand it -> modify it -> engineer it
```

Students are not expected to learn a framework as the subject. They first build or inspect the mechanism, discover its limitation, and then use a library where it makes the mechanism easier to maintain.

The course avoids introducing the complete agent architecture on the first day. Terms appear progressively as students encounter the corresponding problem.

## Course outcomes

By the end, students should be able to:

1. Explain the difference between an LLM application, workflow, agent, multi-agent system, and harness.
2. Configure the course OpenRouter model and understand local/direct-provider alternatives.
3. Obtain validated structured output from a model.
4. Let a model request tools and implement a bounded agent loop.
5. Build a small RAG system that retrieves evidence and supplies citations.
6. Distinguish context, state, knowledge, and persistent memory.
7. Add planning, permission checks, guardrails, and human approval.
8. Inspect execution and perform small, practical evaluations.
9. Construct handoff and supervisor-based multi-agent workflows.
10. Build a mini harness containing a runtime, tool registry, policy checks, events, and an MCP connection.

## Architectural coverage

```text
Model -> Tool -> Agent -> Knowledge -> Memory -> Safety
      -> Observability -> Multi-Agent -> Harness
```

Two ideas run across these layers:

- **State and workflow:** how information and execution progress through a system.
- **Evaluation and reliability:** how we determine whether the system behaves correctly.

## Five-day map

The table below is the final delivery map. Notebook counts are intentionally uneven:
the number follows the conceptual steps required by the project, not an artificial
daily template.

| Day | Required project | Notebook path | Required inference path | Guided/optional exposure |
|---|---|---|---|---|
| 1 | Smart Research Assistant | `day_01_model_tools_agent/notebooks/` | OpenRouter or deterministic fallback | Ollama comparison, direct OpenAI once, LangGraph |
| 2 | Engineering Knowledge Assistant | `day_02_knowledge_and_state/notebooks/` | Local/mock retrieval plus OpenRouter or extractive fallback | Sentence Transformers, Chroma |
| 3 | Safe Personal Task Agent | `day_03_memory_and_safety/notebooks/` | Mock or OpenRouter action proposal with local policy | Mem0, LangSmith, Langfuse, LangGraph interrupt pattern |
| 4 | Engineering Design Review Team | `day_04_multi_agent_systems/notebooks/` | Structured mock or OpenRouter reviewers | LangGraph fan-out representation, LangSmith traces |
| 5 | Mini AI Harness and Website Maintenance Agent | `day_05_ai_harness/notebooks/` | Cached/mock first, then one bounded public-data or OpenRouter observation | Ollama adapter, real local MCP stdio, FastAPI/Docker extensions |

### Day 1: From model to agent

Project: Smart Research Assistant

```text
Model call -> prompt configuration -> structured output
-> tool request -> manual agent loop -> LangGraph agent
```

### Day 2: Knowledge and state

Project: Engineering Knowledge Assistant

```text
Documents -> chunks -> embeddings -> retrieval -> RAG
-> citations -> retrieval tool -> stateful knowledge agent
```

### Day 3: Context, memory, planning, and safety

Project: Safe Personal Task Agent

```text
History -> context trimming and summarization -> persistent memory -> small plan -> side-effecting tools
-> permissions -> human approval -> visible execution
```

### Day 4: Multi-agent systems and evaluation

Project: Engineering Design Review Team

```text
Seeded engineering artifact -> single-reviewer baseline -> deterministic checks
-> parallel specialist reviewers -> supervisor synthesis -> measured A/B
```

### Day 5: AI harness

Project: Mini AI Harness operating a Website Maintenance Agent

```text
Repeated components -> model configuration -> runtime
-> tool registry -> guardrails -> events -> MCP -> integrated harness
-> scheduled check -> approval -> persistent website update -> verification
```

## Final notebook learning contract

Every required notebook now provides:

- a problem or limitation before the new terminology;
- concrete learning outcomes;
- a deterministic path that does not spend API credit;
- a live route only where model behavior is part of the lesson;
- an expected observation stated as an invariant rather than fixed wording;
- a bounded student modification;
- a recap connecting the new layer to previous layers;
- a link to the relevant external architecture diagrams.

Short notebooks are not padded to satisfy a fixed cell count. A notebook is complete
when the student can build or inspect the mechanism, observe its state, reproduce a
limitation, make one bounded change, and explain the remaining boundary.

## Required versus optional interpretation

- **Required — all students:** local Python mechanisms, mock routes, supplied datasets,
  safety policy, evaluations, and all five integrated projects.
- **Choose one:** OpenRouter is the primary classroom live route; deterministic mock is
  the outage/debugging route. Students should normally observe both, but live availability
  is never part of student performance.
- **Guided product exposure:** Mem0 Platform and LangSmith use synthetic data and may be
  demonstrated or completed within their current free quotas.
- **Optional portability:** Ollama and direct OpenAI show provider choice without repeating
  complete setup in later notebooks.
- **Extension:** Langfuse self-hosting, FastAPI, Docker, writing an MCP server, and
  production deployment remain outside the core course.

## Scope boundaries

The core course does not attempt to cover:

- CrewAI or AutoGen.
- Surveys of many agent frameworks.
- Model training, fine-tuning, or reinforcement learning.
- Agent swarms or open-ended autonomous agents.
- Advanced Graph RAG or retrieval research.
- Browser/computer-use agents.
- Kubernetes or distributed agent infrastructure.
- Production deployment, remote MCP authentication, or enterprise identity systems.

These may be referenced as future-learning topics but should not displace core practice.

## Delivery model

Each day uses:

- Contextual theory inside notebooks.
- Small, runnable demonstrations.
- A deliberately broken or limited version.
- A guided improvement.
- Short exercises with explicit completion criteria.
- One independently runnable project.

Projects are conceptually cumulative but operationally independent. Each day includes the starter components needed to begin even if a student has not completed an earlier project.

## Included learner resources

- All required theory embedded beside the relevant notebook code so students do not switch resources.
- 45 notebooks, including six pivotal stub-and-test notebooks, and five independently runnable project implementations.
- Pivotal exercises covering the manual loop, RAG context assembly, history compaction, action policy, supervisor merging, and the tool registry.
- Architecture diagrams maintained outside the notebooks.
- A glossary, worked RAG failure diagnosis, deterministic datasets, golden sets, and offline tests.
- Individually limited classroom access containing **Rs 100 worth of AI API credits per student** for the guided live-model exercises.

The API credit is instructional infrastructure, not a requirement for completing the logic. Deterministic mock routes remain available for debugging, outages, and repeatable evaluation.

## Classroom timetable

The instructor delivery plan is maintained in `instructor/five_day_timetable.md`. It separates core lessons from optional hosted-product demonstrations and provides an offline fallback for every day. Mem0 and LangSmith are short guided exposures; they do not displace memory, policy, tracing, and evaluation mechanisms that students implement locally.

## Infrastructure policy

- OpenRouter with a course-approved GPT-OSS model is the default classroom route.
- Each student uses an individually limited and expiring course key.
- Ollama is an optional local-provider comparison rather than a prerequisite.
- A direct OpenAI API example is shown once for students with their own access.
- Mock mode is required for application-logic testing and low-spec machines.
- Provider latency and cost are observed but are not treated as student performance.
- Datasets, prompts, and agent loops remain intentionally small.
- Free hosted tiers are never described as guaranteed.
- Synthetic data is required when using hosted memory or tracing systems.

## Evaluation progression

- Day 1: schema, tool-selection, argument, and termination checks.
- Day 2: 10-case golden set, retrieval hit-rate, grounding, citation, and abstention.
- Day 3: context/memory behaviour and allow/deny/approval safety cases.
- Day 4: single-agent versus multi-agent defect discovery, false positives, calls, tokens, latency, and cost.
- Day 5: reusable run events that support auditing and evaluation.

One bounded live observation is required each day. Provider or network availability is never graded; instructor-captured traces and deterministic/cached routes are the fallback. The Day 5 website workflow performs a real local file update only after explicit approval and does not publish unattended.

## Hosted product exposure

Students first implement a transparent local mechanism, then inspect a productized system:

- Custom memory before a guided Mem0 Platform exercise.
- Local structured logs before a guided LangSmith tracing exercise.
- Mem0 OSS and Langfuse are presented as self-hostable alternatives.

Only fictional users, synthetic prompts, supplied public course documents, and deliberately created code artifacts may be sent to these hosted platforms.
