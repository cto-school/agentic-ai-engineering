# Worked RAG Failure Diagnosis

Use this worksheet after students have built keyword search, semantic retrieval, and a basic grounded answer.

## The case

Question: “What inspection is required before energising the prototype?”

Expected evidence: `commissioning.md`, section “Pre-energisation checks,” which says the enclosure and protective-earth continuity must be inspected.

Observed result: the assistant answers, “Run a functional software test,” and cites `testing.md`.

## Diagnose one layer at a time

### 1. Inspect the question and stored documents

Check that the expected statement actually exists in the corpus and was loaded. If it is absent, the failure is ingestion or the test expectation—not generation.

### 2. Inspect chunks and metadata

Find the expected text in the chunk list. Confirm that its source and section metadata survived chunking. A missing sentence indicates a chunking or cleaning failure. Incorrect metadata can produce a correct answer with a false citation.

### 3. Inspect retrieval independently

Run retrieval without calling the answer model. Record the top-k chunk identifiers and scores.

Example observation:

```text
1. testing.md#functional-tests      0.74
2. commissioning.md#power-up       0.61
3. commissioning.md#pre-checks     0.58
```

The expected chunk is present at rank 3. This is not a total retrieval miss. Before changing models, test whether `top_k=3` and the context builder preserve that chunk.

### 4. Inspect assembled context

Print the exact context sent to the model, including source labels. In this case, the context builder kept only the first two chunks, so the required evidence never reached the model. The defect is context assembly, not model intelligence.

### 5. Inspect the answer contract

The generator was instructed to answer even when evidence was weak. Tighten the contract: use only supplied evidence, cite the supporting source, and abstain when the evidence does not support the answer.

### 6. Re-run the same case and the full set

After changing the context builder, re-run both this example and the full golden set. A local fix can create regressions—for example, raising top-k can introduce distractors or exceed the context budget.

## Diagnosis record

| Layer | Evidence inspected | Finding | Change |
|---|---|---|---|
| Ingestion | Loaded document list | Expected source present | None |
| Chunking | Chunk text and metadata | Expected statement preserved | None |
| Retrieval | Ranked chunk IDs | Expected chunk at rank 3 | None initially |
| Context assembly | Exact model input | Only top 2 chunks included | Include selected top-k within budget |
| Generation | Prompt and output | Answer forced despite weak evidence | Add grounded abstention contract |
| Evaluation | Full golden set | Re-test required | Run retrieval and answer checks separately |

## Rule of thumb

Do not “fix RAG” by immediately changing the language model. First locate the failing boundary: document → chunk → retrieval result → assembled context → answer → citation.

