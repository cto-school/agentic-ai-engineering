from exercise import ToolRegistry


registry = ToolRegistry()
registry.register(
    "add",
    {"name": "add", "parameters": {"a": "number", "b": "number"}},
    lambda a, b: a + b,
    "math.read",
)
assert len(registry.schemas_for({"math.read"})) == 1
assert registry.schemas_for(set()) == []
assert registry.dispatch("add", {"a": 4, "b": 5}, {"math.read"}) == 9

for label, call, expected in [
    ("ungranted dispatch", lambda: registry.dispatch("add", {"a": 1, "b": 1}, set()), PermissionError),
    ("unknown tool", lambda: registry.dispatch("nope", {}, {"math.read"}), KeyError),
    ("duplicate registration", lambda: registry.register("add", {}, lambda: None, "math.read"), ValueError),
]:
    try:
        call()
    except expected:
        pass
    else:
        raise AssertionError(f"{label} must raise {expected.__name__}")
print("PASS: registry centralizes discovery, dispatch, and capability checks")
