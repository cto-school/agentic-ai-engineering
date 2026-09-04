"""Build one classroom-facing Colab notebook per day from the modular lessons.

The smaller notebooks remain the maintainable source of truth. This generator gives
students a single, ordered notebook for each six-hour project day without duplicating
hand-maintained teaching content.
"""

from __future__ import annotations

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
    return cloned


def build_day(day_index: int, directory: str, day_title: str, project: str) -> Path:
    notebook_dir = ROOT / directory / "notebooks"
    source_files = sorted(notebook_dir.glob("*.ipynb"))
    sources = [(path, json.loads(path.read_text(encoding="utf-8"))) for path in source_files]
    titles = [lesson_title(notebook, path.name) for path, notebook in sources]
    toc = "\n".join(
        f"{number}. [{short_title(title)}](#day-{day_index}-section-{number})"
        for number, title in enumerate(titles, start=1)
    )
    intro = f"""# Day {day_index} — {day_title}

## Daily project: {project}

This is the classroom master notebook for Day {day_index}. Work from top to bottom: each section introduces one limitation, adds one system layer, and carries that improvement into the daily project.

### How to use this notebook

- Run the environment check and setup cells before beginning.
- Complete sections in order during class; optional provider comparisons are clearly marked.
- If Colab restarts, rerun the current section's import/setup cell before continuing.
- At each checkpoint, explain the observable change before moving forward.
- Use mock or cached mode first. Use the instructor-issued OpenRouter credit only for bounded live observations.

### Day {day_index} contents

{toc}

---
"""
    cells = [markdown_cell(intro, "master-notebook-introduction")]
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
        "- [ ] I completed the pivotal exercise without copying the reference implementation.\n"
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
