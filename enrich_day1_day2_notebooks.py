"""Idempotently add final beginner guidance to the hand-authored Day 1–2 notebooks."""
import json
from pathlib import Path

ROOT=Path(__file__).parent
META={
"day_01_model_tools_agent/notebooks/01_first_model_call.ipynb":("Send one prompt through the classroom route and identify request, response, provider, model, and usage fields.","Mock output is deterministic; live wording varies, but a non-empty response and usage record should appear.","Change one prompt constraint and compare outputs without changing providers.","D01","A model call generates output from supplied context; it does not create an agent."),
"day_01_model_tools_agent/notebooks/02_configuring_model_behavior.ipynb":("Separate standing instructions from the current task and observe temperature/output constraints.","The constrained response follows the requested format more reliably than the broad prompt.","Change one instruction at a time and record which behavior changes.","D01","Configuration shapes generation but does not guarantee truth or safety."),
"day_01_model_tools_agent/notebooks/03_structured_outputs.ipynb":("Define a Pydantic contract, request structured data, and handle validation failure.","Valid data becomes a typed object; plausible data outside field constraints is rejected.","Add one constrained field and deliberately supply an invalid value.","D02","A schema makes failure visible; it does not make model claims correct."),
"day_01_model_tools_agent/notebooks/04_tool_calling.ipynb":("Distinguish a model tool request from host validation and Python execution.","The model returns a name and arguments; the calculator runs only after validation in application code.","Send an unsupported argument and prove the function is not executed.","D03","The model requests; the host validates, authorizes, and executes."),
"day_01_model_tools_agent/notebooks/05_manual_agent_loop.ipynb":("Trace repeated model/tool turns and prove the host step limit stops execution.","Every tool result is appended before the next model call; forced looping ends at max_steps.","Set max_steps to one and explain the incomplete trace.","D04","An agent loop is bounded application control around model decisions."),
"day_01_model_tools_agent/notebooks/06_langgraph_agent.ipynb":("Represent the same loop as state, nodes, edges, and conditional routing.","The final state contains the message history and a terminal route.","Change one routing condition to a safe failure and inspect the final state.","D05","LangGraph represents orchestration; it does not replace tools, policy, or evaluation."),
"day_01_model_tools_agent/notebooks/07_project_research_assistant.ipynb":("Run the bounded research project and explain model, tool, loop, validation, and termination boundaries.","The behavior suite completes in mock mode and reports usage without spending API credit.","Add one behavior case and one tool failure case with objective assertions.","D01–D05","The project is an application-specific agent, not yet a reusable harness."),
"day_02_knowledge_and_state/notebooks/01_documents_and_chunks.ipynb":("Inspect supplied documents and create chunks that retain source and section metadata.","Every chunk has stable text, source, section, and identifier fields.","Change chunk size or heading boundaries and compare one resulting record.","D06","Retrieval quality depends on the units indexed, not only the model."),
"day_02_knowledge_and_state/notebooks/02_keyword_search.ipynb":("Build an explainable lexical baseline and identify a meaning match it misses.","Exact terms rank well; a paraphrase exposes the baseline limitation.","Write one exact query and one paraphrase, then compare returned sections.","D06","Always establish a simple baseline before adding semantic infrastructure."),
"day_02_knowledge_and_state/notebooks/03_embeddings_and_semantic_search.ipynb":("Compare deterministic teaching embeddings with sentence-transformer semantic search.","The offline hasher is stable but limited; the optional real embedder better handles paraphrases after download.","Record one query where both agree and one where they differ.","D06","Similarity is a ranking signal, not proof that a chunk answers the question."),
"day_02_knowledge_and_state/notebooks/04_basic_rag.ipynb":("Trace question to retrieval to grounded generation and diagnose which layer fails.","The answer uses retrieved evidence; an irrelevant retrieval produces a visibly weak or abstaining result.","Replace the top chunk with an irrelevant one and classify the resulting failure.","D07","RAG is a pipeline; retrieval and generation must be inspected separately."),
"day_02_knowledge_and_state/notebooks/05_citations_and_abstention.ipynb":("Require attributable citations and treat insufficient evidence as a successful abstention.","Answerable input cites supplied sections; unanswerable input does not invent an answer.","Add one unanswerable question and assert abstention plus absence of fabricated citations.","D07","Grounding needs application checks, not only an instruction to cite."),
"day_02_knowledge_and_state/notebooks/06_retrieval_evaluation.ipynb":("Calculate retrieval success from a golden set and compare top-k settings.","Changing top-k changes section recall and may add irrelevant context.","Hand-calculate one case before checking the helper result.","D07","Evaluation converts retrieval tuning from guesswork into measurement."),
"day_02_knowledge_and_state/notebooks/07_retrieval_tool_and_state.ipynb":("Expose retrieval as a tool and inspect application state separately from model context and memory.","State shows the query, retrieved chunks, and answer-building inputs.","Remove one state field and explain what becomes harder to debug.","D07","State belongs to the running application; context is only what the model receives."),
"day_02_knowledge_and_state/notebooks/08_project_knowledge_assistant.ipynb":("Integrate ingestion, retrieval, citations, abstention, state, and separate evaluation.","The ten-case report exposes retrieval and answer outcomes rather than one vague score.","Diagnose one missed case using query, chunks, expected source, and proposed change.","D06–D07","A knowledge agent is only as reliable as its retrieval evidence and evaluation."),
}

