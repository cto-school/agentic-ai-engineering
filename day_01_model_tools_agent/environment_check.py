"""Check the minimum Day 1 environment without modifying it."""

from __future__ import annotations

import importlib.util
import os
import shutil
import sys


def main() -> int:
    mode = os.getenv("MODEL_MODE", "mock").lower()
    checks = {
        "Python >= 3.11": sys.version_info >= (3, 11),
        "pydantic installed": importlib.util.find_spec("pydantic") is not None,
        "valid MODEL_MODE": mode in {"mock", "local", "api"},
        "OpenRouter key (needed only for api mode)": bool(os.getenv("OPENROUTER_API_KEY")),
        "Ollama command (needed only for local mode)": shutil.which("ollama") is not None,
        "LangGraph installed (needed for notebook 06)": importlib.util.find_spec("langgraph") is not None,
    }
    print(f"MODEL_MODE={mode}")
    for label, passed in checks.items():
        required_now = not not_required(label, mode)
        status = "PASS" if passed else ("OPTIONAL" if not required_now else "FAIL")
        print(f"[{status:8}] {label}")
    return 0 if all(value or not_required(label, mode) for label, value in checks.items()) else 1


def not_required(label: str, mode: str) -> bool:
    return (
        (label.startswith("Ollama") and mode != "local")
        or (label.startswith("OpenRouter") and mode != "api")
        or label.startswith("LangGraph")
    )


if __name__ == "__main__":
    raise SystemExit(main())
