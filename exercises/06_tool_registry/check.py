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
try:
    registry.dispatch("add", {"a": 1, "b": 1}, set())
except PermissionError:
    pass
else:
    raise AssertionError("dispatch should reject an ungranted capability")
print("PASS: registry centralizes discovery, dispatch, and capability checks")

