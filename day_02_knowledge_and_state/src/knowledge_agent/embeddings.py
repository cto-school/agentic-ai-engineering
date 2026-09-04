"""Real local embeddings plus a deterministic offline teaching fallback."""

from __future__ import annotations

import hashlib
import math
import os
from typing import Protocol

from .text import tokenize

# Kept as a private alias so older notebooks and tests that imported `_tokens`
# from this module keep working.
_tokens = tokenize


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


def _normalize(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / magnitude for value in vector]


class TokenHashEmbedder:
    """Stable token vectors for offline runs; not a substitute for semantic embeddings.

    Each word is hashed to one position in a fixed-length vector and counted there.
    Two texts are similar only when they share the *same words*, so this embedder is
    keyword search wearing a vector costume. That is exactly why we compare it with a
    trained model in notebook 03.
    """

    def __init__(self, dimensions: int = 512):
        self.dimensions = dimensions
        self.name = "hash"

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            vector = [0.0] * self.dimensions
            for token in tokenize(text):
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "big") % self.dimensions
                vector[index] += 1.0
            vectors.append(_normalize(vector))
        return vectors


class SentenceTransformerEmbedder:
    """Local semantic embeddings downloaded once and reused across requests."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:  # package missing
            raise RuntimeError("Install sentence-transformers for semantic search") from exc
        # The first call downloads ~90 MB; afterwards it is served from the local cache.
        self.model = SentenceTransformer(model_name)
        self.name = "semantic"

    def embed(self, texts: list[str]) -> list[list[float]]:
        values = self.model.encode(texts, normalize_embeddings=True)
        return [vector.tolist() for vector in values]


def default_embedder_preference() -> str:
    """Read the classroom toggles: EMBEDDER wins, otherwise DAY2_MODE decides."""

    explicit = os.getenv("EMBEDDER")
    if explicit:
        return explicit.strip().lower()
    return "hash" if os.getenv("DAY2_MODE", "").strip().lower() == "mock" else "auto"


def load_embedder(preference: str | None = None, verbose: bool = True) -> tuple[Embedder, str]:
    """Return (embedder, label) and never raise because a download failed.

    preference: "auto" (semantic if it loads, else hash), "semantic", or "hash".
    The classroom laptop may be offline, so a failed model download must degrade to the
    deterministic hash embedder with a printed explanation instead of stopping the lesson.
    """

    choice = (preference or default_embedder_preference()).strip().lower()
    if choice not in {"auto", "semantic", "hash"}:
        raise ValueError("EMBEDDER must be auto, semantic, or hash")

    if choice == "hash":
        if verbose:
            print("Embedder     : hash (deterministic offline fallback, selected explicitly)")
        return TokenHashEmbedder(), "hash"

    model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    try:
        embedder = SentenceTransformerEmbedder(model_name)
    except Exception as exc:  # no package, no network, corrupted cache...
        if verbose:
            print(f"Embedder     : hash (sentence-transformers unavailable: {type(exc).__name__})")
            print("               Every cell still runs; paraphrase questions will retrieve worse.")
        return TokenHashEmbedder(), "hash"
    if verbose:
        print(f"Embedder     : semantic ({model_name})")
    return embedder, "semantic"
