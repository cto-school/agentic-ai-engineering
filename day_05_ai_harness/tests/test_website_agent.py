from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mini_harness.website_agent import (
    CachedJSONSource, JSONStateStore, WebsiteGuardrails,
    WebsiteMaintenanceAgent, deterministic_proposer,
)


def build(tmp_path, fixture="website_updates.json"):
    site = tmp_path / "site"
    agent = WebsiteMaintenanceAgent(
        CachedJSONSource(ROOT / "data" / fixture),
        deterministic_proposer,
        WebsiteGuardrails(site, {"github.com"}),
        JSONStateStore(tmp_path / "state.json"),
    )
    return agent, site


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
            return type(proposal)(proposal.item_id, "../outside.md", proposal.heading, proposal.body, proposal.source_url)
        agent.proposer = unsafe
        assert agent.check_once().status == "blocked"
        assert not (root / "outside.md").exists()
