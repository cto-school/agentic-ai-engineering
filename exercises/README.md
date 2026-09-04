# Pivotal Coding Exercises

Most notebooks are guided builds. These six exercises are deliberately different: students receive a small stub, a behavioural check, and a contract. They complete the missing decision-making code, then compare it with the fully commented reference solution that follows the check in the same notebook. The check prints a hint instead of failing while the stub is unfinished. Each exercise is a section inside the day's Colab notebook (stub, behavioural check, commented reference solution), so students never leave the notebook. The checks are deterministic and use no API credits.

| Exercise | Where in the day notebook | Central idea |
|---|---|---|
| 1. Manual agent loop | Day 1, section 1.5 | Observe, dispatch, append result, terminate safely |
| 2. RAG context assembly | Day 2, section 2.4 | Select and label evidence within a budget |
| 3. History compaction | Day 3, section 3.2 | Preserve essential state while bounding context |
| 4. Action policy | Day 3, section 3.7 (worked Try-it) | Separate proposed, allowed, and approved actions |
| 5. Supervisor merge | Day 4, section 4.5 | Combine specialist results deterministically |
| 6. Tool registry | Day 5, section 5.3 | Centralize schemas, dispatch, and permissions |

The `.py` files under this directory are source mirrors for automated checks and instructor maintenance. Students should work in the notebooks.
