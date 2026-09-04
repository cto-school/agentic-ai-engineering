"""Tiny shared text helpers.

Keyword search, the offline embedder and the offline generator all need the same
answer to one question: "what are the words of this text?". Keeping that in one
place means a student can change the tokenizer once and see every layer move.
"""

from __future__ import annotations

import re

# Words that appear in almost every English question. They carry no evidence, so we
# remove them before comparing a question with a chunk.
STOPWORDS = frozenset(
    """
    a an and are as at be by can could did do does for from had has have how if in into is it
    its may might must not of on or should that the their them then there these this those to
    was were what when where which who whom why will with you your during be been
    """.split()
)


def tokenize(text: str) -> list[str]:
    """Lowercase words, with a crude plural trim so 'records' matches 'record'."""

    words = re.findall(r"[a-z0-9]+", text.lower())
    return [word[:-1] if word.endswith("s") and len(word) > 4 else word for word in words]


def content_terms(text: str) -> set[str]:
    """The words that actually carry meaning: no stopwords, nothing shorter than 3 letters."""

    return {word for word in tokenize(text) if word not in STOPWORDS and len(word) > 2}