TAG="final-beginner-guidance"
for relative,(goals,expected,exercise,diagram,recap) in META.items():
    path=ROOT/relative; notebook=json.loads(path.read_text(encoding="utf-8"))
    cells=[cell for cell in notebook["cells"] if TAG not in cell.get("metadata",{}).get("tags",[])]
    day="day_01" if "day_01" in relative else "day_02"
    diagram_path="../../diagrams/source/day_01.md" if day=="day_01" else "../../diagrams/source/day_02.md"
    guide={"cell_type":"markdown","metadata":{"tags":[TAG]},"source":f'''## Before you begin

### Learning outcomes

{goals}

Architecture reference: [{diagram}]({diagram_path}).

### Expected observation

{expected}
'''.splitlines(True)}
    finish={"cell_type":"markdown","metadata":{"tags":[TAG]},"source":f'''## Your turn

{exercise}

## Recap

{recap}
'''.splitlines(True)}
    notebook["cells"]=[cells[0],guide,*cells[1:],finish]

    # Day 1 notebooks 1–4 predate the shared provider project. Keep their mechanisms
    # visible, but make the required path continue in deterministic mock mode when a
    # classroom key or network is unavailable.
    code_cells=[cell for cell in notebook["cells"] if cell["cell_type"]=="code"]
    if relative.endswith("01_first_model_call.ipynb"):
        code_cells[0]["source"]='''# Run once if required, then restart the kernel.
# %pip install -q openai python-dotenv
import os
from types import SimpleNamespace
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
COURSE_MODEL=os.getenv("OPENROUTER_MODEL","openai/gpt-oss-120b")
api_key=os.getenv("OPENROUTER_API_KEY")
client=OpenAI(base_url="https://openrouter.ai/api/v1",api_key=api_key) if api_key else None
print("Route:","OpenRouter" if client else "mock fallback")
'''.splitlines(True)
        code_cells[1]["source"]='''question="Explain recursion in two sentences for a beginner."
if client:
    response=client.chat.completions.create(model=COURSE_MODEL,messages=[{"role":"user","content":question}],
        max_tokens=300,extra_body={"reasoning":{"effort":"low","exclude":True},"provider":{"sort":"price"}})
    answer=response.choices[0].message.content
else:
    response=None
    answer="Recursion is when a function solves a problem by calling itself on a smaller version. It needs a base case so the calls eventually stop."
print(answer)
'''.splitlines(True)
        code_cells[2]["source"]='''if response:
    print(response.usage)
else:
    print({"provider":"mock","prompt_tokens":0,"completion_tokens":0,"cost_usd":0.0})
'''.splitlines(True)
    elif relative.endswith("02_configuring_model_behavior.ipynb"):
        code_cells[0]["source"]='''import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
api_key=os.getenv("OPENROUTER_API_KEY")
client=OpenAI(base_url="https://openrouter.ai/api/v1",api_key=api_key) if api_key else None
COURSE_MODEL=os.getenv("OPENROUTER_MODEL","openai/gpt-oss-120b")
def ask(messages,max_tokens=400):
    if not client:
        constrained=any(message.get("role")=="system" for message in messages)
        return "Definition: An agent chooses bounded actions.\\nExample: It requests a calculator tool.\\nLimitation: Host code must control execution." if constrained else "An AI agent uses a model and tools to work toward a goal."
    return client.chat.completions.create(model=COURSE_MODEL,messages=messages,max_tokens=max_tokens,
        extra_body={"reasoning":{"effort":"low","exclude":True}}).choices[0].message.content
print("Route:","OpenRouter" if client else "mock fallback")
'''.splitlines(True)
    elif relative.endswith("03_structured_outputs.ipynb"):
        code_cells[0]["source"]='''import json,os
from types import SimpleNamespace
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel,Field,ValidationError
load_dotenv(); api_key=os.getenv("OPENROUTER_API_KEY")
client=OpenAI(base_url="https://openrouter.ai/api/v1",api_key=api_key) if api_key else None
COURSE_MODEL=os.getenv("OPENROUTER_MODEL","openai/gpt-oss-120b")
print("Route:","OpenRouter" if client else "mock fallback")
'''.splitlines(True)
        code_cells[1]["source"]='''if client:
    plain=client.chat.completions.create(model=COURSE_MODEL,messages=[{"role":"user","content":"Explain an AI agent. Return JSON with topic, summary, key_points, and confidence."}],max_tokens=500,extra_body={"reasoning":{"effort":"low","exclude":True}})
    plain_text=plain.choices[0].message.content
else:
    plain_text='{"topic":"AI agents","summary":"A model-guided application","key_points":["May request tools"],"confidence":0.8}'
print(plain_text)
'''.splitlines(True)
        code_cells[3]["source"]='''if client:
    response=client.chat.completions.create(model=COURSE_MODEL,messages=[{"role":"user","content":"Explain an AI agent for a beginner with two or three key points."}],response_format={"type":"json_schema","json_schema":{"name":"research_summary","strict":True,"schema":schema}},max_tokens=600,extra_body={"reasoning":{"effort":"low","exclude":True},"provider":{"require_parameters":True}})
    response_text=response.choices[0].message.content
else:
    response_text=json.dumps({"topic":"AI agents","summary":"An application that uses a model to choose bounded actions.","key_points":["The host executes tools","The loop needs limits"],"confidence":0.9})
result=ResearchSummary.model_validate_json(response_text)
result
'''.splitlines(True)
    elif relative.endswith("04_tool_calling.ipynb"):
        code_cells[0]["source"]='''import ast,json,operator,os
from types import SimpleNamespace
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel,Field,ValidationError
load_dotenv(); api_key=os.getenv("OPENROUTER_API_KEY")
client=OpenAI(base_url="https://openrouter.ai/api/v1",api_key=api_key) if api_key else None
COURSE_MODEL=os.getenv("OPENROUTER_MODEL","openai/gpt-oss-120b")
print("Route:","OpenRouter" if client else "mock fallback")
'''.splitlines(True)
        code_cells[3]["source"]='''messages=[{"role":"user","content":"What is 12 * 7? Use the calculator."}]
if client:
    first=client.chat.completions.create(model=COURSE_MODEL,messages=messages,tools=[calculator_tool],max_tokens=400,
        extra_body={"reasoning":{"effort":"low","exclude":False},"provider":{"require_parameters":True}})
    assistant_message=first.choices[0].message
else:
    call=SimpleNamespace(id="mock-calculator",function=SimpleNamespace(name="calculator",arguments='{"expression":"12 * 7"}'))
    assistant_message=SimpleNamespace(tool_calls=[call],model_dump=lambda **kwargs:{"role":"assistant","content":"","tool_calls":[{"id":call.id,"type":"function","function":{"name":"calculator","arguments":call.function.arguments}}]})
assistant_message.tool_calls
'''.splitlines(True)
        code_cells[5]["source"]='''messages.append(assistant_message.model_dump(exclude_none=True))
messages.append({"role":"tool","tool_call_id":call.id,"content":tool_output})
if client:
    final=client.chat.completions.create(model=COURSE_MODEL,messages=messages,tools=[calculator_tool],max_tokens=300,
        extra_body={"reasoning":{"effort":"low","exclude":True}})
    final_text=final.choices[0].message.content
else:
    final_text=f"The calculator result is {tool_output}."
print(final_text)
'''.splitlines(True)
    path.write_text(json.dumps(notebook,indent=1,ensure_ascii=False),encoding="utf-8")
print(f"Enriched {len(META)} Day 1–2 notebooks")
