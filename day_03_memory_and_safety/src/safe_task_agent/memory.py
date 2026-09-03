from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .schemas import MemoryRecord


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SQLiteMemoryStore:
    """Small, inspectable memory store. Every operation is scoped by user_id."""

    def __init__(self, path: str | Path = ":memory:"):
        self.connection = sqlite3.connect(str(path))
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("""CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY, user_id TEXT NOT NULL, text TEXT NOT NULL,
            source TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")

    def add(self, user_id: str, text: str, source: str = "user_confirmed") -> MemoryRecord:
        stamp, memory_id = _now(), str(uuid4())
        self.connection.execute("INSERT INTO memories VALUES (?, ?, ?, ?, ?, ?)",
                                (memory_id, user_id, text, source, stamp, stamp))
        self.connection.commit()
        return self.get(user_id, memory_id)

    def get(self, user_id: str, memory_id: str) -> MemoryRecord | None:
        row = self.connection.execute(
            "SELECT * FROM memories WHERE user_id=? AND id=?", (user_id, memory_id)).fetchone()
        return MemoryRecord(**dict(row)) if row else None

    def all(self, user_id: str) -> list[MemoryRecord]:
        rows = self.connection.execute(
            "SELECT * FROM memories WHERE user_id=? ORDER BY updated_at DESC", (user_id,)).fetchall()
        return [MemoryRecord(**dict(row)) for row in rows]

    def search(self, user_id: str, query: str, limit: int = 3) -> list[MemoryRecord]:
        words = {w.lower().strip(".,!?") for w in query.split() if len(w) > 2}
        ranked = []
        for memory in self.all(user_id):
            memory_words = {w.lower().strip(".,!?") for w in memory.text.split()}
            # Tiny plural-tolerant matcher: deliberately inspectable, not an embedding model.
            score = sum(any(q == m or q.startswith(m) or m.startswith(q)
                            for m in memory_words) for q in words)
            if score:
                ranked.append((score, memory))
        return [m for _, m in sorted(ranked, key=lambda item: item[0], reverse=True)[:limit]]

    def update(self, user_id: str, memory_id: str, text: str) -> MemoryRecord | None:
        self.connection.execute(
            "UPDATE memories SET text=?, updated_at=? WHERE user_id=? AND id=?",
            (text, _now(), user_id, memory_id))
        self.connection.commit()
        return self.get(user_id, memory_id)

    def delete(self, user_id: str, memory_id: str) -> bool:
        cursor = self.connection.execute(
            "DELETE FROM memories WHERE user_id=? AND id=?", (user_id, memory_id))
        self.connection.commit()
        return cursor.rowcount == 1
