"""Reference run of the mini harness in MOCK mode. No API key, no credit spent."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from mini_harness import (  # noqa: E402
    AgentConfig, HarnessRuntime, MAX_STEPS_HARD_CAP, ModelConfig, MockModel,
    build_demo_registry, effective_step_limit,
)


def load(name: str) -> AgentConfig:
    raw = json.loads((ROOT / "configs" / f"{name}.json").read_text(encoding="utf-8"))
    raw["model"] = ModelConfig(**raw["model"])
    return AgentConfig(**raw)


runtime = HarnessRuntime(build_demo_registry(), MockModel())
print("Hard step cap in the runtime:", MAX_STEPS_HARD_CAP)

for name, prompt in [("research_agent", "What is a harness?"),
                     ("task_agent", "Prepare a project update")]:
    config = load(name)
    print(f"\n=== {name} (requested max_steps={config.max_steps}, "
          f"effective limit={effective_step_limit(config)}) ===")
    result = runtime.run(config, prompt)
    print("status :", result.status)
    print("output :", result.output)
    for event in result.events:
        print("  event:", event["event"], event["details"])

task = load("task_agent")
print("\n=== approval path ===")
pending = runtime.run(task, "Send a synthetic course update")
print("status         :", pending.status)
print("pending action :", pending.pending_action["tool"], pending.pending_action["arguments"])
resumed = runtime.resume(pending.run_id, task, approved=True)
print("after approval :", resumed.status, resumed.output)
