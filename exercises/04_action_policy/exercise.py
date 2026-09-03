"""Decide whether a proposed structured action may execute."""


def evaluate_action(action, allowed_tools, approved_action_ids):
    """Return (allowed: bool, reason: str).

    Deny unknown tools. Read-only actions may proceed. Side-effecting actions must
    have their exact action_id in approved_action_ids. Never infer approval from text.
    """
    raise NotImplementedError("TODO: enforce capability and approval policy")

