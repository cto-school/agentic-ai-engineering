from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .schemas import Event


class EventRecorder:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else None
        self.events: list[Event] = []

    def record(self, event: str, **details: Any) -> Event:
        item = Event(event, datetime.now(timezone.utc).isoformat(), details)
        self.events.append(item)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(item.as_dict()) + "\n")
        return item

