"""Build one classroom-facing Colab notebook per day from the modular lessons.

The smaller notebooks remain the maintainable source of truth. This generator gives
students a single, ordered notebook for each six-hour project day without duplicating
hand-maintained teaching content.
"""
from __future__ import annotations

import sys as _sys
if "--force" not in _sys.argv:  # pragma: no cover
    raise SystemExit(
        "ARCHIVED: the day notebooks (day_0X_complete.ipynb) are now the source of truth and the "
        "lesson notebooks are derived from them by split_day_notebooks.py. This generator worked in "
        "the opposite direction and would overwrite the day notebooks. Run with --force only if you mean it."
    )


import copy
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DAY_CONFIG = [
    ("day_01_model_tools_agent", "From Model to Agent", "Smart Research Assistant"),
    ("day_02_knowledge_and_state", "Knowledge and State", "Engineering Knowledge Assistant"),
    ("day_03_memory_and_safety", "Memory, Planning, and Safety", "Safe Personal Task Agent"),
    ("day_04_multi_agent_systems", "Multi-Agent Systems and Evaluation", "Engineering Design Review Team"),
    ("day_05_ai_harness", "AI Harness and Automation", "Mini AI Harness + Website Maintenance Agent"),
]


def source_text(cell: dict) -> str:
    source = cell.get("source", [])
    return "".join(source) if isinstance(source, list) else str(source)


def markdown_cell(text: str, *tags: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {"tags": list(tags)} if tags else {},
        "source": text.splitlines(keepends=True),
    }


def lesson_title(notebook: dict, fallback: str) -> str:
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        match = re.search(r"^#\s+(.+)$", source_text(cell), flags=re.MULTILINE)
        if match:
            return match.group(1).strip().replace("**", "").replace("`", "")
    return fallback.replace(".ipynb", "").replace("_", " ").title()


def short_title(title: str) -> str:
    return re.sub(r"^(?:Day\s+\d+(?:\.\d+)?|Pivotal Exercise)\s*(?:—|-)\s*", "", title)


def demote_opening_heading(cell: dict, day_number: int, lesson_number: int) -> dict:
    cloned = copy.deepcopy(cell)
    text = source_text(cloned)
    title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else f"Lesson {day_number}.{lesson_number}"
    title = short_title(title)
    remainder = re.sub(r"^#\s+.+\r?\n?", "", text, count=1).lstrip()
    anchor = f"day-{day_number}-section-{lesson_number}"
    rebuilt = f'<a id="{anchor}"></a>\n\n## {day_number}.{lesson_number} — {title}\n\n{remainder}'.rstrip() + "\n"
    cloned["source"] = rebuilt.splitlines(keepends=True)
    cloned.setdefault("metadata", {}).setdefault("tags", []).append("master-section-start")
    return cloned


def clean_cell(cell: dict) -> dict:
    cloned = copy.deepcopy(cell)
    if cloned.get("cell_type") == "code":
        cloned["execution_count"] = None
        cloned["outputs"] = []
    elif cloned.get("cell_type") == "markdown":
        # Lesson notebooks live in <day>/notebooks/; the master lives one level up in <day>/.
        # Relative links such as ../../diagrams/... therefore lose one "../" in the master.
        cloned["source"] = source_text(cloned).replace("](../../", "](../").splitlines(keepends=True)
    return cloned


REQUIREMENTS_BY_DAY = {
    2: "setup/requirements-day2.txt",
    5: "setup/requirements-day5.txt",
}


