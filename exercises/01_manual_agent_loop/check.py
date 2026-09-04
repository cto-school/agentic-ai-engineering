from exercise import run_agent


calls = []
def add(a, b):
    calls.append((a, b))
    return a + b


# Case 1: one tool request, then a final answer.
responses = iter([
    {"type": "tool", "name": "add", "arguments": {"a": 2, "b": 3}},
    {"type": "final", "text": "The result is 5."},
])
history = [{"role": "user", "content": "Add 2 and 3"}]
assert run_agent(lambda messages: next(responses), {"add": add}, history) == "The result is 5."
assert calls == [(2, 3)], "the tool must run exactly once with the model's arguments"
assert any(message.get("role") == "tool" for message in history), "the tool result must be appended"

# Case 2: an unknown tool must be rejected before anything runs.
bad = iter([{"type": "tool", "name": "delete_everything", "arguments": {}}])
try:
    run_agent(lambda messages: next(bad), {"add": add}, [{"role": "user", "content": "x"}])
except ValueError:
    pass
else:
    raise AssertionError("an unknown tool name must raise ValueError")

# Case 3: a model that never answers must be stopped by the step limit.
forever = lambda messages: {"type": "tool", "name": "add", "arguments": {"a": 1, "b": 1}}
try:
    run_agent(forever, {"add": add}, [{"role": "user", "content": "x"}], max_steps=3)
except RuntimeError:
    pass
else:
    raise AssertionError("the loop must raise RuntimeError after max_steps")

print("PASS: dispatch, unknown-tool rejection, and step limit all behave correctly")
