from exercise import compact_history


history = [
    {"role": "user", "content": "My preferred unit is millimetres."},
    {"role": "assistant", "content": "Noted."},
    {"role": "tool", "content": "calculation completed: 25 mm"},
    {"role": "user", "content": "Use that result in the report."},
]
compacted = compact_history(history, keep_recent=2)
assert history[0]["content"].startswith("My preferred")
assert len(compacted) == 3
assert compacted[0]["role"] == "system"
assert "millimetres" in compacted[0]["content"]
assert compacted[-2:] == history[-2:]
print("PASS: history is bounded and essential information is retained")

