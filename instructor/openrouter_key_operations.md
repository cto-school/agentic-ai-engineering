# OpenRouter Student-Key Operations

This is an instructor operations specification. Do not commit generated plaintext keys.

## Key properties

- Name format: `agentic-ai-COURSE-student-NNN`
- Limit: USD 1
- Limit reset: none
- Expiry: shortly after course completion
- One key per student

## Private records

Maintain outside the public repository:

- Student/roll identifier
- OpenRouter key label and hash
- Plaintext key distribution status
- Current usage and remaining limit
- Revocation status

The management API credential must never be placed in student code, notebooks, logs, screenshots, or generated distribution files.

## Lifecycle

1. Purchase sufficient account credits plus contingency.
2. Create a management API key.
3. Generate individually named, limited, expiring keys.
4. Capture each plaintext key exactly once.
5. Distribute keys through an approved private channel.
6. Apply model/provider guardrails where available.
7. Monitor usage by key during delivery.
8. Disable compromised or anomalous keys.
9. Revoke every student key after the course.

## Pre-course validation

- Run the complete instrumented course once.
- Verify actual per-student cost under the configured limits.
- Run a representative concurrency test from the institution network.
- Confirm 403/limit errors are explained clearly in notebooks.
- Prepare mock mode for API outage or capacity problems.

Official references:

- [OpenRouter management API keys](https://openrouter.ai/docs/guides/overview/auth/management-api-keys)
- [Create API key](https://openrouter.ai/docs/api/api-reference/api-keys/create-keys)
- [OpenRouter guardrails](https://openrouter.ai/docs/guides/features/guardrails/overview)