def bootstrap_cell(day_index: int, directory: str) -> dict:
    """Colab clone/install + API-key entry. Harmless on a local machine."""
    extra = REQUIREMENTS_BY_DAY.get(day_index)
    extra_install = (
        f'        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(REPO_DIR / "{extra}")], check=True)\n'
        if extra else ""
    )
    source = f'''# --- Environment setup: run this cell first (Colab or local) -------------------------
import os, sys, subprocess
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
REPO_URL = "https://github.com/cto-school/agentic-ai-engineering.git"   # the public course repository
REPO_DIR = Path("/content/agentic-ai-engineering")

if IN_COLAB:
    if not REPO_DIR.exists():
        print("Cloning the course repository ...")
        subprocess.run(["git", "clone", "--depth", "1", REPO_URL, str(REPO_DIR)], check=True)
        print("Installing requirements (this takes a minute) ...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", str(REPO_DIR / "setup/requirements-core.txt")], check=True)
{extra_install}    os.chdir(REPO_DIR / "{directory}")
    # Colab has no .env file. Paste the key you were issued; it is kept only in this runtime.
    from getpass import getpass
    if not os.getenv("OPENROUTER_API_KEY"):
        key = getpass("OPENROUTER_API_KEY (press Enter to stay in mock mode): ").strip()
        if key:
            os.environ["OPENROUTER_API_KEY"] = key
else:
    # Local machine: the key is read from the .env file at the repository root
    # (Day 1.1 explains how to create it from .env.example).
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(usecwd=True))

print("Working directory:", os.getcwd())
print("Mode:", "LIVE (OpenRouter key found)" if os.getenv("OPENROUTER_API_KEY") else "MOCK (no key found: deterministic answers, no credit spent)")
'''
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"tags": ["master-bootstrap"]},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def build_day(day_index: int, directory: str, day_title: str, project: str) -> Path:
    notebook_dir = ROOT / directory / "notebooks"
    source_files = sorted(notebook_dir.glob("*.ipynb"))
    sources = [(path, json.loads(path.read_text(encoding="utf-8"))) for path in source_files]
    titles = [lesson_title(notebook, path.name) for path, notebook in sources]
    toc = "\n".join(
        f"{number}. [{short_title(title)}](#day-{day_index}-section-{number})"
        for number, title in enumerate(titles, start=1)
    )
    exercise_positions = [number for number, (path, _) in enumerate(sources, start=1) if "_exercise_" in path.name]
    exercise_number = str(exercise_positions[0]) if exercise_positions else "?"
    intro = f"""# Day {day_index} — {day_title}

## Daily project: {project}

This is the classroom master notebook for Day {day_index}. Work from top to bottom: each section introduces one limitation, adds one system layer, and carries that improvement into the daily project.

### How to use this notebook

- Run the **Environment setup** cell directly below first. On Google Colab it clones the repository, installs packages, and asks for your API key. On your own computer it only loads the `.env` file.
- Every section starts with a small setup cell of its own; if the kernel restarts, rerun that cell and continue.
- Run the code cells in order and read the printed output: each cell prints what changed and why.
- Every lesson ends with a short **Checkpoint** (answers are folded under *Show answer*) and a **Recap**.
- Without an API key everything runs in deterministic **mock** mode and spends no credit. Use the instructor-issued OpenRouter key only for the marked live observations.
- Section {day_index}.{exercise_number} is the day's single hands-on exercise; a commented reference solution follows its check.

### Day {day_index} contents

{toc}

---
"""
    cells = [markdown_cell(intro, "master-notebook-introduction"), bootstrap_cell(day_index, directory)]
    for lesson_number, (_, notebook) in enumerate(sources, start=1):
        lesson_cells = notebook.get("cells", [])
        for cell_index, cell in enumerate(lesson_cells):
            cells.append(demote_opening_heading(cell, day_index, lesson_number) if cell_index == 0 and cell.get("cell_type") == "markdown" else clean_cell(cell))
        cells.append(markdown_cell(
            f"---\n\n### Section {day_index}.{lesson_number} checkpoint\n\n"
            "Before continuing, confirm that you can state: **what limitation we observed, what layer we added, and what evidence shows the improvement worked.**\n",
            "master-section-checkpoint",
        ))
    cells.append(markdown_cell(
        f"## Day {day_index} completion checklist\n\n"
        f"- [ ] I can explain how every section contributes to the **{project}**.\n"
        "- [ ] I ran the deterministic path and at least one required live observation or classroom fallback.\n"
        "- [ ] I attempted the pivotal exercise before reading its reference solution, and I can explain the solution line by line.\n"
        "- [ ] I can identify the system state, safety boundary, and evidence used to judge the result.\n",
        "master-notebook-completion",
    ))
    metadata = copy.deepcopy(sources[0][1].get("metadata", {})) if sources else {}
    metadata["course"] = {
        "day": day_index,
        "title": day_title,
        "project": project,
        "generated_from": [path.name for path, _ in sources],
        "source_of_truth": "modular notebooks",
    }
    master = {"cells": cells, "metadata": metadata, "nbformat": 4, "nbformat_minor": 5}
    destination = ROOT / directory / f"day_{day_index:02d}_complete.ipynb"
    destination.write_text(json.dumps(master, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    outputs = [build_day(index, *config) for index, config in enumerate(DAY_CONFIG, start=1)]
    print("Built master notebooks:")
    for output in outputs:
        print(f" - {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
