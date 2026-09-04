"""Local permission decisions. Python decides, never the model."""
from .schemas import AgentConfig, ToolSpec

# The one place risk levels are turned into permission decisions.
RISK_POLICY: dict[str, str] = {
    "read": "allow",           # no side effect outside the process
    "write": "allow",          # reversible local change
    "external": "approval",    # leaves the machine or is visible to others -> pause for a human
    "destructive": "deny",     # never automatic in this course
}

# Returned for any risk label we do not recognise. Failing *closed* means an
# unknown or misspelled risk level can never accidentally grant permission.
UNKNOWN_RISK_DECISION = "deny"


def decide(config: AgentConfig, tool: ToolSpec) -> str:
    """Return 'allow', 'approval' or 'deny' for this agent calling this tool."""
    if tool.name not in config.allowed_tools:
        return "deny"  # not on this agent's allow-list, whatever its risk is
    # .get(...) rather than [...]: an unknown risk label denies instead of raising KeyError.
    return RISK_POLICY.get(tool.risk, UNKNOWN_RISK_DECISION)
