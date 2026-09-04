from exercise import compact_history


history = [
    {"role": "user", "content": "My preferred unit is millimetres."},
    {"role": "assistant", "content": "Noted."},
    {"role": "tool", "content": "calculation completed: 25 mm"},
    {"role": "user", "content": "Use that result in the report."},
]
compacted = compact_history(history, keep_recent=2)
assert len(history) == 4 and history[0]["content"].startswith("My preferred"), "input must not be mutated"
assert len(compacted) == 3
assert compacted[0]["role"] == "system" and "millimetres" in compacted[0]["content"], "older user facts survive"
assert compacted[-2:] == history[-2:], "recent messages stay verbatim"

short = history[:2]
kept = compact_history(short, keep_recent=2)
assert kept == short and kept is not short, "short histories are returned as an unchanged copy"
print("PASS: history is bounded, essential information is retained, input is untouched")
