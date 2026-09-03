# Accounts and API Keys

## Service matrix

| Service | Requirement | Free/local alternative | Intended use |
|---|---|---|---|
| GitHub | Recommended | Download repository ZIP | Course distribution |
| OpenRouter | Required classroom route | Mock mode during outages | Days 1–5 |
| Ollama | Optional | OpenRouter | Provider-portability lab |
| OpenAI API | Optional | OpenRouter or mock mode | Direct-provider alternative introduced on Day 1 |
| LangSmith | Guided exposure | Structured local logs | Days 3–5 |
| Mem0 Platform | Guided exposure | Custom memory or Mem0 OSS | Day 3 |
| Google Colab | Optional | Local Jupyter | Selected API-based notebooks |

## Account policy

- Core learning must not depend on a paid account.
- Hosted free tiers can change and must not be guaranteed.
- Students create optional accounts only before the day on which they are used.
- Every hosted service must have a local or mock learning path.

## Secret handling

- Store keys in `.env`, never directly in a notebook.
- Do not commit `.env` or paste keys into screenshots.
- Use separate course/test credentials where possible.
- Explain what data is sent to a hosted service before enabling it.
- Revoke any key that is accidentally exposed.

## Classroom model-route policy

OpenRouter with the course-approved GPT-OSS model is the primary classroom route so students receive consistent model capability and iteration speed across different personal computers.

During the first model-call notebook, students are shown three routes:

1. OpenRouter — the default used by the remaining guided notebooks.
2. Ollama — an optional local-provider comparison.
3. OpenAI API — one complete direct-provider example for students who already have API access.
4. Mock mode — a deterministic fallback for testing application logic.

The complete Ollama and direct OpenAI alternatives are not repeated in every notebook. Later guided notebooks use the issued OpenRouter key consistently.

## Instructor-issued OpenRouter keys

Each student receives one named key with:

- USD 1 lifetime spending limit
- No daily, weekly, or monthly reset
- Expiry shortly after the course
- A course model allowlist where account controls permit it

The instructor retains the key hash/label for usage monitoring and revocation. Plaintext keys are returned only at creation and must be distributed privately.

An OpenAI API key belongs to the API platform. A ChatGPT subscription should not be presented as automatically including API credits or API access. Students using this route must verify their own API project and billing settings.

Official quickstart: [OpenAI API developer quickstart](https://platform.openai.com/docs/quickstart)
