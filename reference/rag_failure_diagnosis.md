# Worked RAG Failure Diagnosis

Use this worksheet after Day 2 notebook 06. Every number below comes from the Day 2 corpus
in `day_02_knowledge_and_state/data/corpus/` and can be reproduced in mock mode:

```text
cd day_02_knowledge_and_state
python evaluate_project.py
```

The rule it teaches: do not "fix RAG" by changing the model. Locate the failing boundary
first — document → chunk → retrieval result → assembled context → answer → citation.

## The case

Golden case **q01** (`data/golden_set.json`).

- Question: "Which loads stay powered when the campus microgrid is islanded?"
- Expected evidence: `solar_microgrid.md`, section **Load priorities**, chunk id
  `solar_microgrid:load-priorities`, which lists emergency lighting, network equipment,
  fire-alarm equipment and the medical room refrigerator.
- Observed answer (mock mode): a passage about grid-connected and islanded *operating
  modes*, cited as `solar_microgrid:operating-modes`.

The scorecard shows the contradiction that starts the investigation:

```text
retrieval : source_hit=yes   section_hit=NO   expected_rank=n/a
answers   : citation_correct=yes   essential_term_coverage=0.00
```

The citation names the right file, so a shallow check passes — while the answer contains
none of the four facts the question asked for.

## Diagnose one layer at a time

### 1. Ingestion — is the statement in the corpus at all?

```python
chunks = load_markdown_corpus(PROJECT_ROOT / "data" / "corpus")
print([c.chunk_id for c in chunks if "emergency lighting" in c.text])
# ['solar_microgrid:load-priorities']
```

Present. If this printed `[]` the defect would be ingestion or a wrong golden expectation,
and nothing downstream would be worth inspecting.

### 2. Chunking — did the metadata survive?

The chunk carries `source='solar_microgrid.md'`, `section='Load priorities'`,
`chunk_id='solar_microgrid:load-priorities'`, and the whole priority list sits inside one
chunk (notebook 01 shows a blind 250-character slice cutting the same document mid-rule).
Metadata is intact, so a citation *could* have been correct. Not the defect.

### 3. Retrieval — inspect it without calling any generator

Mock mode, `TokenHashEmbedder`, `top_k=3`:

```text
1. solar_microgrid:operating-modes          0.435
2. solar_microgrid:purpose                  0.314
3. battery_safety:thermal-event-response    0.304
...
8. solar_microgrid:load-priorities          (expected chunk)
```

The expected chunk is at rank **8 of 15**. This is not a near miss that a larger `top_k`
quietly repairs — at `top_k=5` it is still absent. **This is the defect.**

Why: the question says *loads stay powered*; the chunk says *priority 1 loads … lower
priority loads are shed first*. The words barely overlap, and the hash embedder only
measures word overlap (notebook 03).

### 4. Context assembly — was the retrieved evidence passed on faithfully?

`build_evidence_context` labels each passage with its chunk id, source and section and
passes all three retrieved chunks through. Nothing was dropped or truncated. Given what
retrieval supplied, the context is correct — so the generator never had a chance.

### 5. Generation and citation — what did the answer do with bad evidence?

The generator quoted the top chunk and cited `solar_microgrid:operating-modes`.
`validate_citations` confirms that id *was* retrieved, so `grounded=True`: the answer is
faithful to its evidence and still useless. Grounding is a claim about provenance, never
about correctness. Essential-term coverage is the column that exposes it.

### 6. Fix the layer that actually failed, then re-measure everything

Change one thing — the representation — and run the identical golden set:

```text
SentenceTransformerEmbedder, top_k=3
1. solar_microgrid:operating-modes   0.687
2. solar_microgrid:limitation        0.627
3. solar_microgrid:load-priorities   0.595   <- expected chunk, now in context
```

Retrieval for the whole set moves from `source_hit 8/9, section_hit 7/9` to `9/9, 9/9`,
and case q03 (a complete source miss under the hash embedder) is repaired at the same time.

Re-measure the answers too. q01's essential-term coverage is *still* 0.00: the expected
chunk is now in the context at rank 3, but the offline extractive generator quotes the
rank-1 chunk. The defect has moved from retrieval to generation — which is progress, and
which only separate reports can show. Remaining options belong to that layer: a real model
that reads all three passages, a reranker, or a `top_k` and ordering change.

## Diagnosis record

| Layer | Evidence inspected | Finding | Change |
|---|---|---|---|
| Ingestion | Chunk list filtered by phrase | Expected statement present | None |
| Chunking | `chunk_id`, `source`, `section`, text | Metadata intact, rule not split | None |
| Retrieval | Ranked chunk ids and scores | Expected chunk at rank 8 of 15 | **Swap the embedder** |
| Context assembly | Exact string sent to the model | All retrieved chunks passed, labelled | None |
| Generation | Answer plus essential terms | Quoted rank 1, missed the facts | Live model / rerank |
| Citation | `validate_citations` result | Citation genuine, `grounded=True` | None — it was never the bug |
| Evaluation | Full golden set, before and after | Retrieval 7/9 → 9/9 sections | Re-run both reports |

## Rule of thumb

A wrong answer is a routing problem before it is a quality problem. Ask "was the evidence
retrieved?" before "was the answer good?", and only change one layer between measurements —
otherwise you cannot tell which change helped.
