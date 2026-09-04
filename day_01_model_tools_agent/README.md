# Day 1 — From Model to Agent

## Project

Build a **Smart Research Assistant**: an application that asks a model a question, lets it
request safe tools, feeds the results back, validates the final answer against a schema,
and stops after a fixed number of turns.

All required theory is embedded in the notebooks at the point where it is used. Complete
Notebook 08 after the guided manual-loop build.

**Classroom notebook:** [`day_01_complete.ipynb`](day_01_complete.ipynb) combines all eight
sections into one Colab-ready learning path. The files under `notebooks/` remain the
modular source and standalone lesson versions.

## Every notebook runs without an API key

Each notebook begins with the same course setup cell. It finds the project folder, puts
`src/` on `sys.path`, loads `.env`, and sets `LIVE = bool(os.getenv("OPENROUTER_API_KEY"))`.

- **MOCK mode (default, no key, no cost).** A deterministic provider stands in for the
  model. Every cell still runs and prints output, and the Day 1 behaviour suite gives the
  same table for everyone.
- **LIVE mode.** Set `OPENROUTER_API_KEY` in the repository-root `.env` file and the same
  cells call OpenRouter instead. Live calls are wrapped in `try/except`, so a 400 or a
  timeout prints one line and falls back to the mock rather than ending the class.

Mock output demonstrates that the *application* works. It says nothing about model quality;
only a live run does.

**Setting up `.env` is taught once, in Notebook 01** — location, exact filename, Windows and
macOS/Linux commands, the two variables, the Colab `getpass` alternative, and a
verification cell that prints the key masked.

## Progression

```text
first model call
-> configure messages, temperature and length
-> request schema-validated structured data
-> add one tool the model may request
-> build the bounded tool loop by hand
-> express the same loop as a LangGraph graph
-> assemble the project and test its behaviour
```

## Concepts introduced

Model, prompt, message roles, context window, temperature, token usage, structured output,
JSON Schema and strict mode, validation, tool schema, tool request, observation, agent
loop, step limit, duplicate-request detection, node, edge, and state.

## Notebook sequence

Each lesson notebook is a step-by-step build: short "Step N" markdown, then one small code
cell that prints labelled output. Every notebook ends with a `### Checkpoint` (two
questions with answers) and a `### Recap`.

1. `01_first_model_call.ipynb` — set up `.env`, build a request payload, send it, read the
   usage record, and reason about the context window. Optional Ollama and direct-OpenAI
   routes are documented but commented out.
2. `02_configuring_model_behavior.ipynb` — system versus user messages, `max_tokens`, and a
   `temperature` demonstration; ends by asking for a dictionary and watching `json.loads`
   fail on perfectly friendly prose.
3. `03_structured_outputs.ipynb` — a Pydantic contract, the JSON Schema it generates, and
   the post-processing that makes that schema legal for `strict: True`
   (`additionalProperties: false`, all properties required, unsupported keywords removed).
   Validation failures include a hint for truncated responses.
4. `04_tool_calling.ipynb` — a simplified teaching calculator built line by line and then
   compared with the hardened `research_agent.tools.calculate`; a tool schema, a request,
   argument validation, execution, and the `tool` observation message.
5. `05_manual_agent_loop.ipynb` — students write the ~25-line loop themselves (call model →
   branch on `tool_calls` → execute → append observation → step counter → validate), print
   the message list after every turn, force the step limit, and only then open
   `AgentRunner` and confirm it is the same loop plus bookkeeping.
6. `06_langgraph_agent.ipynb` — the same loop as state, nodes and conditional edges. If
   `langgraph` is not installed the notebook prints an install hint and skips every graph
   cell instead of raising.
7. `07_project_research_assistant.ipynb` — assemble the project, run a four-case behaviour
   suite, and trigger three failures on purpose (see below).
8. `08_exercise_manual_agent_loop.ipynb` — independently complete and test the bounded loop.

## Failure cases demonstrated in code

Notebook 07 does not just list these; it runs them and prints the result.

| Failure | How it is triggered | What you see |
|---|---|---|
| Invalid tool argument | five bad argument dictionaries sent to `Tool.execute` | `is_error=True` and a `Tool error: ...` observation, never an exception |
| Repeated tool request stopped | a `StuckProvider` that repeats one call with a fresh id each time | `status=failed`, `Duplicate tool request stopped: calculator`, after 2 of 5 turns |
| Invalid structured output | a `ChattyProvider` that answers in prose | `status=failed`, `Final response failed validation`, partial trace kept |
| Unknown tool requested | notebook 04, a request for `delete_all_files` | `Tool error: unknown tool ...`; nothing executes |
| Maximum steps reached | notebooks 05 and 06 with `max_steps=1` | `status=max_steps` plus the partial trace |
| A question needing no tool / two tools | behaviour suite cases `direct` and `two_tools` | `tools_used` matches the expectation column |

## Required environment

- Python 3.10 or newer, plus the core dependencies in the root `requirements.txt`.
- `langgraph` for notebook 06 only (`pip install langgraph`); everything else runs without it.
- An instructor-issued OpenRouter key for live mode. Optional: Ollama or your own OpenAI
  key for the provider-portability comparison.
- No network access is required for mock mode.

## Reference implementation

`src/research_agent/` is ordinary Python and intentionally precedes the teaching notebooks:

- `providers.py` — OpenRouter, mock and optional Ollama routes behind one `complete()` interface
- `schemas.py` — Pydantic contracts for messages, tool calls, usage and the final response
- `tools.py` — an AST-based arithmetic tool (no `eval()`) and a deterministic notes search,
  each with a validated argument model
- `agent.py` — the bounded loop with validation, failure statuses, duplicate-call detection
  (the signature is the tool name plus its sorted arguments — never the call id) and `max_steps`
- `graph.py` — the same loop as a LangGraph graph, imported lazily so it is optional

### Run without Ollama or an API key

```text
python day_01_model_tools_agent/run_project.py "Explain an AI agent and calculate 12 * 7"
```

`MODEL_MODE` defaults to `mock`; set it to `api` (with a key) or `local` for the others.

### Run the tests

```text
cd day_01_model_tools_agent && python -m pytest tests -q
```

### Check the environment

```text
python day_01_model_tools_agent/environment_check.py
```

A missing `langgraph` is reported as a warning naming notebook 06, not a failure.

See `setup/model_selection.md` for the hosted-model choice and benchmark process.

## Deliberately deferred

- Formal provider interfaces
- Trace/span terminology
- Advanced retry policies
- Persistent checkpoints
- Performance optimization

## Project completion checklist

- [ ] The assistant accepts a research question.
- [ ] Its final response passes a Pydantic schema.
- [ ] It can use a calculator and one information tool.
- [ ] It returns tool results to the model before answering.
- [ ] It stops after the configured maximum number of steps.
- [ ] The student can explain why the model does not execute Python itself.

## Day 1 behaviour checks

Notebook 07 runs a four-case suite and records, per case: final schema valid or invalid,
expected tool selected or not, agent completed / failed / limited, model turns, and
approximate API cost (zero in mock mode).

## Provider-portability lab

After the agent works through OpenRouter, students with suitable hardware may run the same
request through `OllamaProvider`. The purpose is to observe model capability, latency and
provider portability — not to require local inference from every student.

## Optional extensions

- Compare GPT-OSS 20B and 120B on the same behaviour cases.
- Use direct OpenAI API access following Notebook 01.
- Stream the final response.
- Add a second information tool.
