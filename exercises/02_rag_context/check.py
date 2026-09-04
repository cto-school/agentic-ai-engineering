from exercise import build_context


chunks = [
    {"source": "a.md", "section": "Safety", "text": "Wear eye protection."},
    {"source": "b.md", "section": "Power", "text": "Verify protective earth."},
    {"source": "c.md", "section": "Noise", "text": "This distractor should not fit."},
]
result = build_context(chunks, 90)
assert len(result) <= 90, "the budget is a hard limit"
assert "[a.md | Safety]" in result and "Wear eye protection." in result
assert "[b.md | Power]" in result and "Verify protective earth." in result
assert result.index("[a.md") < result.index("[b.md"), "rank order must be preserved"
assert "This distractor" not in result, "a chunk that does not fit is skipped, never cut"
assert "[c.md" not in result, "a skipped chunk must not leave a dangling label"
print("PASS: context is labelled, ordered, bounded, and never truncated")
