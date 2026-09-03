# Dependency Policy

## Core stack

- Python
- Jupyter
- OpenAI Python SDK configured for OpenRouter
- Pydantic
- LangGraph
- Chroma
- Sentence Transformers
- PyPDF
- Pytest
- Rich

## Optional/later-day stack

- Ollama provider-comparison route
- LangSmith
- Mem0
- MCP Python SDK
- FastAPI and Uvicorn as extensions

## Selection rules

1. Use one primary library per concept in student labs.
2. Mention alternatives without requiring students to install them.
3. Use GPT-OSS through OpenRouter for consistent classroom inference; prefer local/open-source components for embeddings, data, tests, and transparent mechanisms.
4. Provide mock implementations for external systems.
5. Pin versions only after end-to-end reference projects pass.
6. Review dependency versions before each course delivery.
