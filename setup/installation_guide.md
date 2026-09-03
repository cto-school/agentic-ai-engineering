# Installation Guide

This is the high-level setup contract. Recheck package pins before each course
delivery because hosted APIs and the MCP SDK evolve independently of the notebooks.

## 1. Install Python

Install Python 3.11 or later and confirm that Python and `pip` are available.

## 2. Obtain the repository

Clone the repository with Git or download and extract its ZIP archive.

## 3. Create a virtual environment

Create one environment for the course and activate it before running notebooks.

## 4. Install the core dependencies

For the simplest complete setup, install the root `requirements.txt`.

For staged classroom setup, install smaller requirement files only when needed:

```powershell
py -m pip install -r setup/requirements-core.txt
py -m pip install -r setup/requirements-day2.txt
py -m pip install -r setup/requirements-day5.txt
```

`requirements-day3-optional.txt` is needed only for guided Mem0/LangSmith calls.
`requirements-local-optional.txt` is needed only for the Ollama comparison. Staging
the heavier packages reduces Day 1 setup time and makes installation failures easier
to isolate.

## 5. Configure environment values

Copy `.env.example` to `.env`. Do not commit `.env`.

The standard classroom mode is:

```dotenv
MODEL_MODE=api
```

The instructor supplies an individually limited OpenRouter key. Optional alternatives are:

```dotenv
MODEL_MODE=local
```

```dotenv
MODEL_MODE=mock
```

## 6. Configure the classroom API

Place the individually issued key in `.env`:

```dotenv
OPENROUTER_API_KEY=your_individual_course_key
OPENROUTER_MODEL=openai/gpt-oss-120b
```

Never copy another student's key and never commit `.env`.

## 7. Optional local inference

Students who complete the provider-portability lab may install Ollama and download the course-approved comparison model. Ollama is not required for the main classroom path.

## 8. Day-specific optional accounts

- Day 3: Mem0 Platform and LangSmith are guided, synthetic-data-only exposures.
- Day 5: the stable MCP Python SDK is installed from `requirements.txt` for the local
  stdio lab. FastAPI and Docker remain optional extensions.

## 9. Validate the environment

Run the Day 1 environment check, then run each day's tests before teaching:

```powershell
py day_01_model_tools_agent/environment_check.py
py -m pytest day_01_model_tools_agent/tests day_02_knowledge_and_state/tests day_03_memory_and_safety/tests day_04_multi_agent_systems/tests day_05_ai_harness/tests -q
```

Use `python` instead of `py` where that is the configured launcher. Live model and
hosted-service connectivity require the relevant keys; deterministic mock tests do not.

## Hardware expectations

The course uses short contexts, compact datasets, bounded outputs, and bounded agent loops. Local hardware does not determine access to the primary inference route. Mock mode remains available during outages and while debugging application logic.
