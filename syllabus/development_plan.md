# Curriculum Development Plan

## Stage 1: Foundation — complete

- Course outcomes and scope
- Five-day concept progression
- Project specifications
- Repository structure
- Notebook and day README templates
- Setup/account plan
- Glossary starter
- Diagram inventory

## Stage 2: Build final projects first — complete

Implement the known-good final version of each project before decomposing it into lessons. This validates dependencies, model capabilities, data size, hardware expectations, and realistic project scope.

Recommended order:

1. Day 1 research agent
2. Day 2 knowledge agent
3. Day 3 safe task agent
4. Day 4 engineering design review team
5. Day 5 harness

## Stage 3: Design backward — complete

For every final project, work backward:

```text
Final project
<- final capability
<- limitation that motivates it
<- previous working stage
<- smallest starting example
```

## Stage 4: Create student notebooks — complete

Each notebook should follow `templates/notebook_template.md` and include both local and mock execution where practical.

## Stage 5: Verify environments — offline reference validation complete

Test the complete course on:

- A clean Windows environment.
- A clean Linux or macOS environment where available.
- OpenRouter classroom mode.
- Optional local Ollama comparison mode.
- Optional hosted API mode.
- Mock/offline mode.

Record exact supported versions only after this verification.

Repository-wide offline validation is provided by `validate_course.py`. Clean-machine,
live OpenRouter, hosted-product, and real MCP checks remain pre-delivery instructor
responsibilities because credentials, quotas, SDKs, and network policies change.

## Stage 6: Beginner pilot

Pilot with learners unfamiliar with agentic AI. Capture setup time, confusing terminology, notebook failures, inference latency, and points requiring instructor intervention.
