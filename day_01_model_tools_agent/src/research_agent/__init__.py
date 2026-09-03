"""Reference implementation for the Day 1 research agent."""

from .agent import AgentRunner
from .providers import MockModelProvider, OllamaProvider, OpenRouterProvider
from .tools import default_tool_registry

__all__ = [
    "AgentRunner",
    "MockModelProvider",
    "OllamaProvider",
    "OpenRouterProvider",
    "default_tool_registry",
]

