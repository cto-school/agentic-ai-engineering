from exercise import evaluate_action


allowed = {"search": {"side_effect": False}, "send_email": {"side_effect": True}}
cases = [
    ({"action_id": "a1", "tool": "search"},     set(),  True,  "read-only tool runs without approval"),
    ({"action_id": "a2", "tool": "send_email"}, set(),  False, "side effect without approval is blocked"),
    ({"action_id": "a2", "tool": "send_email"}, {"a2"}, True,  "side effect with exact approval runs"),
    ({"action_id": "a2", "tool": "send_email"}, {"a9"}, False, "approval for a different action id does not transfer"),
    ({"action_id": "a3", "tool": "delete_all"}, {"a3"}, False, "unknown tool is denied even if 'approved'"),
]
for action, approvals, expected, label in cases:
    allowed_flag, _reason = evaluate_action(action, allowed, approvals)
    assert allowed_flag == expected, label
print("PASS: capability and exact-action approval are enforced")
