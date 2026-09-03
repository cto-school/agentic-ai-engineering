from exercise import build_context


chunks = [
    {"source": "a.md", "section": "Safety", "text": "Wear eye protection."},
    {"source": "b.md", "section": "Power", "text": "Verify protective earth."},
    {"source": "c.md", "section": "Noise", "text": "This distractor should not fit."},
]
result = build_context(chunks, 90)
assert len(result) <= 90
assert "[a.md | Safety]" in result
assert "Wear eye protection." in result
assert "This distractor" not in result
print("PASS: context is labeled, ordered, and bounded")

