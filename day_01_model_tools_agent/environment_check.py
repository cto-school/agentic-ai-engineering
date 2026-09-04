"""Check the minimum Day 1 environment without modifying it."""

from __future__ import annotations

import importlib.util
import os
import shutil
import sys

# The course is developed and taught on Python 3.10+. Nothing in Day 1 uses a
# 3.11-only feature, so 3.10 is the real floor.
MINIMUM_PYTHON = (3, 10)


def main() -> int:
    mode = os.getenv("MODEL_MODE", "mock").lower()
    checks = {
        f"Python >= {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]}": sys.version_info >= MINIMUM_PYTHON,
        "pydantic installed": importlib.util.find_spec("pydantic") is not None,
        "valid MODEL_MODE": mode in {"mock", "local", "api"},
        "OpenRouter key (needed only for api mode)": bool(os.getenv("OPENROUTER_API_KEY")),
        "Ollama command (needed only for local mode)": shutil.which("ollama") is not None,
        "LangGraph installed (needed only for notebook 06)": importlib.util.find_spec("langgraph")
        is not None,
    }
    print(f"MODEL_MODE={mode}")
    print(f"Python     ={sys.version.split()[0]}")
    for label, passed in checks.items():
        optional = not_required(label, mode)
        status = "PASS" if passed else ("OPTIONAL" if optional else "FAIL")
        print(f"[{status:8}] {label}")

    # A missing optional package is a warning, never a failure: notebooks 01-05 and 07
    # run without it and notebook 06 prints an install hint instead of raising.
    if not checks["LangGraph installed (needed only for notebook 06)"]:
        print("WARNING: langgraph is not installed. Notebook 06 will skip its graph cells.")
        print("         Install it with: pip install langgraph")

    return 0 if all(value or not_required(label, mode) for label, value in checks.items()) else 1


def not_required(label: str, mode: str) -> bool:
    return (
        (label.startswith("Ollama") and mode != "local")
        or (label.startswith("OpenRouter") and mode != "api")
        or label.startswith("LangGraph")
    )


if __name__ == "__main__":
    raise SystemExit(main())
