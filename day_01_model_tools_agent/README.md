# Day 1 — From Model to Agent

## Project

Build a Smart Research Assistant that can return predictable data, request tools, use their results, and stop after a small number of steps.

All required theory is embedded in the notebooks at the point where it is used. Complete Notebook 08 after the guided manual-loop build.

## Progression

```text
First model call
-> configure messages
-> request structured data
-> add one tool
-> add a bounded tool loop
-> represent the loop in LangGraph
```

## Concepts introduced

Model, prompt, message, context window, structured output, schema, validation, tool request, observation, agent loop, node, edge, and state.

## Notebook sequence

1. `01_first_model_call.ipynb` — run OpenRouter, optional Ollama/direct OpenAI, and mock routes. **Available.**
2. `02_configuring_model_behavior.ipynb` — messages and basic generation settings. **Available.**
3. `03_structured_outputs.ipynb` — JSON, Pydantic, and validation failure. **Available.**
4. `04_tool_calling.ipynb` — calculator and local lookup tools. **Available.**
5. `05_manual_agent_loop.ipynb` — repeated tool use with a step limit. **Available.**
6. `06_langgraph_agent.ipynb` — express the known loop as nodes and edges. **Available.**
7. `07_project_research_assistant.ipynb` — assemble and test the final project. **Available.**
8. `08_exercise_manual_agent_loop.ipynb` — independently complete and test the bounded loop. **Available.**

## Required environment

- Core Python dependencies
- An instructor-issued OpenRouter key for the standard classroom route
- Ollama or direct OpenAI access only for optional provider comparisons
- No external access is required for mock mode

## Reference implementation status

The ordinary-Python reference implementation is available in `src/research_agent/` and intentionally precedes the teaching notebooks.

It currently includes:

- OpenRouter, mock, and optional Ollama model routes
- Pydantic message, tool-call, and final-response contracts
- A safe arithmetic tool that does not use `eval()`
- A deterministic local-notes search tool
- A manual agent loop with validation, failure status, duplicate-call detection, and maximum steps
- An optional low-level LangGraph representation of the same loop
- Environment checks and automated tests

### Run without Ollama or an API key

From the repository root, set `MODEL_MODE=mock`, then run:

```text
python day_01_model_tools_agent/run_project.py "Explain an AI agent and calculate 12 * 7"
```

### Run tests

```text
python -m unittest discover -s day_01_model_tools_agent/tests -v
```

### Check the environment

```text
python day_01_model_tools_agent/environment_check.py
```

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

## Failure cases to demonstrate

- Invalid structured output
- Invalid tool argument
- A question requiring no tool
- A question requiring two tool interactions
- Repeated tool requests stopped by the application

## Day 1 behaviour checks

Students run a compact supplied case set and record:

- Final schema valid or invalid
- Expected tool selected or not selected
- Tool arguments valid or invalid
- Agent completed, failed, or reached its limit
- Model turns and approximate API cost

## Provider-portability lab

After the agent works through OpenRouter, students with suitable hardware may run the same request through Ollama. The purpose is to observe model capability, latency, and provider portability—not to require local inference from every student.

## Optional extensions

- Compare GPT-OSS 20B and 120B on the same behaviour cases.
- Use direct OpenAI API access following Notebook 01.
- Stream the final response.
- Add a second information tool.
