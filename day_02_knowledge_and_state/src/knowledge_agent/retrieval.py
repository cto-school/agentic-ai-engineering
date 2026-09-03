"""A small inspectable vector index used before introducing a database wrapper."""

from __future__ import annotations

from .embeddings import Embedder
from .schemas import DocumentChunk, RetrievedChunk


def dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


class VectorIndex:
    def __init__(self, embedder: Embedder):
        self.embedder = embedder
        self.chunks: list[DocumentChunk] = []
        self.vectors: list[list[float]] = []

    def add(self, chunks: list[DocumentChunk]) -> None:
        self.chunks.extend(chunks)
        self.vectors.extend(self.embedder.embed([chunk.searchable_text for chunk in chunks]))

    def search(self, query: str, top_k: int = 3) -> list[RetrievedChunk]:
        if not self.chunks:
            raise ValueError("Index is empty")
        query_vector = self.embedder.embed([query])[0]
        ranked = sorted(
            zip(self.chunks, self.vectors),
            key=lambda pair: dot(query_vector, pair[1]),
            reverse=True,
        )[:top_k]
        return [
            RetrievedChunk(chunk=chunk, score=dot(query_vector, vector), rank=rank)
            for rank, (chunk, vector) in enumerate(ranked, start=1)
        ]


class ChromaVectorIndex:
    """Ephemeral Chroma collection using the same explicit embedding component."""

    def __init__(self, embedder: Embedder, collection_name: str = "day2_engineering_notes"):
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError("Install chromadb for the classroom vector-database path") from exc
        self.embedder = embedder
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self.chunks_by_id: dict[str, DocumentChunk] = {}

    def add(self, chunks: list[DocumentChunk]) -> None:
        self.chunks_by_id.update({chunk.chunk_id: chunk for chunk in chunks})
        self.collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {"source": chunk.source, "title": chunk.title, "section": chunk.section}
                for chunk in chunks
            ],
            embeddings=self.embedder.embed([chunk.searchable_text for chunk in chunks]),
        )

    def search(self, query: str, top_k: int = 3) -> list[RetrievedChunk]:
        result = self.collection.query(
            query_embeddings=self.embedder.embed([query]),
            n_results=top_k,
            include=["distances"],
        )
        ids = result["ids"][0]
        distances = result["distances"][0]
        return [
            RetrievedChunk(
                chunk=self.chunks_by_id[chunk_id],
                score=1.0 - float(distance),
                rank=rank,
            )
            for rank, (chunk_id, distance) in enumerate(zip(ids, distances), start=1)
        ]
