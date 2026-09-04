# Day 2 Course Data

`corpus/` holds three fictional engineering documents written for this course (a campus
solar microgrid, a battery safety guide, and a controller interface reference). They may
be redistributed with the repository.

They are deliberately small - about 700 words and 15 heading-sized chunks in total - so
students can inspect every chunk and every retrieval result by hand instead of trusting a
pipeline they cannot see.

`golden_set.json` contains the 10 evaluation cases: nine answerable questions with the
expected source, section and essential terms, plus one question the corpus cannot answer
(the battery purchase price). It is the exam paper, so it must never be added to the
indexed corpus or shown to the model.

Two answerable cases, q01 and q03, are deliberately hard for the deterministic offline
embedder. Their misses are the worked examples in `reference/rag_failure_diagnosis.md`.
