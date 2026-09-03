"""Grounded answer generators for real classroom and deterministic test modes."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Protocol

from .schemas import Citation, GroundedAnswer, RetrievedChunk


class GroundedGenerator(Protocol):
    def generate(self, question: str, retrieved: list[RetrievedChunk]) -> GroundedAnswer: ...


def _context(retrieved: list[RetrievedChunk]) -> str:
    return "\n\n".join(
        f"[{item.chunk.chunk_id}] Source: {item.chunk.source}; Section: {item.chunk.section}\n{item.chunk.text}"
        for item in retrieved
    )


class MockGroundedGenerator:
    """Extractive deterministic generator used to test the pipeline offline."""

    def generate(self, question: str, retrieved: list[RetrievedChunk]) -> GroundedAnswer:
        context = _context(retrieved)
        lowered_question = question.lower()
        absent_fact_cues = ("price", "purchase cost", "warranty")
        unsupported = any(cue in lowered_question and cue not in context.lower() for cue in absent_fact_cues)
        if not retrieved or unsupported:
            return GroundedAnswer(
                answer="The supplied documents do not contain enough evidence to answer this question.",
                citations=[],
                grounded=True,
                abstained=True,
            )

        best = retrieved[0].chunk
        return GroundedAnswer(
            answer=best.text,
            citations=[Citation(source=best.source, section=best.section, chunk_id=best.chunk_id)],
            grounded=True,
            abstained=False,
        )


class OpenRouterGroundedGenerator:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")

    def generate(self, question: str, retrieved: list[RetrievedChunk]) -> GroundedAnswer:
        schema = GroundedAnswer.model_json_schema()
        prompt = f"""Answer only from the supplied evidence.
If the evidence does not answer the question, set abstained=true, use no citations,
and say that the supplied documents do not contain enough evidence.
Every non-abstained answer must cite the exact source, section, and chunk_id.

Question: {question}

Evidence:
{_context(retrieved)}
"""
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "grounded_answer", "strict": True, "schema": schema},
            },
            "max_tokens": 700,
            "reasoning": {"effort": "low", "exclude": True},
            "provider": {"require_parameters": True, "sort": "price"},
        }
        request = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"OpenRouter request failed: {exc}") from exc
        return GroundedAnswer.model_validate_json(data["choices"][0]["message"]["content"])

