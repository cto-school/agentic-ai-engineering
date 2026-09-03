from __future__ import annotations

from .schemas import Message


def estimate_tokens(text: str) -> int:
    """A visible classroom approximation; provider tokenizers are more exact."""
    return max(1, (len(text) + 3) // 4)


def compact_history(messages: list[Message], budget: int = 250) -> list[Message]:
    """Keep recent turns and replace older turns with a transparent summary."""
    if sum(estimate_tokens(m.content) for m in messages) <= budget:
        return messages[:]
    kept: list[Message] = []
    used = 0
    for message in reversed(messages):
        cost = estimate_tokens(message.content)
        if kept and used + cost > max(1, budget * 2 // 3):
            break
        kept.append(message)
        used += cost
    kept.reverse()
    removed = messages[: len(messages) - len(kept)]
    facts = [f"{m.role}: {m.content[:90]}" for m in removed]
    summary = Message("system", "Earlier conversation summary: " + " | ".join(facts))
    return [summary, *kept]

