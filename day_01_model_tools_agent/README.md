# Day 1 — From a Model Call to an Agent

**Project:** Smart Research Assistant — a bounded, tool-using agent whose every step is inspectable.

## The notebook

Students open **one** Google Colab notebook, `day_01_complete.ipynb`, and run it top to bottom.
It is self-contained: no repository clone, no local files, no `.env`. The API key comes from a
Colab secret named `OPENROUTER_API_KEY` (or is typed once when the setup cell asks). Without a
key the notebook runs on a built-in mock model with canned replies and real request/response shapes.

Every section is a step-by-step build: a short explanation, a code cell that does one thing and
prints what happened, and a two-question checkpoint with folded answers. The manual agent loop is
the day's one hands-on exercise: students write it, run a scripted check, then read the commented
reference solution that the rest of the day uses.

| Section | Lesson file (derived) | What is built |
|---|---|---|
| 1.1 | `01_first_model_call.ipynb` | `chat()` helper; messages; statelessness; context window and `max_tokens` |
| 1.2 | `02_configuring_model_behavior.ipynb` | system vs user messages; `temperature`; "an instruction is not a contract" |
| 1.3 | `03_structured_outputs.ipynb` | Pydantic contract; strict JSON schema; validation with readable failures |
| 1.4 | `04_tool_calling.ipynb` | safe AST calculator; tool schema; `execute_tool_call`; four refused requests |
| 1.5 | `05_exercise_manual_agent_loop.ipynb` | **exercise:** `run_agent` with step limit, unknown-tool and duplicate detection |
| 1.6 | `06_langgraph_agent.ipynb` | the same loop as a LangGraph state graph (optional) |
| 1.7 | `07_project_research_assistant.ipynb` | assistant with typed output, behaviour suite, three failures mapped to layers |

The files under `notebooks/` are generated from the day notebook by `split_day_notebooks.py`
for the course portal. Edit the day notebook, then re-run the split; do not edit the lesson files.

## Live versus mock

| Mode | When | What differs |
|---|---|---|
| Mock | no key found | replies are canned rules inside the notebook; shapes, tools, validation and the loop are real |
| Live | key found | `chat()` calls `openai/gpt-oss-120b` through OpenRouter with `reasoning.effort=low`, `temperature=0`, `max_tokens=600` |

Both modes run every cell. The one *required live observation* (section 1.1) compares two live
replies to the same prompt.

## Failure cases demonstrated in code

| Layer | Trigger | What the student sees |
|---|---|---|
| Tool | invented tool, wrong field, code in an expression, `2 ** 999`, `10 / 0` | `Tool error: …` returned as an observation; no function ran |
| Loop | `max_steps=1`; a model that repeats the same request | status `max_steps` / `failed` with a reason and the partial trace |
| Output | a final JSON with `key_points: []` and `confidence: 2` | `invalid: …` from Pydantic; the typed object is `None` |

## Reference package (optional)

`src/research_agent/` is a packaged version of the same design (providers, tools, bounded runner,
LangGraph form) with tests in `tests/`. It is not used by the notebook; it exists for instructors
and for students who want to see the notebook's ideas as an installable module.

```powershell
python -m pytest tests -q
python run_project.py "What is an agent, and what is 12 * 9?"
```
