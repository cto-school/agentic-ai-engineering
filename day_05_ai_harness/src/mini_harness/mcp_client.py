"""MCP client seam: one offline fake plus one real stdio client.

The fake and the real SDK must be *shape compatible*, otherwise the lesson would
teach an access pattern that breaks the moment a real server is used.
"""
from __future__ import annotations
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class MCPToolDescription:
    """Same attribute names the real MCP SDK's ``Tool`` object uses.

    ``inputSchema`` is camelCase on purpose: that is what the protocol sends, so
    ``tool.inputSchema`` works identically against the fake and a real server.
    """
    name: str
    description: str
    inputSchema: dict[str, Any] = field(default_factory=dict)


class MCPClient(Protocol):
    async def list_tools(self) -> list[MCPToolDescription]: ...
    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any: ...


class FakeMCPClient:
    """Offline protocol-shaped fallback used by tests, outage labs and mock mode."""

    async def list_tools(self) -> list[MCPToolDescription]:
        return [
            MCPToolDescription(
                name="course_lookup",
                description="Look up a synthetic course fact",
                inputSchema={"type": "object",
                             "properties": {"topic": {"type": "string"}},
                             "required": ["topic"]},
            )
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]):
        if name != "course_lookup":
            raise KeyError(name)
        return {"topic": arguments["topic"], "answer": "Synthetic MCP response"}


def tool_result_payload(result: Any) -> Any:
    """Normalise a tool result from either client into a plain Python value.

    The fake returns a dict. The real SDK returns a ``CallToolResult`` holding a
    list of content blocks. One helper means notebooks use one access pattern.
    """
    if isinstance(result, (dict, list, str)) or result is None:
        return result
    structured = getattr(result, "structuredContent", None)
    if structured:
        return structured
    blocks = getattr(result, "content", None) or []
    texts = [getattr(block, "text", "") for block in blocks]
    joined = "\n".join(text for text in texts if text)
    try:
        return json.loads(joined)  # FastMCP servers usually return JSON text
    except (ValueError, TypeError):
        return joined


def run_in_fresh_event_loop(make_coroutine):
    """Run one async job in a dedicated thread that owns a brand-new event loop.

    A Jupyter kernel already owns an event loop, and on Windows that loop cannot
    start subprocesses - which is exactly what an stdio MCP server is. Handing the
    job to a worker thread with its own loop makes the real-server cell work in a
    notebook without any special launch flags.
    """
    import asyncio
    import concurrent.futures

    def worker():
        loop = asyncio.ProactorEventLoop() if sys.platform == "win32" else asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(make_coroutine())
        finally:
            asyncio.set_event_loop(None)
            loop.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(worker).result()


@dataclass
class StdioMCPClient:
    """Real MCP client over stdio. `command` should be sys.executable on Windows."""
    command: str
    args: list[str]

    async def list_and_optionally_call(self, name: str | None = None, arguments: dict | None = None):
        """One-session stable-SDK example; discovery never grants authorization."""
        import os
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        params = StdioServerParameters(command=self.command, args=self.args)
        # The SDK sends the server's stderr to `errlog`, and that needs a real
        # file descriptor. Inside Jupyter, sys.stderr has none, so we discard the
        # server's log output instead of crashing with UnsupportedOperation.
        with open(os.devnull, "w", encoding="utf-8") as server_log:
            async with stdio_client(params, errlog=server_log) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    result = await session.call_tool(name, arguments or {}) if name else None
                    return tools.tools, result

    def list_and_optionally_call_sync(self, name: str | None = None, arguments: dict | None = None):
        """Blocking version, safe to call from a notebook cell on any platform."""
        return run_in_fresh_event_loop(
            lambda: self.list_and_optionally_call(name, arguments))
