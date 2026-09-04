from exercise import merge_findings


results = [
    {"status": "ok", "findings": [{"id": "F2", "severity": 2}, {"id": "F1", "severity": 3}]},
    {"status": "error", "error": "timeout"},
    {"status": "ok", "findings": [{"id": "F1", "severity": 3}, {"id": "F3", "severity": 1}]},
]
merged = merge_findings(results)
assert [item["id"] for item in merged] == ["F1", "F2", "F3"], "dedupe by id, tolerate the failed specialist"

# Severity must win over id order: Z1 (severity 4) comes before A9 (severity 1).
tricky = [{"status": "ok", "findings": [{"id": "A9", "severity": 1}, {"id": "Z1", "severity": 4}]}]
assert [item["id"] for item in merge_findings(tricky)] == ["Z1", "A9"], "sort by severity first, then id"
print("PASS: merge is deterministic, deduplicated, ranked, and tolerant of partial failure")
