from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class EventStore:
    def __init__(self, path: str | Path | None = None):
        self.path=Path(path) if path else None; self.by_run: dict[str,list[dict[str,Any]]]={}

    def add(self, run_id: str, event: str, **details: Any) -> dict[str,Any]:
        row={"run_id":run_id,"event":event,"timestamp":datetime.now(timezone.utc).isoformat(),"details":details}
        self.by_run.setdefault(run_id,[]).append(row)
        if self.path:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            with self.path.open("a",encoding="utf-8") as f: f.write(json.dumps(row)+"\n")
        return row

    def get(self, run_id: str) -> list[dict[str,Any]]: return list(self.by_run.get(run_id,[]))


class CheckpointStore:
    def __init__(self): self.items: dict[str,dict[str,Any]]={}
    def save(self, run_id: str, state: dict[str,Any]): self.items[run_id]=state
    def load(self, run_id: str): return self.items.get(run_id)
    def delete(self, run_id: str): self.items.pop(run_id,None)


class JSONCheckpointStore:
    """Small durable checkpoint store for restart/resume demonstrations."""
    def __init__(self,directory: str|Path): self.directory=Path(directory); self.directory.mkdir(parents=True,exist_ok=True)
    def _path(self,run_id): return self.directory/f"{run_id}.json"
    def save(self,run_id,state): self._path(run_id).write_text(json.dumps(state,indent=2),encoding="utf-8")
    def load(self,run_id):
        path=self._path(run_id); return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    def delete(self,run_id):
        path=self._path(run_id)
        if path.exists(): path.unlink()
