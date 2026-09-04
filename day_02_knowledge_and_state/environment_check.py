"""Read-only Day 2 environment and data check.

    python environment_check.py                      # what mock mode needs
    DAY2_MODE=classroom python environment_check.py  # also checks the classroom extras

Nothing here writes files or calls a network service.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    mode = os.getenv("DAY2_MODE", "mock").lower()
    corpus = sorted((ROOT / "data" / "corpus").glob("*.md"))
    golden = json.loads((ROOT / "data" / "golden_set.json").read_text(encoding="utf-8"))
    checks = {
        "Python >= 3.10": sys.version_info >= (3, 10),
        "valid DAY2_MODE": mode in {"mock", "classroom"},
        "Pydantic installed": importlib.util.find_spec("pydantic") is not None,
        "python-dotenv installed": importlib.util.find_spec("dotenv") is not None,
        "Sentence Transformers (classroom)": importlib.util.find_spec("sentence_transformers") is not None,
        "Chroma (classroom)": importlib.util.find_spec("chromadb") is not None,
        "OpenRouter key (classroom)": bool(os.getenv("OPENROUTER_API_KEY")),
        "three corpus documents": len(corpus) == 3,
        "ten golden cases": len(golden) == 10,
    }
    failed = False
    print(f"DAY2_MODE={mode}")
    for label, passed in checks.items():
        classroom_only = "(classroom)" in label
        required = not classroom_only or mode == "classroom"
        status = "PASS" if passed else ("OPTIONAL" if not required else "FAIL")
        failed = failed or (required and not passed)
        print(f"[{status:8}] {label}")
    print("\nOPTIONAL lines are fine: mock mode runs every notebook without them.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
