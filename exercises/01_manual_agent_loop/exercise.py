"""Complete the bounded manual agent loop. No SDK is required.

Mirror of Day 1 section 1.5. The notebook version also validates arguments with
Pydantic; this mirror keeps only the loop so the check stays dependency-free.
"""


def run_agent(question, tools, model, max_steps=5):
    """Return {"status", "answer", "messages", "steps", "tools_used", "error"}.

    model(messages, tools) returns {"content": str, "tool_calls": [{"id", "name", "arguments"}]}.
    tools is {name: python_function}.
    Rules: append the assistant reply and every tool result to messages; stop with status
    "completed" on a reply without tool calls; return "failed" for an unknown tool or a
    repeated identical request; return "max_steps" when the limit is reached.
    """
    raise NotImplementedError("TODO: implement observe-dispatch-append-terminate")
