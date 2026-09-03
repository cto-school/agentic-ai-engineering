"""Transparent Markdown loading and heading-aware chunking."""

from __future__ import annotations

import re
from pathlib import Path

from .schemas import DocumentChunk


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def chunk_markdown(path: Path) -> list[DocumentChunk]:
    """Create one small chunk per second-level Markdown section."""

    lines = path.read_text(encoding="utf-8").splitlines()
    title = path.stem.replace("_", " ").title()
    section = "Introduction"
    buffer: list[str] = []
    chunks: list[DocumentChunk] = []

    def flush() -> None:
        text = " ".join(line.strip() for line in buffer if line.strip()).strip()
        if not text:
            return
        chunks.append(
            DocumentChunk(
                chunk_id=f"{path.stem}:{_slug(section)}",
                source=path.name,
                title=title,
                section=section,
                text=text,
            )
        )

    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            flush()
            buffer = []
            section = line[3:].strip()
            continue
        buffer.append(line)
    flush()
    return chunks


def load_markdown_corpus(directory: str | Path) -> list[DocumentChunk]:
    root = Path(directory)
    chunks: list[DocumentChunk] = []
    for path in sorted(root.glob("*.md")):
        chunks.extend(chunk_markdown(path))
    if not chunks:
        raise ValueError(f"No Markdown documents found in {root}")
    return chunks

