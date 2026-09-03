"""One scheduled tick of the classroom Website Maintenance Agent."""
from pathlib import Path
import sys

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from mini_harness.website_agent import (  # noqa: E402
    CachedJSONSource, JSONStateStore, WebsiteGuardrails,
    WebsiteMaintenanceAgent, deterministic_proposer,
)

site = ROOT / "data" / "demo_site"
agent = WebsiteMaintenanceAgent(
    CachedJSONSource(ROOT / "data" / "website_updates.json"),
    deterministic_proposer,
    WebsiteGuardrails(site, {"github.com"}),
    JSONStateStore(ROOT / "data" / "website_agent_state.json"),
)
result = agent.check_once()
print(result)
if result.status == "pending_approval":
    print("Dry run only. Review the proposal, then call agent.resolve(run_id, approved=True) explicitly.")

