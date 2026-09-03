"""Optional LangGraph form of the already-understood manual loop.

LangGraph is imported inside the factory so mock/manual lessons can run before
students install it.
"""

from __future__ import annotations

from typing import TypedDict

from .providers import ModelProvider
from .schemas import Message, ResearchResponse
from .tools import Tool


class GraphState(TypedDict):
    messages: list[Message]
    steps: int
    max_steps: int
    final_response: ResearchResponse | None
    error: str | None


def build_graph(provider: ModelProvider, tools: dict[str, Tool]):
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise RuntimeError("Install langgraph to run the Day 1 graph example") from exc

    def call_model(state: GraphState) -> dict:
        turn = provider.complete(
            state["messages"], [tool.definition for tool in tools.values()]
        )
        message = Message(role="assistant", content=turn.content, tool_calls=turn.tool_calls)
        update: dict = {
            "messages": [*state["messages"], message],
            "steps": state["steps"] + 1,
        }
        if not turn.tool_calls:
            try:
                update["final_response"] = ResearchResponse.model_validate_json(turn.content)
            except Exception as exc:
                update["error"] = f"Final response failed validation: {exc}"
        return update

    def route_after_model(state: GraphState) -> str:
        if state["error"] or state["final_response"]:
            return "end"
        if state["steps"] >= state["max_steps"]:
            return "limit"
        return "tools" if state["messages"][-1].tool_calls else "end"

    def run_tools(state: GraphState) -> dict:
        new_messages = list(state["messages"])
        for call in state["messages"][-1].tool_calls:
            tool = tools.get(call.name)
            output = (
                tool.execute(call.id, call.arguments).output
                if tool
                else f"Tool error: unknown tool '{call.name}'"
            )
            new_messages.append(
                Message(role="tool", name=call.name, tool_call_id=call.id, content=output)
            )
        return {"messages": new_messages}

    def hit_limit(state: GraphState) -> dict:
        return {"error": f"Agent stopped after {state['max_steps']} steps"}

    builder = StateGraph(GraphState)
    builder.add_node("model", call_model)
    builder.add_node("tools", run_tools)
    builder.add_node("limit", hit_limit)
    builder.add_edge(START, "model")
    builder.add_conditional_edges(
        "model", route_after_model, {"tools": "tools", "limit": "limit", "end": END}
    )
    builder.add_edge("tools", "model")
    builder.add_edge("limit", END)
    return builder.compile()

