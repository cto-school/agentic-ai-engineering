"""Merge specialist findings without another model call."""


def merge_findings(results):
    """Return findings sorted by severity then stable identifier.

    Deduplicate identical finding IDs, keeping the first result. A failed specialist
    is represented by {"status": "error", ...} and must not erase successful work.
    """
    raise NotImplementedError("TODO: deterministic merge, deduplication, partial failure")

