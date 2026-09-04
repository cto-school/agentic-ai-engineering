# Day 2 — Knowledge, RAG and State

**Project:** Engineering Knowledge Assistant — a retrieval pipeline that answers only from the
passages it retrieved, cites them, refuses when the evidence is missing, and is scored on a golden
set that keeps retrieval failures and answer failures apart.

## The notebook

Students open **one** Google Colab notebook, `day_02_complete.ipynb`, and run it top to bottom.
It is self-contained: no repository clone, no local files, no `.env`. The API key comes from a
Colab secret named `OPENROUTER_API_KEY` (or is typed once when the setup cell asks). Without a key
the notebook runs on a built-in mock model that answers strictly from the evidence the application
supplied and abstains when that evidence is weak, so grounding, citation validation and abstention
are all real at zero cost.

The three corpus documents and the ten golden cases are created **inside** the notebook: a
"Create the day's data" cell writes `day2_corpus/*.md` next to the notebook and defines
`GOLDEN_CASES` as a Python list. Four Day 1 helpers (`make_strict`, `make_tool`,
`execute_tool_call`, `assistant_message`) are reproduced once in a "Carried over from Day 1" cell;
everything else is built step by step in the notebook.

| Section | Lesson file (derived) | What is built |
|---|---|---|
| 2.1 | `01_documents_and_chunks.ipynb` | `Chunk` model, heading-aware `chunk_markdown`, 15 chunks with `source`/`title`/`section`/`chunk_id`; blind character slices as the counter-example |
| 2.2 | `02_keyword_search.ipynb` | `tokenize` / `content_terms` / `keyword_score`; the paraphrase "What keeps running during a blackout?" scores the correct chunk **0** |
| 2.3 | `03_embeddings_and_semantic_search.ipynb` | `HashEmbedder`, `VectorIndex`, `SentenceTransformerEmbedder` with a printed fallback; the same question moves the expected chunk from rank 14 to rank 1. Optional Chroma cell |
| 2.4 | `04_exercise_rag_context.ipynb` | **exercise:** `build_context(retrieved, character_budget)` — ranked, labelled, bounded, skip-not-truncate — then the prompt and the first grounded answer |
| 2.5 | `05_citations_and_abstention.ipynb` | `ModelAnswer` / `GroundedAnswer`, strict schema, `validate_citations`, the `grounded` flag, abstention, and the assembled `KnowledgeAssistant` |
| 2.6 | `06_retrieval_evaluation.ipynb` | `evaluate_retrieval` and `evaluate_answers` scored separately, `n/a` for the unanswerable case, essential-term coverage, top-k sweep, embedder swap |
| 2.7 | `07_retrieval_tool_and_state.ipynb` | retrieval behind a real tool-calling loop, `KnowledgeState` printed after every step, a planted instruction quoted as evidence rather than obeyed |
| 2.8 | `08_project_knowledge_assistant.ipynb` | the project: both scorecards, a diagnosis per failing case, one layer changed, both halves re-measured |

The files under `notebooks/` are generated from the day notebook by `split_day_notebooks.py`
for the course portal. Edit the day notebook, then re-run the split; do not edit the lesson files.

## Live versus mock

| Mode | When | What differs |
|---|---|---|
| Mock | no key found | `mock_model` parses the labelled evidence blocks the application supplied, quotes the passage matching the most specific question words, abstains when none matches, requests the retrieval tool when one is offered, and returns schema-valid JSON when a `response_format` is given |
| Live | key found | `chat()` calls `openai/gpt-oss-120b` through OpenRouter with `reasoning.effort=low`, `temperature=0`, `max_tokens=600`; the same cells, the same contract |

Both modes run every cell. The one *required live observation* (section 2.4) compares a live
grounded answer with the mock one over the identical retrieved passages.

The mock is deliberately only a lexical stand-in, and the notebook says where it can be fooled:
"Who manufactured the battery cells?" is answered rather than refused because a retrieved passage
contains the word *cell*.

## What each layer is measured on

| Report | Checks | Baseline (hash embedder, top_k=3) | After swapping the embedder |
|---|---|---|---|
| Retrieval | `source_hit`, `section_hit`, `expected_rank`, `n/a` when the case is unanswerable | 8/9 source, 7/9 section (q01, q03 miss) | 9/9 source, 9/9 section |
| Answers | `abstention_correct`, `citation_correct`, `citation_provenance_ok`, essential-term coverage | 9/10, 9/10, 10/10, coverage 0.737 | 10/10, 10/10, 10/10, coverage 0.789 |

q01 still covers none of its essential terms after the fix even though its section is now retrieved
at rank 3 — the notebook names that hand-over explicitly as a generation limit, not a retrieval one.

## Failure cases demonstrated in code

| Layer | Trigger | What the student sees |
|---|---|---|
| Chunking | 250-character blind slices of `solar_microgrid.md` | the five-minute reconnection rule is split across two pieces that carry no source, section or id |
| Retrieval | the paraphrase "What keeps running during a blackout?"; `top_k=3` on the hash index for golden case q03 | keyword score 0 and rank 14; the answering section never reaches the model and the answer is a refusal |
| Sufficiency | "What is the purchase price of the battery system?" | three chunks come back with ordinary scores; nearest-neighbour search has no concept of "no result" |
| Citation | a hand-built answer citing `battery_safety:appendix-c` | the citation is dropped and `grounded` becomes `False` |
| Prompt injection | a scratch chunk saying "IGNORE ALL PREVIOUS INSTRUCTIONS" indexed beside the corpus | the agent quotes it as evidence, cites its chunk id, and the marker scan flags it |

## Required environment

Python 3.10+ and the root `requirements.txt`. Inside the notebook only one install runs:
`%pip install -q sentence-transformers` in section 2.3. If it fails, or the model cannot be
downloaded, the notebook prints why and continues on the deterministic hash embedder; every
comparison then says "not available" instead of pretending. `chromadb` is never installed — the
Chroma cell imports it inside `try/except` and is safe to skip.

## Reference package (optional)

`src/knowledge_agent/` is a packaged version of the same design (documents, embeddings, retrieval,
generation, citation validation, evaluation) with tests in `tests/`. It is not used by the notebook;
it exists for instructors and for students who want to see the notebook's ideas as an installable
module. `data/corpus/` and `data/golden_set.json` are the same corpus and golden set the notebook
recreates inline.

```powershell
python -m pytest tests -q
python run_project.py "Which loads stay powered when the campus microgrid is islanded?"
python evaluate_project.py
```

For a worked, layer-by-layer diagnosis of one failing case, see
[`reference/rag_failure_diagnosis.md`](../reference/rag_failure_diagnosis.md).

## Deliberately deferred

Rerankers, hybrid-search tuning, graph RAG, large ingestion pipelines, retrieval benchmarks, and
vector-database comparisons. Day 3 takes over with context growth, memory and execution policy.
