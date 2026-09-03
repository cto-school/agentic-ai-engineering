# Classroom Setup Guide

This guide assumes every student works on a personal computer.

## Before the course

Students should install:

- Python 3.11 or later
- Git, or download the repository as a ZIP
- VS Code with the Jupyter extension, or JupyterLab
- The course Python dependencies
- Their privately issued OpenRouter course key

Students should run the Day 1 environment checker before class.

## Model choices presented in the first lesson

### Route A — OpenRouter with GPT-OSS (classroom default)

Students place their individually limited key in `.env`. Subsequent guided notebooks use the same model slug and request controls so behaviour is consistent across personal computers.

### Route B — Ollama (optional comparison)

Students with suitable hardware can install Ollama and run the same bounded agent locally. This is a provider-portability and model-capability lab, not a prerequisite.

### Route C — OpenAI API (optional)

Students who already have an OpenAI API key may use the official Python SDK example in Day 1 Notebook 01. They must set `OPENAI_API_KEY` locally and select an API model available to their project.

This is a complete alternative in the first lesson only. Later lessons do not duplicate setup and API-call instructions.

### Route D — Mock mode (fallback)

Mock mode helps when installation fails, inference is too slow, or students need to test control flow. It does not replace experimenting with a real model.

## Instructor preparation

Before Day 1:

- Benchmark GPT-OSS 120B through the exact OpenRouter routing configuration.
- Create, privately distribute, monitor, and later revoke individual limited keys.
- Test concurrent requests from the institution's classroom network.
- Verify the current model price, provider availability, and supported parameters.
- Prepare the optional Ollama command only for the comparison lab.
- Provide a mock-mode fallback exercise.

## Avoiding classroom setup delays

- Do not ask every student to create OpenRouter, OpenAI, LangSmith, and Mem0 accounts on the first day.
- Do not download embedding models until preparation for Day 2.
- Do not install MCP dependencies until preparation for Day 5.
- Pair students temporarily when API/network configuration is incomplete.
- Use small prompts and bounded loops to reduce waiting.
