from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mini_harness import HarnessRuntime, MockModel, EventStore, JSONCheckpointStore  # noqa: E402
from mini_harness.website_agent import (  # noqa: E402
    CachedJSONSource, JSONStateStore, WebsiteGuardrails,
    WebsiteMaintenanceAgent, build_website_registry, deterministic_proposer,
    website_agent_config,
)

FIRST_ITEM = "course-release-2"


def build(tmp_path, fixture="website_updates.json"):
    site = tmp_path / "site"
    agent = WebsiteMaintenanceAgent(
        CachedJSONSource(ROOT / "data" / fixture),
        deterministic_proposer,
        WebsiteGuardrails(site, {"github.com"}),
        JSONStateStore(tmp_path / "state.json"),
    )
    return agent, site


def build_harness(tmp_path, fixture="website_updates.json"):
    """The same two actions, driven by the harness instead of by hand."""
    site = tmp_path / "site"
    guardrails = WebsiteGuardrails(site, {"github.com"})
    state = JSONStateStore(tmp_path / "state.json")
    registry = build_website_registry(
        CachedJSONSource(ROOT / "data" / fixture), deterministic_proposer, guardrails, state)
    runtime = HarnessRuntime(registry, MockModel(), EventStore(tmp_path / "events.jsonl"),
                             JSONCheckpointStore(tmp_path / "checkpoints"))
    return runtime, website_agent_config(), site


# --- hand-written workflow ---------------------------------------------------

def test_approval_creates_persistent_verified_update():
    with tempfile.TemporaryDirectory() as directory:
        agent, site = build(Path(directory))
        pending = agent.check_once()
        assert pending.status == "pending_approval"
        assert not (site / "content" / "updates.md").exists()
        done = agent.resolve(pending.run_id, approved=True)
        assert done.status == "completed"
        text = (site / "content" / "updates.md").read_text(encoding="utf-8")
        assert "Engineering Lab Schedule Updated" in text and "Source:" in text


def test_change_detection_walks_the_backlog_then_reports_no_change():
    """Two cached items: the second check finds new work, the third finds none."""
    with tempfile.TemporaryDirectory() as directory:
        agent, _ = build(Path(directory))
        first = agent.check_once()
        agent.resolve(first.run_id, approved=True)
        second = agent.check_once()
        assert second.status == "pending_approval"
        assert second.proposal.item_id != first.proposal.item_id
        agent.resolve(second.run_id, approved=True)
        assert agent.check_once().status == "no_change"


def test_rejection_has_no_website_side_effect():
    with tempfile.TemporaryDirectory() as directory:
        agent, site = build(Path(directory))
        pending = agent.check_once()
        assert agent.resolve(pending.run_id, approved=False).status == "cancelled"
        assert not (site / "content" / "updates.md").exists()


def test_indirect_injection_is_blocked_before_proposal():
    with tempfile.TemporaryDirectory() as directory:
        agent, site = build(Path(directory), "poisoned_website_updates.json")
        result = agent.check_once()
        assert result.status == "blocked"
        assert "instruction-like content" in result.message
        assert not site.exists()


def test_path_escape_is_blocked():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        agent, site = build(root)

        def unsafe(item):
            proposal = deterministic_proposer(item)
            return type(proposal)(proposal.item_id, "../outside.md", proposal.heading,
                                  proposal.body, proposal.source_url)

        agent.proposer = unsafe
        assert agent.check_once().status == "blocked"
        assert not (root / "outside.md").exists()


# --- same workflow, driven by the harness ------------------------------------

def test_harness_pauses_on_the_external_publish_tool():
    with tempfile.TemporaryDirectory() as directory:
        runtime, config, site = build_harness(Path(directory))
        result = runtime.run(config, FIRST_ITEM)
        assert result.status == "pending_approval"
        assert result.pending_action["tool"] == "publish_update"
        decisions = [(e["details"]["tool"], e["details"]["decision"])
                     for e in result.events if e["event"] == "policy_decision"]
        assert decisions == [("propose_update", "allow"), ("publish_update", "approval")]
        assert not (site / "content" / "updates.md").exists()


def test_harness_approval_writes_and_rejection_does_not():
    with tempfile.TemporaryDirectory() as directory:
        runtime, config, site = build_harness(Path(directory))
        rejected = runtime.run(config, FIRST_ITEM)
        assert runtime.resume(rejected.run_id, config, approved=False).status == "cancelled"
        assert not (site / "content" / "updates.md").exists()

        approved = runtime.run(config, FIRST_ITEM)
        done = runtime.resume(approved.run_id, config, approved=True)
        assert done.status == "completed"
        text = (site / "content" / "updates.md").read_text(encoding="utf-8")
        assert "Engineering Lab Schedule Updated" in text
        assert runtime.checkpoints.load(approved.run_id) is None


def test_harness_guardrail_block_is_recorded_as_a_tool_failure():
    with tempfile.TemporaryDirectory() as directory:
        runtime, config, site = build_harness(Path(directory), "poisoned_website_updates.json")
        result = runtime.run(config, "poisoned-1")
        assert result.status == "failed"
        assert "instruction-like content" in result.output
        failures = [e for e in result.events if e["event"] == "tool_failed"]
        assert failures and failures[0]["details"]["tool"] == "propose_update"
        assert not (site / "content" / "updates.md").exists()
