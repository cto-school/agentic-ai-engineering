from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from knowledge_agent.documents import load_markdown_corpus
from knowledge_agent.evaluation import evaluate_retrieval, load_golden_set
from run_project import build_assistant


class DocumentTests(unittest.TestCase):
    def test_heading_aware_chunks_keep_metadata(self):
        chunks = load_markdown_corpus(PROJECT_ROOT / "data" / "corpus")
        self.assertGreaterEqual(len(chunks), 12)
        self.assertTrue(all(chunk.source and chunk.section and chunk.text for chunk in chunks))


class KnowledgeAssistantTests(unittest.TestCase):
    def test_answer_has_citation(self):
        state = build_assistant("mock").answer("How long are battery fault records retained?")
        self.assertEqual(state.status, "completed")
        self.assertFalse(state.answer.abstained)
        self.assertEqual(state.answer.citations[0].source, "battery_safety.md")

    def test_absent_purchase_price_causes_abstention(self):
        state = build_assistant("mock").answer("What is the purchase price of the battery system?")
        self.assertTrue(state.answer.abstained)
        self.assertEqual(state.answer.citations, [])

    def test_retrieval_source_hit_rate_is_useful_offline(self):
        assistant = build_assistant("mock")
        cases = load_golden_set(PROJECT_ROOT / "data" / "golden_set.json")
        records = evaluate_retrieval(assistant.index, cases, top_k=3)
        answerable = [record for record in records if record["answerable"]]
        hit_rate = sum(record["source_hit"] for record in answerable) / len(answerable)
        self.assertGreaterEqual(hit_rate, 0.8)


if __name__ == "__main__":
    unittest.main()

