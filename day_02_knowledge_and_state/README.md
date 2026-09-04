# Day 2 — Knowledge and State

## Project

Build an Engineering Knowledge Assistant that retrieves from supplied documents, answers with citations, validates those citations, can expose retrieval as an agent tool, and carries visible execution state.

All required theory is embedded in the notebooks at the point where it is used.

**Classroom notebook:** [`day_02_complete.ipynb`](day_02_complete.ipynb) combines all nine sections into one Colab-ready learning path. The files under `notebooks/` remain the modular source and standalone lesson versions.

## Progression

```text
Load documents
-> split into chunks
-> keyword search (and watch it fail on a paraphrase)
-> semantic search (same question, better representation)
-> basic RAG
-> citations, citation validation and abstention
-> 10-case golden set, scored honestly
-> retrieval as a tool, visible state, prompt injection
-> the assembled project
```

## Concepts introduced

Document, chunk, embedding, semantic similarity, vector index, retrieval, grounding, citation validation, abstention, RAG, knowledge tool, indirect prompt injection, and application state.

## Notebook sequence

Every lesson runs end to end with **no API key**. Notebooks 04, 05, 07 and 08 use the live model only if `OPENROUTER_API_KEY` is present, and fall back with a printed message otherwise.

1. `01_documents_and_chunks.ipynb` — read the corpus, split it into 15 heading-aware chunks with `source`, `section` and a stable `chunk_id`; compare with blind character slicing.
2. `02_keyword_search.ipynb` — build a word-overlap retriever; it ranks the right chunk first for a literal question and scores it **0** for the paraphrase "What keeps running during a blackout?".
3. `03_embeddings_and_semantic_search.ipynb` — index the corpus with `TokenHashEmbedder` and `SentenceTransformerEmbedder` and rank the **same** question with both: the expected chunk moves from rank 14 to rank 1. Optional Chroma cell.
4. `04_basic_rag.ipynb` — build the labelled evidence context and the prompt, generate an answer, then show that retrieval returns three confident chunks for a question the corpus cannot answer.
5. `05_citations_and_abstention.ipynb` — strict answer schema, then application-side `validate_citations`: an invented `chunk_id` is dropped and the answer is marked `grounded=False`; an unanswerable question abstains with zero citations.
6. `06_retrieval_evaluation.ipynb` — score retrieval and answers separately on the 10-case golden set, with `n/a` for the unanswerable case, essential-term coverage, a top-k sweep, and a one-layer fix that is re-measured.
7. `07_retrieval_tool_and_state.ipynb` — a real tool-calling loop (JSON schema, tool registry, state printed after each step) plus a planted instruction inside a retrieved chunk that is quoted as evidence rather than obeyed.
8. `08_project_knowledge_assistant.ipynb` — assemble the project, produce both scorecards, diagnose the two failing cases, change one layer, re-measure.
9. `09_exercise_rag_context.ipynb` — individual lab: assemble bounded, labelled evidence context within a character budget. Do it after notebook 04, or at the end of the day; it needs no API key.

## Required environment

- Python 3.10+ and the root `requirements.txt`
- Optional for the classroom path: `sentence-transformers` (semantic embeddings) and `chromadb` (vector database cell)
- Supplied engineering document corpus in `data/corpus/`

No hosted vector database and no API key are required.

Check your machine before the session:

```text
python day_02_knowledge_and_state/environment_check.py
DAY2_MODE=classroom python day_02_knowledge_and_state/environment_check.py
```

`OPTIONAL` lines are fine in mock mode; they only become `FAIL` when `DAY2_MODE=classroom`.

## Reference implementation

`src/knowledge_agent/` contains the assembled project:

- `documents.py` — heading-aware Markdown chunking with source, section and stable ids
- `embeddings.py` — `TokenHashEmbedder` (deterministic, offline), `SentenceTransformerEmbedder` (local semantic model), and `load_embedder` which degrades to the hash embedder with a printed reason
- `retrieval.py` — an inspectable in-memory `VectorIndex` and a Chroma-backed index
- `generation.py` — the offline `MockGroundedGenerator` (abstains from the retrieved evidence, not from a cue list), the OpenRouter generator, and `strict_json_schema`
- `assistant.py` — the pipeline plus `validate_citations`, which sets `grounded`
- `evaluation.py` — separate retrieval and answer evaluation, `n/a` where a check does not apply, essential-term coverage, and a small table renderer
- `schemas.py` — `ModelAnswer` (what the model may return) and `GroundedAnswer` (what the application concludes)

### Toggles

| Variable | Values | Effect |
|---|---|---|
| `OPENROUTER_API_KEY` | key or unset | live generation, or deterministic offline generation |
| `EMBEDDER` | `auto` / `semantic` / `hash` | which embedder the notebooks load |
| `DAY2_MODE` | `mock` / `classroom` | `mock` forces the hash embedder and the offline generator |
| `EMBEDDING_MODEL` | model name | sentence-transformers model to load |

### Offline validation

```text
python day_02_knowledge_and_state/run_project.py
python day_02_knowledge_and_state/evaluate_project.py
python -m pytest day_02_knowledge_and_state/tests -q
```

The deterministic hash embedder is intentionally less capable than semantic embeddings. Its retrieval misses (cases q01 and q03) are the worked examples for diagnosing the retrieval layer.

## Dataset constraints

- Three short documents, about 700 words in total
- 15 chunks, one per `##` section, so every retrieval result can be checked by hand
- Stable source and section metadata on every chunk
- Ten golden questions with known evidence

## Deliberately deferred

- Rerankers
- Hybrid-search tuning
- Graph RAG
- Large ingestion pipelines
- Retrieval benchmarks
- Multiple vector-database comparisons

## Project completion checklist

- [ ] The system ingests the supplied documents into inspectable chunks.
- [ ] It retrieves relevant chunks using semantic search.
- [ ] Answers carry citations, and the application validates them against what was retrieved.
- [ ] The system declines when evidence is missing.
- [ ] Retrieval can be selected as an agent tool.
- [ ] Intermediate state is visible to the student.
- [ ] The student can distinguish corpus knowledge from model training data.

## Required test questions

The supplied golden set covers all of these:

- Three questions answerable from the corpus (for example q04, q06, q09)
- One question with a wording mismatch that defeats keyword search (q01, and the notebook 02/03 paraphrase "What keeps running during a blackout?")
- One question whose evidence is not top-1 under the offline embedder (q03)
- One unanswerable question (q10, the battery purchase price)

## First formal evaluation

Before the full evaluation, work through the [RAG failure diagnosis](../reference/rag_failure_diagnosis.md). It walks golden case q01 through ingestion, chunking, retrieval, context, generation and citation, using the real corpus and the real chunk ids, and is reproducible from notebook 06.

Retrieval checks:

- Expected source and section appear in top-k (`n/a` when the case is unanswerable)
- Rank of the expected chunk, and the miss list by case id
- Effect of changing top-k

Answer checks:

- Abstention matches answerability
- The cited source is the expected one and every citation survived validation
- Essential-term coverage, so a correct citation with an empty answer cannot look like a pass

Generation and retrieval are evaluated separately so students can locate the failing layer.

## Optional extensions

- Compare Chroma with Qdrant.
- Use a hosted embedding API.
- Add metadata filters (for example, restrict search to one source).
- Add a second tool to notebook 07 so the model has a genuine routing decision.
