from exercise import run_agent


def reply(content="", calls=None):
    return {"content": content, "tool_calls": calls or []}


def scripted(*replies):
    queue = iter(replies)
    return lambda messages, tools: next(queue)


calls = []
def add(a, b):
    calls.append((a, b))
    return str(a + b)


# Case 1: one tool request, then a final answer.
model = scripted(reply(calls=[{"id": "c1", "name": "add", "arguments": {"a": 2, "b": 3}}]),
                 reply("The result is 5."))
result = run_agent("Add 2 and 3", {"add": add}, model)
assert result["status"] == "completed" and result["answer"] == "The result is 5.", result
assert calls == [(2, 3)], "the tool must run exactly once with the model's arguments"
assert any(message["role"] == "tool" for message in result["messages"]), "the tool result must be appended"

# Case 2: an unknown tool is rejected before anything runs.
model = scripted(reply(calls=[{"id": "c2", "name": "delete_everything", "arguments": {}}]))
assert run_agent("x", {"add": add}, model)["status"] == "failed"

# Case 3: a model that never answers hits the step limit.
forever = lambda messages, tools: reply(calls=[{"id": f"c{len(messages)}", "name": "add",
                                                "arguments": {"a": len(messages), "b": 1}}])
assert run_agent("x", {"add": add}, forever, max_steps=3)["status"] == "max_steps"

# Case 4: the same request twice means a stuck model.
stuck = lambda messages, tools: reply(calls=[{"id": "same", "name": "add", "arguments": {"a": 1, "b": 1}}])
assert run_agent("x", {"add": add}, stuck)["status"] == "failed"

print("PASS: dispatch, unknown-tool rejection, the step limit, and duplicate detection all behave correctly")
