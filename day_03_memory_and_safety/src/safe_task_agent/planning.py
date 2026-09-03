from .schemas import PlanStep


def make_plan(goal: str, max_steps: int = 4) -> list[PlanStep]:
    """A deterministic planner keeps the safety lesson independent of model quality."""
    max_steps = min(max(max_steps, 1), 5)
    templates = [
        f"Clarify the intended outcome for: {goal}",
        "Read relevant simulated information",
        "Prepare a reversible draft",
        "Request approval for any consequential action",
        "Report the result and stop",
    ]
    return [PlanStep(i + 1, action) for i, action in enumerate(templates[:max_steps])]

