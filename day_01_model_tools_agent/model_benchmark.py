"""Run the compact Day 1 behavior suite against the configured model route.

This prints JSON Lines so results can later be compared without adding a data
analysis dependency. It makes real model/API calls when MODEL_MODE is local or
api, so students should use mock mode unless instructed otherwise.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from research_agent.agent import AgentRunner  # noqa: E402
from research_agent.providers import provider_from_environment  # noqa: E402
from research_agent.tools import default_tool_registry  # noqa: E402


CASES = [
    {"id": "direct", "question": "Summarize why clear instructions matter."},
    {"id": "calculator", "question": "Calculate 12 * 7."},
    {"id": "local_search", "question": "Explain what an AI agent is."},
    {
        "id": "two_tools",
        "question": "Explain an AI agent and calculate 12 * 7.",
    },
    {
        "id": "unknown",
        "question": "What does the local course note say about quantum gardening?",
    },
]


def main() -> int:
    runner = AgentRunner(provider_from_environment(), default_tool_registry(), max_steps=5)
    mode = os.getenv("MODEL_MODE", "mock")
    failures = 0
    for case in CASES:
        started = time.perf_counter()
        result = runner.run(case["question"])
        elapsed = round(time.perf_counter() - started, 3)
        if result.status != "completed":
            failures += 1
        print(
            json.dumps(
                {
                    "case": case["id"],
                    "mode": mode,
                    "status": result.status,
                    "steps": result.steps,
                    "tools_used": result.response.tools_used if result.response else [],
                    "schema_valid": result.response is not None,
                    "prompt_tokens": result.usage.prompt_tokens,
                    "completion_tokens": result.usage.completion_tokens,
                    "reasoning_tokens": result.usage.reasoning_tokens,
                    "cost_usd": round(result.usage.cost_usd, 6),
                    "elapsed_seconds": elapsed,
                    "error": result.error,
                }
            )
        )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
