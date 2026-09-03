# Required Live Observation Contract

Each day includes one small live-model or live-data observation using the issued classroom access. Mock mode remains the required debugging and deterministic-testing route.

| Day | Required bounded observation | Outage fallback |
|---|---|---|
| 1 | One model response with provider/model/usage fields | Instructor-captured request and response trace |
| 2 | One grounded answer generated from supplied retrieved evidence | Captured grounded-generation trace plus deterministic fallback |
| 3 | One live structured action proposal governed by Python guardrails | Captured proposal; run the same policy locally |
| 4 | One single-reviewer versus specialist comparison | Captured structured outputs; evaluate locally |
| 5 | One public-source fetch or live website-update proposal | Cached source and captured proposal trace |

Rules:

- Keep prompts, contexts and outputs bounded.
- Use only supplied synthetic or public course data.
- Save the structured output and usage record where available.
- Never grade a student on provider uptime or exact model wording.
- Stop the Day 5 website agent at approval; no unattended publishing.
