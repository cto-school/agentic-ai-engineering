from pathlib import Path
import asyncio,json,sys
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/"src"))
from mini_harness import *


def config(name):
    raw=json.loads((ROOT/"configs"/f"{name}.json").read_text(encoding="utf-8"))
    raw["model"]=ModelConfig(**raw["model"])
    return AgentConfig(**raw)


def test_two_configs_share_runtime():
    runtime=HarnessRuntime(build_demo_registry(),MockModel())
    research=runtime.run(config("research_agent"),"What is a harness?")
    draft=runtime.run(config("task_agent"),"Prepare a short update")
    assert research.status==draft.status=="completed"
    assert "tool result" in research.output and "draft" in draft.output


def test_validation_policy_and_approval():
    registry=build_demo_registry()
    try: registry.call("create_draft",{"subject":"missing body"})
    except ValueError: pass
    else: raise AssertionError("invalid arguments were accepted")
    runtime=HarnessRuntime(registry,MockModel()); cfg=config("task_agent")
    pending=runtime.run(cfg,"Send a synthetic update")
    assert pending.status=="pending_approval" and pending.pending_action
    assert runtime.resume(pending.run_id,cfg,False).status=="cancelled"


def test_events_and_limits_explain_termination():
    class Endless:
        def decide(self,prompt,config,tools,history):
            return ModelDecision("tool",tool="lookup_notes",arguments={"query":prompt})
    cfg=config("research_agent"); cfg.max_steps=2
    result=HarnessRuntime(build_demo_registry(),Endless()).run(cfg,"loop")
    assert result.status=="step_limit"
    assert result.events[-1]["event"]=="step_limit_reached"


def test_fake_mcp_discovery_and_call():
    async def scenario():
        client=FakeMCPClient(); tools=await client.list_tools()
        result=await client.call_tool(tools[0]["name"],{"topic":"harness"})
        return tools,result
    tools,result=asyncio.run(scenario())
    assert tools[0]["name"]=="course_lookup" and "answer" in result
