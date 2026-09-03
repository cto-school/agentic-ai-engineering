"""Build seven Day 5 capstone notebooks."""
import json
from pathlib import Path
ROOT=Path(__file__).parent; (ROOT/"notebooks").mkdir(exist_ok=True)
META={
"01_what_is_a_harness.ipynb":("Identify repeated responsibilities across earlier projects and distinguish agent, workflow, framework, protocol, runtime, and harness.","Two configurations differ while pointing to the same runtime responsibilities.","List three duplicated responsibilities from Days 1 and 3 and decide which belongs in shared infrastructure.","A harness standardizes execution concerns without erasing application policy.","D16"),
"02_model_configuration_and_runtime.ipynb":("Load provider configuration, run the same runtime in mock or OpenRouter mode, and observe provider failures as events.","Mock mode completes locally; configured OpenRouter uses the same runtime contract and records token usage.","Switch only the provider configuration, then compare event shapes rather than answer wording.","Provider adapters isolate API differences from agent behavior.","D16"),
"03_tool_registry.ipynb":("Register tools dynamically, discover an allow-listed subset, and validate arguments before execution.","Research sees only lookup_notes; a missing draft body is rejected before the function runs.","Register one read-only tool with a required string argument and prove an invalid type fails.","Schemas describe valid calls; registry discovery does not grant authority.","D16"),
"04_permissions_and_limits.ipynb":("Enforce risk policy, pause external actions, cancel safely, deny destructive actions, and stop loops.","Send pauses, rejection becomes cancelled, destructive access is denied, and an endless loop reaches step_limit.","Add erase_workspace to a temporary agent allow-list and prove risk policy still denies it.","The model proposes; policy and limits control execution.","D16"),
"05_events_logs_and_checkpoints.ipynb":("Distinguish events from checkpoints and prove a durable checkpoint can resume after runtime reconstruction.","Approval state survives a new JSON checkpoint-store instance and clears after resolution.","Inspect the checkpoint file, reconstruct the runtime, resume, and verify the event order.","Events explain history; checkpoints preserve continuation state.","D16"),
"06_mcp_client.ipynb":("Discover an MCP tool, classify it locally, authorize it through harness policy, and invoke it through mock or stdio transport.","course_lookup is discovered, classified read-only, and called only after local validation and policy.","Change its local risk to external and show that discovery stays identical while authorization changes.","MCP standardizes capability exchange; the harness retains trust and permission decisions.","D17"),
"07_project_mini_harness.ipynb":("Host two agent configurations with one live/mock runtime, registry, policy, memory, events, checkpoints, and MCP boundary.","Research completes with evidence; task sending pauses; the explicit resume decision determines the outcome.","Add a third configuration without modifying runtime.py and submit its event trace plus one denied action.","The harness is reusable infrastructure, not a universal autonomous agent.","D16–D18"),
"09_project_website_maintenance_agent.ipynb":("Run an operational cycle from public/cached update through state, proposal, named guardrails, approval, persistent website change, verification, and events.","The clean update pauses before writing; rejection changes no file; approval creates a verified Markdown update; poisoned external instructions are blocked.","Run the cached cycle, reject once, approve once in a fresh state directory, and explain which controls remain authoritative with a live model.","A scheduler triggers a bounded run; the agent proposes; guardrails and a human control the real side effect.","D19"),
}
def md(s): return {"cell_type":"markdown","metadata":{},"source":s.splitlines(True)}
def code(s): return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":s.splitlines(True)}
def write(name,cells):
    goals,expected,exercise,recap,diagram=META[name]
    guide=md(f'''## Before you begin

**Required — all students:** run mock mode first. **Choose one:** repeat provider lessons with OpenRouter when configured. The real MCP stdio cell requires the pinned Day 5 SDK; fake MCP is the fallback.

### Learning outcomes

{goals}

Architecture reference: [Day 5 diagrams {diagram}](../../diagrams/source/day_05.md).

### Expected observation

{expected} Exact IDs, timing, and live wording will vary.''')
    finish=md(f'''## Your turn

{exercise}

## Recap

{recap} Name one responsibility that deliberately remains application-specific.''')
    cells=[cells[0],guide,*cells[1:],finish]
    nb={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.11"}},"nbformat":4,"nbformat_minor":5}
    (ROOT/"notebooks"/name).write_text(json.dumps(nb,indent=1),encoding="utf-8")
setup=code('''from pathlib import Path
import sys,json
DAY=Path.cwd()
if (DAY/"day_05_ai_harness").exists(): DAY=DAY/"day_05_ai_harness"
elif DAY.name=="notebooks": DAY=DAY.parent
if not (DAY/"src"/"mini_harness").exists(): raise RuntimeError("Launch Jupyter from the repository, day folder, or notebooks folder.")
sys.path.insert(0,str(DAY/"src"))
from mini_harness import *
def load_config(name):
    raw=json.loads((DAY/"configs"/f"{name}.json").read_text(encoding="utf-8"))
    raw["model"]=ModelConfig(**raw["model"])
    return AgentConfig(**raw)
print("Day folder:",DAY)''')

write("01_what_is_a_harness.ipynb",[
md('''# 1. What is an AI harness?

Across Days 1–4 we repeatedly configured a model, described tools, ran a loop, applied policy, stored state, and logged events. A **runtime** executes one run. A **harness** packages these reusable responsibilities so multiple agent configurations can run consistently.

An agent is the configured behavior. A framework is a coding library. A protocol is an interoperability contract. None of these words guarantees safety or quality.'''),setup,
code('''research=load_config("research_agent"); task=load_config("task_agent")
print(research)
print(task)
print("Different behavior; same runtime contract.")'''),
md('''## Architecture inventory

Map each recurring concern to one module: configuration, provider, registry, policy, runtime, events, checkpoints, memory, and MCP adapter. We build the smallest useful harness, not a general-purpose coding platform.''')])

write("02_model_configuration_and_runtime.ipynb",[
md('''# 2. Model configuration and runtime

Configuration is data; execution is code. Centralizing provider selection prevents every agent from reinventing API calls and makes mock/OpenRouter/Ollama switching explicit.'''),setup,
code('''import os
registry=build_demo_registry(); research=load_config("research_agent")
if os.getenv("OPENROUTER_API_KEY"):
    research.model.provider="openrouter"; research.model.model=os.getenv("OPENROUTER_MODEL","openai/gpt-oss-120b")
provider=build_provider(research.model); print("Provider:",research.model.provider)
runtime=HarnessRuntime(registry,provider)
result=runtime.run(research,"What is centralized by a harness?")
print(result.status,result.output)
for event in result.events: print(event)'''),
md('''## Live provider exercise

`build_provider` now supplies the tested OpenAI-compatible adapter. Change only `ModelConfig.provider`; registry, policy, and runtime remain unchanged. Ollama remains optional. Mock mode tests orchestration—it does not assess answer quality.'''),
md('''### Boundaries

Temperature and output limits belong in model configuration. Maximum tool steps belongs in agent/runtime configuration. API keys belong in environment variables, never JSON or notebooks.''')])

write("03_tool_registry.ipynb",[
md('''# 3. Tool registry and discovery

A registry separates capability definition from the loop. Each tool carries a name, description, input schema, and risk level. The agent sees only its allow-listed subset.'''),setup,
code('''registry=build_demo_registry()
for spec in registry.discover(): print(spec)
research=load_config("research_agent")
print("Research sees:",[x.name for x in registry.discover(research.allowed_tools)])'''),
code('''print(registry.call("lookup_notes",{"query":"harness"}))
try: registry.call("create_draft",{"subject":"body is missing"})
except Exception as error: print(type(error).__name__,error)'''),
md('''## Important distinction

JSON Schema describes valid arguments; it does not authorize execution. Tool discovery says a capability exists; it does not say this agent or user may call it. Policy is checked after validation and before side effects.''')])

write("04_permissions_and_limits.ipynb",[
md('''# 4. Permissions, approval, and limits

The model proposes; Python disposes. Read and reversible local writes may run, external effects pause, destructive tools are denied, and unknown tools fail closed. Every loop has a hard step maximum.'''),setup,
code('''runtime=HarnessRuntime(build_demo_registry(),MockModel()); task=load_config("task_agent")
pending=runtime.run(task,"Send a synthetic course update")
print(pending.status,pending.pending_action)
print("Checkpoint:",runtime.checkpoints.load(pending.run_id))
rejected=runtime.resume(pending.run_id,task,approved=False)
print(rejected.status,rejected.output)'''),
code('''class EndlessModel:
    def decide(self,prompt,config,tools,history):
        return ModelDecision("tool",tool="lookup_notes",arguments={"query":prompt})
cfg=load_config("research_agent"); cfg.max_steps=2
limited=HarnessRuntime(build_demo_registry(),EndlessModel()).run(cfg,"keep going")
print(limited.status,limited.events[-1])'''),
code('''cfg=load_config("task_agent"); cfg.allowed_tools.append("erase_workspace")
destructive=build_demo_registry().get("erase_workspace").spec
print("Visible in allow-list, but policy decision is:",decide(cfg,destructive))
assert decide(cfg,destructive)=="deny"'''),
md('''Rejection is a successful safety outcome even though the run status is failed in this minimal implementation. A production schema might distinguish `cancelled` from technical failure.''')])

write("05_events_logs_and_checkpoints.ipynb",[
md('''# 5. Events, logs, and checkpoints

Events are append-only observations; checkpoints are mutable continuation state. Events support audit and evaluation. A checkpoint lets approval resume the exact pending action without asking the model to recreate it.'''),setup,
code('''events=EventStore(); checkpoint_dir=DAY/"data"/"demo_checkpoints"
checkpoints=JSONCheckpointStore(checkpoint_dir)
runtime=HarnessRuntime(build_demo_registry(),MockModel(),events,checkpoints)
cfg=load_config("task_agent"); paused=runtime.run(cfg,"Send the synthetic update")
for event in events.get(paused.run_id): print(event)
print("Saved state:",checkpoints.load(paused.run_id))
# Simulate a restart by constructing a new runtime and checkpoint-store object.
resumed_runtime=HarnessRuntime(build_demo_registry(),MockModel(),events,JSONCheckpointStore(checkpoint_dir))
done=resumed_runtime.resume(paused.run_id,cfg,approved=True)
print("Final:",done.status,done.output)
print("Checkpoint cleared:",checkpoints.load(paused.run_id))'''),
md('''## Persisting locally

Pass a JSONL path to `EventStore` for durable logs. The teaching checkpoint store is in-memory and transparent; replacing it with SQLite is a useful extension. Do not log secrets, private prompts, or hidden reasoning. LangSmith export remains optional and synthetic-only.''')])

write("06_mcp_client.ipynb",[
md('''# 6. MCP client: discover, then govern

Model Context Protocol standardizes how clients discover and invoke server capabilities. It does not decide whether a capability is trusted or authorized. We first use an offline protocol-shaped client, then optionally connect to the instructor’s local stdio server.'''),setup,
code('''import asyncio
async def offline_demo():
    client=FakeMCPClient(); tools=await client.list_tools()
    print("Discovered:",tools)
    raw=tools[0]
    spec=ToolSpec(raw["name"],raw["description"],raw["inputSchema"],"read")
    cfg=AgentConfig("mcp_demo","Use one supplied fact.",[spec.name])
    print("Local policy:",decide(cfg,spec))
    if decide(cfg,spec)=="allow": print("Result:",await client.call_tool(spec.name,{"topic":"mcp"}))
await offline_demo()'''),
md('''## Official SDK local lab

Install the instructor-pinned stable SDK (`mcp[cli]`). The supplied server is course infrastructure; students need not write it. `StdioMCPClient` uses `StdioServerParameters`, `stdio_client`, `ClientSession.initialize()`, `list_tools()`, and `call_tool()`. On Windows use the Python executable that launches the current environment.'''),
code('''# Set RUN_REAL_MCP=1 before launching Jupyter after installing the pinned SDK.
import importlib.util,os,sys
if os.getenv("RUN_REAL_MCP")=="1" and importlib.util.find_spec("mcp"):
    client=StdioMCPClient(sys.executable,[str(DAY/"instructor_mcp_server.py")])
    tools,result=await client.list_and_optionally_call("course_lookup",{"topic":"harness"})
    print([tool.name for tool in tools]); print(result)
else:
    print("Real MCP skipped. Complete the offline policy path above or enable RUN_REAL_MCP=1.")'''),
md('''## Security checkpoint

Before importing an MCP tool into the registry, inspect server origin, tool description/schema, local risk classification, allowed agents, arguments, output handling, timeout, and logging. A server can change its advertised tools; rediscovery is not automatic authorization.''')])

write("07_project_mini_harness.ipynb",[
md('''# 7. Capstone: Mini AI Harness

One runtime now hosts a research agent and a safe task agent. Demonstrate configuration loading, scoped discovery, validation, policy, bounded execution, events, approval/checkpoint resume, memory interface, and MCP discovery.'''),setup,
code('''runtime=HarnessRuntime(build_demo_registry(),MockModel())
cases=[("research_agent","What is a harness?"),("task_agent","Prepare a concise project update")]
for name,prompt in cases:
    result=runtime.run(load_config(name),prompt)
    print(name,result.status,result.output)
    print("events:",[e["event"] for e in result.events])'''),
code('''task=load_config("task_agent")
pending=runtime.run(task,"Send a synthetic project update")
assert pending.status=="pending_approval"
print("Approval card:",pending.pending_action)
final=runtime.resume(pending.run_id,task,approved=True)
print(final.status,final.output)
print([e["event"] for e in final.events])'''),
code('''memory=SimpleMemory(); memory.add("fictional_asha","Prefer concise project updates")
print(memory.search("fictional_asha","concise update"))
async def mcp_check():
    client=FakeMCPClient(); return await client.list_tools(),await client.call_tool("course_lookup",{"topic":"harness"})
tools,mcp_result=await mcp_check(); print(tools,mcp_result)'''),
md('''## Final explanation

Draw: **agent config → runtime → provider/tool proposal → registry validation → policy → approval or execution → events/checkpoint**. MCP enters through discovery/invocation but still passes local policy.

Defend what this harness does *not* provide: authentication, OS sandboxing, remote MCP trust, distributed workers, deployment, or guaranteed model quality. Optional next steps are FastAPI, Docker, SQLite checkpoints, LangSmith/OpenTelemetry export, and a second hosted provider—not core requirements.''')])
write("09_project_website_maintenance_agent.ipynb",[
md('''# 9. Operational capstone: Website Maintenance Agent

One bounded scheduled tick fetches an update, compares durable state, obtains a structured proposal, applies named guardrails, pauses for approval, writes a real local website file, verifies it, and records the run. The classroom target is local Markdown; direct public publishing is outside the core.'''),setup,
md('''## 1. Configure a fresh classroom run

The cached source is repeatable. The optional live source reads public GitHub release data. Both produce the same `UpdateItem` contract.'''),
code('''from mini_harness import (CachedJSONSource,GitHubReleaseSource,JSONStateStore,WebsiteGuardrails,
    WebsiteMaintenanceAgent,deterministic_proposer,OpenRouterWebsiteProposer,EventStore)
run_root=DAY/"data"/"website_classroom_run"
site_root=run_root/"site"
source=CachedJSONSource(DAY/"data"/"website_updates.json")
events=EventStore(run_root/"events.jsonl")
state=JSONStateStore(run_root/"state.json")
guardrails=WebsiteGuardrails(site_root,{"github.com"})
proposer=deterministic_proposer
print("Website target:",site_root)'''),
md('''## 2. Check once and inspect the exact proposal

No website file exists yet. Approval is a state transition over the exact saved proposal, not a conversational "yes".'''),
code('''agent=WebsiteMaintenanceAgent(source,proposer,guardrails,state,events)
pending=agent.check_once()
print(pending.status,pending.proposal)
assert pending.status in {"pending_approval","no_change"}
print("Website exists before approval:",(site_root/"content"/"updates.md").exists())'''),
md('''## 3. Resolve deliberately

For the first run, leave `approved=False` and prove rejection has no side effect. Use a fresh run directory before repeating with approval.'''),
code('''if pending.status=="pending_approval":
    approved=False  # change only after inspecting the proposal
    final=agent.resolve(pending.run_id,approved)
    print(final.status,final.message)
print("Website exists:",(site_root/"content"/"updates.md").exists())'''),
md('''## 4. Practical indirect prompt-injection challenge

The poisoned fixture mixes a real-looking update with instructions to reveal a key and invoke another tool. External content is evidence, not authority.'''),
code('''poisoned=WebsiteMaintenanceAgent(
    CachedJSONSource(DAY/"data"/"poisoned_website_updates.json"),deterministic_proposer,
    guardrails,JSONStateStore(run_root/"poisoned_state.json"),events)
blocked=poisoned.check_once()
print(blocked.status,blocked.message)
assert blocked.status=="blocked"
assert not (site_root/"content"/"updates.md").exists()'''),
md('''## 5. Optional bounded live observations

Choose one live source and one live model call. If unavailable, use the cached source and instructor-captured trace.

```python
source = GitHubReleaseSource("modelcontextprotocol", "python-sdk", limit=3)
# proposer = OpenRouterWebsiteProposer()
```

Never publish automatically in this course. A live run stops at `pending_approval`.'''),
md('''## 6. Evaluation and optional LLM judge

Deterministic checks remain authoritative: trusted host, matching evidence, allowed path, body-size limit, prohibited active content, explicit approval and post-write verification. An optional LLM judge may score semantic faithfulness, but it is advisory and requires calibration against human-labelled examples.

A model council is unnecessary unless measured evidence shows one proposer/reviewer is inadequate. Day 4 provides the specialist-and-supervisor pattern.'''),
md('''## 7. Daily automation boundary

An operating-system scheduler, cron or CI schedule invokes `run_website_agent.py` once per day. Scheduling is ordinary automation; it merely triggers one bounded check. Production credentials, deployment and unattended approval are outside the core.''')])
print("Built 8 Day 5 guided/project notebooks")
