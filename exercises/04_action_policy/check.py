from exercise import evaluate_action


allowed = {"search": {"side_effect": False}, "send_email": {"side_effect": True}}
assert evaluate_action({"action_id": "a1", "tool": "search"}, allowed, set())[0]
assert not evaluate_action({"action_id": "a2", "tool": "send_email"}, allowed, set())[0]
assert evaluate_action({"action_id": "a2", "tool": "send_email"}, allowed, {"a2"})[0]
assert not evaluate_action({"action_id": "a3", "tool": "delete_all"}, allowed, {"a3"})[0]
print("PASS: capability and exact-action approval are enforced")

