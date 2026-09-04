# Day 4 synthetic evaluation data

| File | What it is |
| --- | --- |
| `seeded_artifact/order_service.py` | Deliberately defective classroom code. Never reuse it in an application. |
| `golden_defects.json` | The instructor-owned answer key (9 defects) used to measure recall, false positives and duplicates. |
| `captured_comparison.json` | A saved comparison table so notebook 06 works with no network. |

Students should inspect the artifact and predict defects **before** the answer key is
revealed (notebook 01 is ordered that way), then use the key only for evaluation. The key
is never included in any prompt sent to a reviewer.

## About `captured_comparison.json`

It was generated **offline by `MockStructuredReviewer` — no model was called**, so it is a
record of the deterministic classroom result, not evidence about any real LLM. It exists
so notebook 06 can still show a table when OpenRouter is unavailable. Regenerate it with:

```powershell
py evaluate_project.py --write
```
