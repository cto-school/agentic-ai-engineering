# Architecture Diagrams

Detailed diagrams live outside notebooks so they can be reused in slides, READMEs, and handouts.

## Directory convention

```text
diagrams/
├── source/     # Mermaid source grouped by teaching day
└── rendered/   # Optional SVG/PNG exports for slides or handouts
```

All required diagrams now have Mermaid source and nearby text alternatives. GitHub
renders the Mermaid blocks directly. Rendered image exports are optional and should
be regenerated from source rather than edited manually.

## Required diagram inventory

| ID | Diagram | First used |
|---|---|---|
| D01 | Basic LLM application | Day 1 |
| D02 | Structured output and validation | Day 1 |
| D03 | Tool-calling sequence | Day 1 |
| D04 | Manual bounded agent loop | Day 1 |
| D05 | Small LangGraph state flow | Day 1 |
| D06 | Document ingestion pipeline | Day 2 |
| D07 | RAG query pipeline | Day 2 |
| D08 | Context versus state versus memory | Day 3 |
| D09 | Context trimming and rolling summarization | Day 3 |
| D10 | Memory retrieval, update, and hosted boundary | Day 3 |
| D11 | Tool permission and human approval | Day 3 |
| D12 | Single reviewer versus specialist reviewers | Day 4 |
| D13 | Parallel review fan-out/fan-in | Day 4 |
| D14 | Supervisor synthesis architecture | Day 4 |
| D15 | Observability and evaluation flow | Day 4 |
| D16 | Reusable two-agent harness architecture | Day 5 |
| D17 | MCP client consuming an instructor server | Day 5 |
| D18 | Complete course layer map | Day 5 |

## Source files

- [Day 1 diagrams](source/day_01.md) — D01–D05
- [Day 2 diagrams](source/day_02.md) — D06–D07
- [Day 3 diagrams](source/day_03.md) — D08–D11
- [Day 4 diagrams](source/day_04.md) — D12–D15
- [Day 5 diagrams](source/day_05.md) — D16–D19
- [LangChain track diagrams](source/langchain.md) — D20–D30
- [LangGraph track diagrams](source/langgraph.md) — D31–D45
- [Ollama module diagrams](source/ollama.md) — D50–D52
- [n8n module diagrams](source/n8n.md) — D53–D56
- [OpenClaw module diagrams](source/openclaw.md) — D57–D59
- [LLM Foundation module diagrams](source/llm_foundation.md) — D60–D64
- [Mem0 module diagrams](source/mem0.md) — D65–D69

## Diagram rules

- Prefer Mermaid source for maintainability.
- Keep beginner diagrams small and progressive.
- Use consistent colors and names for model, tool, state, and human nodes.
- Do not reveal later layers in early diagrams unless explicitly showing course progression.
- Include alt text or a short text description near every notebook reference.
