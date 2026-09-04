"""Derive the per-section lesson notebooks from each day's master notebook.

The day notebook (``day_0X_complete.ipynb``) is the source of truth. Each markdown cell
tagged ``master-section-start`` begins a section, and ``metadata.course.generated_from``
lists the section file names in order. The cells before the first section (API key,
setup, mock model) are prepended to section 1 so that lesson stays runnable on its own.
Boilerplate cells from the older concatenation pipeline are dropped.

The LangChain track (``langchain_track/langchain_complete.ipynb``) is split the same way;
its sections are headed ``## L3 — Title`` instead of ``## 1.3 — Title``.

Run after editing a day or track notebook:  py split_day_notebooks.py
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DAYS = [
    "day_01_model_tools_agent",
    "day_02_knowledge_and_state",
    "day_03_memory_and_safety",
    "day_04_multi_agent_systems",
    "day_05_ai_harness",
]
TRACKS = {"langchain_track": "langchain_complete.ipynb"}     # directory -> track notebook
SKIP_TAGS = {"master-notebook-introduction", "master-section-checkpoint", "master-notebook-completion"}


def tags(cell: dict) -> set[str]:
    return set(cell.get("metadata", {}).get("tags", []))


def text(cell: dict) -> str:
    source = cell.get("source", [])
    return "".join(source) if isinstance(source, list) else str(source)


def clean(cell: dict) -> dict:
    cloned = copy.deepcopy(cell)
    if cloned.get("cell_type") == "code":
        cloned["execution_count"] = None
        cloned["outputs"] = []
    return cloned


def promote_heading(cell: dict) -> dict:
    """Turn the master's '## 1.2 — Title' section heading back into a lesson H1."""
    cloned = clean(cell)
    body = re.sub(r'^<a id="[^"]+"></a>\s*', "", text(cloned))
    match = re.match(r"^##\s+(\d+)\.(\d+)\s+—\s+(.+?)\s*$", body, flags=re.MULTILINE)
    if match:
        day, number, title = match.groups()
        heading = title if re.match(r"^Day \d+ (Project|Capstone) — ", title) else f"Day {day}.{number} — {title}"
        body = body[: match.start()] + f"# {heading}" + body[match.end():]
    track_match = re.match(r"^##\s+L(\d+)\s+—\s+(.+?)\s*$", body, flags=re.MULTILINE)
    if track_match:
        number, title = track_match.groups()
        body = body[: track_match.start()] + f"# LangChain L{number} — {title}" + body[track_match.end():]
    cloned["source"] = body.splitlines(keepends=True)
    cloned.setdefault("metadata", {})["tags"] = sorted(tags(cloned) - {"master-section-start"})
    return cloned


def split_day(day_index: int, directory: str, master_file: str | None = None) -> list[str]:
    """Split one master notebook; day_index 0 marks a track rather than a course day."""
    day_dir = ROOT / directory
    master_path = day_dir / (master_file or f"day_{day_index:02d}_complete.ipynb")
    master = json.loads(master_path.read_text(encoding="utf-8"))
    files = master["metadata"]["course"]["generated_from"]
    cells = master["cells"]
    starts = [index for index, cell in enumerate(cells) if "master-section-start" in tags(cell)]
    if len(starts) != len(files):
        raise SystemExit(f"{master_path.name}: {len(starts)} section starts but {len(files)} section files listed")
    preamble = [clean(cell) for cell in cells[: starts[0]] if not tags(cell) & SKIP_TAGS]
    out_dir = day_dir / "notebooks"
    out_dir.mkdir(exist_ok=True)
    for number, (start, file_name) in enumerate(zip(starts, files), start=1):
        end = starts[number] if number < len(starts) else len(cells)
        section = [cell for cell in cells[start:end] if not tags(cell) & SKIP_TAGS]
        lesson_cells = (preamble if number == 1 else []) + [promote_heading(section[0])] + [clean(cell) for cell in section[1:]]
        notebook = {
            "cells": lesson_cells,
            "metadata": {
                "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                "language_info": {"name": "python", "version": "3.11"},
                "course": ({"track": master["metadata"]["course"].get("track", directory), "section": number, "derived_from": master_path.name, "source_of_truth": "track notebook"}
                           if master_file else
                           {"day": day_index, "section": number, "derived_from": master_path.name, "source_of_truth": "day notebook"}),
            },
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        (out_dir / file_name).write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    stale = sorted(path.name for path in out_dir.glob("*.ipynb") if path.name not in files)
    if stale:
        print(f"WARNING {directory}/notebooks has files not listed in the day notebook: {stale}")
    return files


def main() -> None:
    total = 0
    for index, directory in enumerate(DAYS, start=1):
        files = split_day(index, directory)
        total += len(files)
        print(f"{directory}: {len(files)} lesson notebooks derived")
    for directory, master_file in TRACKS.items():
        files = split_day(0, directory, master_file)
        total += len(files)
        print(f"{directory}: {len(files)} lesson notebooks derived")
    print(f"Derived {total} lesson notebooks from 5 day notebooks and {len(TRACKS)} track notebook(s).")


if __name__ == "__main__":
    main()
