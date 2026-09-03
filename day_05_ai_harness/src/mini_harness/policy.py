from .schemas import AgentConfig, ToolSpec


def decide(config: AgentConfig, tool: ToolSpec) -> str:
    if tool.name not in config.allowed_tools: return "deny"
    return {"read":"allow", "write":"allow", "external":"approval", "destructive":"deny"}[tool.risk]

