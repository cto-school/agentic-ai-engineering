from pathlib import Path
import asyncio, json, sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mini_harness import *  # noqa: F403,E402
from mini_harness import MAX_STEPS_HARD_CAP, RISK_POLICY, effective_step_limit  # noqa: E402


def config(name):
    raw = json.loads((ROOT / "configs" / f"{name}.json").read_text(encoding="utf-8"))
    raw["model"] = ModelConfig(**raw["model"])
    return AgentConfig(**raw)


def test_two_configs_share_runtime():
    runtime = HarnessRuntime(build_demo_registry(), MockModel())
    research = runtime.run(config("research_agent"), "What is a harness?")
    draft = runtime.run(config("task_agent"), "Prepare a short update")
    assert research.status == draft.status == "completed"
    assert "tool result" in research.output and "draft" in draft.output


def test_a_third_config_needs_no_provider_change():
    """The mock is config-driven, so a new config produces tool + policy events."""
    third = AgentConfig(
        name="notes_agent",
        instructions="Look something up, then ask to email it.",
        allowed_tools=["lookup_notes", "send_email"],
        max_steps=3,
        mock_plan=[{"tool": "lookup_notes", "arguments": {"query": "{prompt}"}},
                   {"tool": "send_email",
                    "arguments": {"to": "mentor@example.test", "subject": "Notes", "body": "{prompt}"}}],
    )
    result = HarnessRuntime(build_demo_registry(), MockModel()).run(third, "harness")
    assert result.status == "pending_approval"
    decisions = [e["details"]["decision"] for e in result.events if e["event"] == "policy_decision"]
    assert decisions == ["allow", "approval"]


def test_config_without_a_plan_still_calls_a_tool():
    plain = AgentConfig("plain_agent", "No plan supplied.", ["lookup_notes"], max_steps=3)
    result = HarnessRuntime(build_demo_registry(), MockModel()).run(plain, "harness")
    assert result.status == "completed"
    assert any(e["event"] == "tool_completed" for e in result.events)


def test_validation_policy_and_approval():
    registry = build_demo_registry()
    try:
        registry.call("create_draft", {"subject": "missing body"})
    except ValueError:
        pass
    else:
        raise AssertionError("invalid arguments were accepted")
    runtime = HarnessRuntime(registry, MockModel())
    cfg = config("task_agent")
    pending = runtime.run(cfg, "Send a synthetic update")
    assert pending.status == "pending_approval" and pending.pending_action
    assert runtime.resume(pending.run_id, cfg, False).status == "cancelled"


def test_unknown_risk_level_fails_closed():
    """An unrecognised risk label must deny, not raise KeyError."""
    strange = ToolSpec("mystery", "Unclassified capability", {"type": "object"}, "quantum")
    cfg = AgentConfig("odd", "x", ["mystery"])
    assert decide(cfg, strange) == "deny"
    assert "quantum" not in RISK_POLICY


def test_events_and_limits_explain_termination():
    class Endless:
        def decide(self, prompt, config, tools, history):
            return ModelDecision("tool", tool="lookup_notes", arguments={"query": prompt})

    cfg = config("research_agent")
    cfg.max_steps = 2
    result = HarnessRuntime(build_demo_registry(), Endless()).run(cfg, "loop")
    assert result.status == "step_limit"
    assert result.events[-1]["event"] == "step_limit_reached"
    assert result.events[-1]["details"]["limit"] == 2


def test_hard_cap_beats_an_over_large_config():
    cfg = config("research_agent")
    cfg.max_steps = 500
    assert effective_step_limit(cfg) == MAX_STEPS_HARD_CAP
    started = HarnessRuntime(build_demo_registry(), MockModel()).run(cfg, "hi").events[0]
    assert started["details"]["effective_step_limit"] == MAX_STEPS_HARD_CAP
    assert started["details"]["requested_max_steps"] == 500


def test_transient_provider_failure_is_retried_once():
    runtime = HarnessRuntime(build_demo_registry(), FlakyModel(failures=1))
    result = runtime.run(config("research_agent"), "What is a harness?")
    assert result.status == "completed"
    retries = [e for e in result.events if e["event"] == "provider_retry"]
    assert len(retries) == 1 and retries[0]["details"]["attempt"] == 1


def test_retry_budget_is_bounded():
    runtime = HarnessRuntime(build_demo_registry(), FlakyModel(failures=99))
    result = runtime.run(config("research_agent"), "What is a harness?")
    assert result.status == "failed"
    assert any(e["event"] == "provider_retry_budget_exhausted" for e in result.events)


def test_fake_mcp_discovery_and_call():
    async def scenario():
        client = FakeMCPClient()
        tools = await client.list_tools()
        result = await client.call_tool(tools[0].name, {"topic": "harness"})
        return tools, result

    tools, result = asyncio.run(scenario())
    # Same attribute access the real MCP SDK uses.
    assert tools[0].name == "course_lookup"
    assert tools[0].inputSchema["required"] == ["topic"]
    assert "answer" in tool_result_payload(result)
