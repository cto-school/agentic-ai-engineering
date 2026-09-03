from exercise import merge_findings


results = [
    {"status": "ok", "findings": [{"id": "F2", "severity": 2}, {"id": "F1", "severity": 3}]},
    {"status": "error", "error": "timeout"},
    {"status": "ok", "findings": [{"id": "F1", "severity": 3}, {"id": "F3", "severity": 1}]},
]
merged = merge_findings(results)
assert [item["id"] for item in merged] == ["F1", "F2", "F3"]
print("PASS: merge is deterministic, deduplicated, and tolerant of partial failure")

