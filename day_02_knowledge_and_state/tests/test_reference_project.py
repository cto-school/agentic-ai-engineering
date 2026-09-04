from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from knowledge_agent.assistant import validate_citations
from knowledge_agent.documents import load_markdown_corpus
from knowledge_agent.evaluation import (
    evaluate_answers,
    evaluate_retrieval,
    load_golden_set,
    summarize,
    summarize_essential_terms,
)
from knowledge_agent.generation import MockGroundedGenerator, strict_json_schema
from knowledge_agent.schemas import Citation, GroundedAnswer, ModelAnswer
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
        self.assertTrue(state.answer.grounded)

    def test_absent_purchase_price_causes_abstention(self):
        state = build_assistant("mock").answer("What is the purchase price of the battery system?")
        self.assertTrue(state.answer.abstained)
        self.assertEqual(state.answer.citations, [])

    def test_mock_abstains_on_an_unseen_topic_without_a_hardcoded_cue(self):
        # "warranty" is on no cue list: the mock abstains because no retrieved chunk
        # contains a specific word from the question.
        state = build_assistant("mock").answer("What is the warranty period of the inverter?")
        self.assertTrue(state.answer.abstained)


class CitationValidationTests(unittest.TestCase):
    def _retrieved(self):
        return build_assistant("mock").answer("How long are battery fault records retained?").retrieved

    def test_invented_citation_is_dropped_and_answer_is_not_grounded(self):
        retrieved = self._retrieved()
        answer = GroundedAnswer(
            answer="Fault records are kept for one year.",
            citations=[Citation(source="battery_safety.md", section="Data retention", chunk_id="made_up:chunk")],
            abstained=False,
        )
        validated = validate_citations(answer, retrieved)
        self.assertEqual(validated.citations, [])
        self.assertEqual(len(validated.dropped_citations), 1)
        self.assertFalse(validated.grounded)

    def test_real_citation_survives_validation(self):
        retrieved = self._retrieved()
        chunk = retrieved[0].chunk
        answer = GroundedAnswer(
            answer=chunk.text,
            citations=[Citation(source=chunk.source, section=chunk.section, chunk_id=chunk.chunk_id)],
            abstained=False,
        )
        validated = validate_citations(answer, retrieved)
        self.assertEqual(len(validated.citations), 1)
        self.assertTrue(validated.grounded)


class SchemaTests(unittest.TestCase):
    def test_strict_schema_is_closed_and_fully_required(self):
        schema = strict_json_schema(ModelAnswer)
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(sorted(schema["properties"]), schema["required"])
        citation = schema["$defs"]["Citation"]
        self.assertFalse(citation["additionalProperties"])
        self.assertEqual(sorted(citation["properties"]), citation["required"])
        self.assertNotIn("default", schema["properties"]["citations"])
        self.assertNotIn("grounded", schema["properties"])  # the host decides, not the model


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.assistant = build_assistant("mock")
        self.cases = load_golden_set(PROJECT_ROOT / "data" / "golden_set.json")

    def test_retrieval_source_hit_rate_is_useful_offline(self):
        records = evaluate_retrieval(self.assistant.index, self.cases, top_k=3)
        answerable = [record for record in records if record["answerable"]]
        hit_rate = sum(record["source_hit"] for record in answerable) / len(answerable)
        self.assertGreaterEqual(hit_rate, 0.8)

    def test_unanswerable_case_is_reported_as_not_applicable(self):
        records = evaluate_retrieval(self.assistant.index, self.cases, top_k=3)
        unanswerable = [record for record in records if not record["answerable"]]
        self.assertTrue(unanswerable)
        for record in unanswerable:
            self.assertIsNone(record["source_hit"])
            self.assertIsNone(record["section_hit"])
        # ...and it must not inflate the rate: summarize scores only applicable cases.
        self.assertEqual(
            summarize(records, ["source_hit"])["source_hit"],
            round(sum(r["source_hit"] for r in records if r["answerable"]) / 9, 3),
        )

    def test_answer_records_expose_provenance_and_term_coverage(self):
        records = evaluate_answers(self.assistant, self.cases)
        self.assertTrue(all(record["citation_provenance_ok"] for record in records))
        terms = summarize_essential_terms(records)
        self.assertEqual(terms["cases_scored"], 9)
        self.assertGreater(terms["coverage"], 0.5)


class GeneratorTests(unittest.TestCase):
    def test_mock_abstains_without_evidence(self):
        answer = MockGroundedGenerator().generate("anything at all", [])
        self.assertTrue(answer.abstained)
        self.assertEqual(answer.citations, [])


if __name__ == "__main__":
    unittest.main()
