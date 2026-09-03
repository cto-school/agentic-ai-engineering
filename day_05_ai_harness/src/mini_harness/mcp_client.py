from __future__ import annotations
from dataclasses import dataclass
from typing import Any,Protocol


class MCPClient(Protocol):
    async def list_tools(self) -> list[dict[str,Any]]: ...
    async def call_tool(self,name: str,arguments: dict[str,Any]) -> Any: ...


class FakeMCPClient:
    """Offline protocol-shaped fallback used by tests and outage labs."""
    async def list_tools(self):
        return [{"name":"course_lookup","description":"Look up a synthetic course fact",
                 "inputSchema":{"type":"object","properties":{"topic":{"type":"string"}},"required":["topic"]}}]
    async def call_tool(self,name,arguments):
        if name!="course_lookup": raise KeyError(name)
        return {"topic":arguments["topic"],"answer":"Synthetic MCP response"}


@dataclass
class StdioMCPClient:
    command: str
    args: list[str]

    async def list_and_optionally_call(self,name: str|None=None,arguments: dict|None=None):
        """One-session stable-SDK example; discovery never grants authorization."""
        from mcp import ClientSession,StdioServerParameters
        from mcp.client.stdio import stdio_client
        params=StdioServerParameters(command=self.command,args=self.args)
        async with stdio_client(params) as (read,write):
            async with ClientSession(read,write) as session:
                await session.initialize()
                tools=await session.list_tools()
                result=await session.call_tool(name,arguments or {}) if name else None
                return tools.tools,result
