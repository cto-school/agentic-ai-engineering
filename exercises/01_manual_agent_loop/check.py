from exercise import run_agent


calls = []
def add(a, b):
    calls.append((a, b))
    return a + b


responses = iter([
    {"type": "tool", "name": "add", "arguments": {"a": 2, "b": 3}},
    {"type": "final", "text": "The result is 5."},
])


def model(messages):
    return next(responses)


history = [{"role": "user", "content": "Add 2 and 3"}]
assert run_agent(model, {"add": add}, history) == "The result is 5."
assert calls == [(2, 3)]
assert any(message.get("role") == "tool" for message in history)
print("PASS: bounded loop dispatched a tool and returned the final answer")

