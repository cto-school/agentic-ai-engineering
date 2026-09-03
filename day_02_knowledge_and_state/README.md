# Day 2 — Knowledge and State

## Project

Build an Engineering Knowledge Assistant that retrieves from supplied documents, answers with citations, uses retrieval as a tool, and carries visible execution state.

All required theory is embedded in the notebooks at the point where it is used. Complete Notebook 09 after building basic RAG.

## Progression

```text
Load documents
-> split into chunks
-> keyword search
-> semantic search
-> basic RAG
-> citations and abstention
-> 10-case golden set
-> retrieval tool and state
```

## Concepts introduced

Document, chunk, embedding, semantic similarity, vector store, retrieval, grounding, citation, RAG, knowledge tool, and application state.

## Notebook sequence

1. `01_documents_and_chunks.ipynb` — load, clean, and split a small corpus. **Available.**
2. `02_keyword_search.ipynb` — build an intuitive retrieval baseline. **Available.**
3. `03_embeddings_and_semantic_search.ipynb` — compare meanings using vectors. **Available.**
4. `04_basic_rag.ipynb` — supply retrieved passages to the model. **Available.**
5. `05_citations_and_abstention.ipynb` — show evidence or decline to answer. **Available.**
6. `06_retrieval_evaluation.ipynb` — measure retrieval and answer behaviour separately. **Available.**
7. `07_retrieval_tool_and_state.ipynb` — let the agent choose document search. **Available.**
8. `08_project_knowledge_assistant.ipynb` — assemble the project. **Available.**
9. `09_exercise_rag_context.ipynb` — independently assemble and test bounded, labeled evidence context. **Available.**

## Required environment

- Completed setup or the supplied Day 2 starter environment
- Sentence Transformers embedding model
- Chroma
- Supplied engineering document corpus

No hosted vector database is required.

## Reference implementation status

The Day 2 final-project reference is available in `src/knowledge_agent/` before notebook decomposition.

It includes:

- Heading-aware Markdown chunking with source and section metadata
- An inspectable in-memory vector index
- A Chroma-backed classroom vector index
- Local Sentence Transformers embeddings
- A deterministic token-hashing embedder for offline tests only
- OpenRouter grounded generation with a strict response schema
- Citation and abstention contracts
- Visible question, retrieval, answer, status, and error state
- Separate retrieval and answer evaluation
- A 10-case golden set

### Offline validation

```text
python day_02_knowledge_and_state/run_project.py
python day_02_knowledge_and_state/evaluate_project.py
python -m unittest discover -s day_02_knowledge_and_state/tests -v
```

### Classroom mode

Set `DAY2_MODE=classroom`. This selects Sentence Transformers, Chroma, and the issued OpenRouter route. The embedding model should be downloaded before Day 2 if classroom internet is unreliable.

The deterministic fallback is intentionally less capable than semantic embeddings. Its retrieval misses become examples for diagnosing the retrieval layer.

## Dataset constraints

- Approximately 3–10 pages for the guided lab
- Approximately 20–50 chunks
- Documents with stable page/source metadata
- Questions with known evidence for manual checking

## Deliberately deferred

- Rerankers
- Hybrid-search tuning
- Graph RAG
- Large ingestion pipelines
- Retrieval benchmarks
- Multiple vector-database comparisons

## Project completion checklist

- [ ] The system ingests the supplied documents.
- [ ] It retrieves relevant chunks using semantic search.
- [ ] Answers include source identifiers.
- [ ] The system declines when evidence is missing.
- [ ] Retrieval can be selected as an agent tool.
- [ ] Intermediate state is visible to the student.
- [ ] The student can distinguish knowledge from model training data.

## Required test questions

- Three questions answerable from the corpus
- One question requiring the calculator
- One unanswerable question
- One wording-mismatch question demonstrating semantic search

## First formal evaluation

Before the full evaluation, work through the [RAG failure diagnosis](../reference/rag_failure_diagnosis.md). It demonstrates how to locate a failure at the ingestion, chunking, retrieval, context, generation, or citation boundary instead of changing components blindly.

Students use a supplied 10-case golden set containing the expected source, answerability, and essential answer points.

Retrieval checks:

- Expected source/chunk appears in top-k
- Retrieval miss count
- Effect of changing top-k

Answer checks:

- Evidence supports the answer
- Citation points to the retrieved source
- System abstains when evidence is absent

Generation and retrieval must be evaluated separately so students can locate the failing layer.

## Optional extensions

- Compare Chroma with Qdrant.
- Use a hosted embedding API.
- Add metadata filters.
