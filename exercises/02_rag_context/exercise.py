"""Assemble grounded context from ranked retrieval results."""


def build_context(chunks, character_budget):
    """Return labeled context without exceeding character_budget.

    Each input is {"source": str, "section": str, "text": str}.
    Preserve rank order. Never cut a chunk mid-text; skip chunks that do not fit.
    Label included chunks as [source | section].
    """
    raise NotImplementedError("TODO: select, label, and budget evidence")

