"""One scheduled tick of the Website Maintenance Agent, driven by the mini harness.

A scheduler (cron, Task Scheduler, CI) runs this once. Scheduling is ordinary
automation: all it does is start one bounded harness run. The run stops at
`pending_approval` because publishing is classified `external`, so nothing is
ever written to the website without a person saying yes.

Everything this script writes lands under data/generated/ (git-ignored).
"""
from pathlib import Path
import sys

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from mini_harness import (  # noqa: E402
    CachedJSONSource, EventStore, HarnessRuntime, JSONCheckpointStore, JSONStateStore,
    MockModel, WebsiteGuardrails, build_website_registry, deterministic_proposer,
    website_agent_config,
)

RUN_ROOT = ROOT / "data" / "generated" / "website_agent"
SITE_ROOT = RUN_ROOT / "site"

source = CachedJSONSource(ROOT / "data" / "website_updates.json")
state = JSONStateStore(RUN_ROOT / "state.json")
guardrails = WebsiteGuardrails(SITE_ROOT, {"github.com"})
registry = build_website_registry(source, deterministic_proposer, guardrails, state)
runtime = HarnessRuntime(registry, MockModel(),
                         EventStore(RUN_ROOT / "events.jsonl"),
                         JSONCheckpointStore(RUN_ROOT / "checkpoints"))

# Change detection: only items the durable state has not already processed.
processed = set(state.load()["processed_ids"])
unseen = [item for item in source.fetch() if item.item_id not in processed]
print("Website root      :", SITE_ROOT)
print("Already processed :", sorted(processed) or "none")

if not unseen:
    print("Result            : no_change (nothing new to propose)")
    raise SystemExit(0)

item = unseen[0]
print("New item          :", item.item_id, "-", item.title)
config = website_agent_config()
result = runtime.run(config, item.item_id)
print("Run status        :", result.status)
for event in result.events:
    print("  event:", event["event"], event["details"].get("tool", ""),
          event["details"].get("decision", ""))

if result.status == "pending_approval":
    print("\nPaused before the external action:", result.pending_action["tool"])
    print("Dry run only. Review the proposal, then call")
    print(f'  runtime.resume("{result.run_id}", config, approved=True)')
    print("Website file exists:", (SITE_ROOT / "content" / "updates.md").exists())
