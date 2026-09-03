# Locked Curriculum Decisions

These decisions are the baseline for future syllabus, notebook, code, and diagram development.

## Classroom inference

- OpenRouter is the primary classroom route.
- `openai/gpt-oss-120b` is the initial primary model candidate, pending a final course benchmark immediately before delivery.
- `openai/gpt-oss-20b` is available for comparison or cost-sensitive exercises.
- Each student receives an individually named OpenRouter key with a USD 1 lifetime limit, no automatic reset, and a course-end expiry.
- Course requests use bounded output, low reasoning, bounded loops, and price-aware provider routing.
- Ollama is an optional provider-portability/local-inference lab, not the default.
- Direct OpenAI API usage is shown once as an optional alternative.
- Mock mode remains mandatory for deterministic testing and outage recovery.
- Local embedding models remain the default for Day 2.

## Evaluation

- Day 1 uses small behaviour checks.
- Day 2 introduces a golden set and retrieval/answer evaluation.
- Day 3 evaluates memory and safety behaviour.
- Day 4 uses measured single-system versus multi-agent comparison.
- Day 5 exposes events needed for evaluation and auditing.

## Memory and context

- Students experience growing conversation context, then implement trimming and rolling summarization.
- Students build transparent custom memory before using a product.
- Mem0 Platform is a guided hands-on exposure, not the definition of memory.
- Mem0 OSS is discussed as the self-hosted path.
- Only synthetic data may be sent to hosted memory or observability platforms.

## Orchestration

- Use the LangGraph graph/state runtime directly.
- Model calls inside nodes use plain provider SDK/API code.
- Do not teach LCEL, LangChain chains, LangChain agent abstractions, or LangChain memory abstractions.
- Dependency versions are locked only after all reference projects pass end-to-end validation.

## Observability

- Local structured events and logs are required.
- LangSmith receives a guided hands-on lab using synthetic course data.
- Langfuse is presented or demonstrated as an open/self-hostable alternative; student self-hosting is optional.

## Multi-agent project

- Day 4 is an Engineering Design Review Team, not an autonomous software-development team.
- Students compare a single reviewer, deterministic workflow, and specialized multi-agent review.
- The supplied artifact contains seeded defects for objective evaluation.
- The single-agent system is allowed to win; measured comparison is the learning outcome.
- Deep patterns: sequential workflow, parallel fan-out/fan-in, and supervisor/handoff.

## Harness project

- Day 1 builds one application-specific loop.
- Day 5 builds a reusable platform that hosts at least two agent configurations.
- Differentiators include dynamic tool registration, policy, session/checkpoint persistence, events, and a service boundary.
- Consuming an instructor-provided MCP server is core.
- Writing an MCP server, FastAPI exposure, and Docker are optional extensions.

