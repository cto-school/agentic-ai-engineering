"""Instructor-provided local MCP server. Students consume it; writing it is optional."""
try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:
    raise SystemExit('Install the classroom-pinned MCP SDK first: pip install "mcp[cli]"') from exc

mcp=FastMCP("Synthetic Course Facts")

@mcp.tool()
def course_lookup(topic: str) -> dict:
    """Return a synthetic fact for the requested course topic."""
    facts={"harness":"A harness combines runtime, tools, policy, state, and events.",
           "mcp":"MCP standardizes capability discovery and invocation; it does not grant permission."}
    return {"topic":topic,"answer":facts.get(topic.lower(),"No supplied fact for that topic.")}

if __name__=="__main__": mcp.run()
