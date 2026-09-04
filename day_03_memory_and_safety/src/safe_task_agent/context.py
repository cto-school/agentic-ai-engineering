from __future__ import annotations

from .schemas import Message

SUMMARY_PREFIX = "Earlier conversation summary (rule-based, lossy):"


def estimate_tokens(text: str) -> int:
    """A visible classroom approximation; provider tokenizers are more exact."""
    return max(1, (len(text) + 3) // 4)


def total_tokens(messages: list[Message]) -> int:
    """Estimated size of a whole message list, so before/after is easy to print."""
    return sum(estimate_tokens(message.content) for message in messages)


def key_fact(message: Message, max_words: int = 12) -> str:
    """Turn one message into a short 'role: fact' line.

    This is a *rule-based* extractor: it simply keeps the first few words. It has no
    understanding of which words mattered, which is exactly the loss we want students
    to see. A model summariser would rewrite the sentence instead of cutting it.
    """
    words = message.content.split()
    fact = " ".join(words[:max_words])
    if len(words) > max_words:
        fact += " ..."
    return f"{message.role}: {fact}"


def summarize_messages(messages: list[Message], summary_budget: int) -> Message:
    """Build one system message that fits inside `summary_budget` estimated tokens.

    Newest facts are added first and the oldest facts are dropped when the budget runs
    out, because the newest dropped turns are usually the most relevant to what comes
    next. The number of fully dropped turns is stated in the summary so the loss is
    never silent.
    """
    lines: list[str] = []
    used = estimate_tokens(SUMMARY_PREFIX) + 10  # header plus room for the "dropped" note
    for message in reversed(messages):
        fact = key_fact(message)
        cost = estimate_tokens(fact) + 1
        if used + cost > summary_budget:
            break
        lines.append(fact)
        used += cost
    lines.reverse()
    dropped = len(messages) - len(lines)
    header = [SUMMARY_PREFIX]
    if dropped:
        header.append(f"- ({dropped} older turns dropped)")
    return Message("system", "\n".join(header + [f"- {line}" for line in lines]))


def compact_history(messages: list[Message], budget: int = 250) -> list[Message]:
    """Keep recent turns verbatim and replace older turns with a bounded summary.

    The summary may use at most `budget // 3` estimated tokens, so compaction always
    makes the history smaller instead of copying the old turns under a new heading.
    """
    before = total_tokens(messages)
    if before <= budget:
        return messages[:]

    summary_budget = max(16, budget // 3)
    recent_budget = budget - summary_budget

    kept: list[Message] = []
    used = 0
    for message in reversed(messages):
        cost = estimate_tokens(message.content)
        # Always keep at least the newest message, even if it alone exceeds the budget.
        if kept and used + cost > recent_budget:
            break
        kept.append(message)
        used += cost
    kept.reverse()

    removed = messages[: len(messages) - len(kept)]
    if not removed:
        return kept

    compacted = [summarize_messages(removed, summary_budget), *kept]
    if total_tokens(compacted) >= before:
        # Safety net: never return something larger than what we started with.
        return kept
    return compacted
