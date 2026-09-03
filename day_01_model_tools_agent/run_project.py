"""Run the Day 1 reference project from the command line."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from research_agent import AgentRunner, default_tool_registry  # noqa: E402
from research_agent.providers import provider_from_environment  # noqa: E402


def load_simple_env(path: Path) -> None:
    """Load simple KEY=VALUE lines without requiring python-dotenv."""

    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    load_simple_env(PROJECT_ROOT.parent / ".env")
    question = " ".join(sys.argv[1:]) or "Explain an AI agent and calculate 12 * 7."
    runner = AgentRunner(provider_from_environment(), default_tool_registry(), max_steps=5)
    result = runner.run(question)
    print(result.model_dump_json(indent=2))
    return 0 if result.status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

