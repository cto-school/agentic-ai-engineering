from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable
from .schemas import ToolSpec


@dataclass
class RegisteredTool:
    spec: ToolSpec
    function: Callable[..., Any]


class ToolRegistry:
    def __init__(self): self._tools: dict[str, RegisteredTool] = {}

    def register(self, spec: ToolSpec, function: Callable[..., Any]) -> None:
        if spec.name in self._tools: raise ValueError(f"Duplicate tool: {spec.name}")
        self._tools[spec.name] = RegisteredTool(spec, function)

    def discover(self, allowed: list[str] | None = None) -> list[ToolSpec]:
        names = set(allowed) if allowed is not None else set(self._tools)
        return [tool.spec for name, tool in self._tools.items() if name in names]

    def get(self, name: str) -> RegisteredTool:
        if name not in self._tools: raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def validate(self, name: str, arguments: dict[str, Any]) -> None:
        schema = self.get(name).spec.input_schema
        required = schema.get("required", [])
        missing = [key for key in required if key not in arguments]
        if missing: raise ValueError(f"Missing required arguments: {missing}")
        expected = {"string":str,"integer":int,"number":(int,float),"boolean":bool,"array":list,"object":dict}
        for key, value in arguments.items():
            prop = schema.get("properties", {}).get(key)
            if prop is None and schema.get("additionalProperties") is False:
                raise ValueError(f"Unexpected argument: {key}")
            if prop and prop.get("type") in expected and not isinstance(value, expected[prop["type"]]):
                raise TypeError(f"{key} must be {prop['type']}")

    def call(self, name: str, arguments: dict[str, Any]) -> Any:
        self.validate(name, arguments)
        return self.get(name).function(**arguments)

