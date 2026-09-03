"""Compact old conversation turns while preserving recent messages."""


def compact_history(messages, keep_recent=2):
    """Return a new history with one summary message plus recent messages.

    Preserve all messages when their count is <= keep_recent. Otherwise summarize
    older user facts and completed tool outcomes into a single system message.
    Do not modify the input list.
    """
    raise NotImplementedError("TODO: compact old turns without losing key facts")

