# How add and search work inside Mem0

Chapter M2 treated Mem0 as a box. This chapter opens it, because every later decision (what to add,
how to scope, how to test) depends on knowing what happens to a message once it goes in.

## Add: four stages (diagram D66)

When you call `add(messages, user_id=...)`:

1. **Context lookup.** Mem0 fetches what it already holds for that scope, so that extraction can
   avoid restating it.
2. **Fact extraction.** A language model reads the messages and pulls out preferences, decisions,
   plans and other details worth keeping, rewritten as short third-person statements. This is the
   step Day 3.3 made you write by hand with a prompt; here it is a model call you pay for once per
   add.
3. **Deduplication and embedding.** Facts that duplicate existing memories are dropped; the rest are
   embedded into vectors for semantic search.
4. **Entity extraction.** People, places, organisations and concepts in each fact are recorded so
   that later searches can match on them.

Storage is **additive**: new facts do not overwrite or delete old ones. If Asha said "meetings after
10" in March and "meetings before 9 now" in June, both memories exist, each with its timestamp,
until you call `update` or `delete` (chapter M5) or set an expiration. Older Mem0 versions inferred
updates and deletions during add; the current documentation describes the additive model, and the
open-source library's behaviour is the same in spirit. Read your results with that in mind.

There is one switch on this pipeline: `infer=False` skips extraction and stores your text exactly
as given. Use it for facts you already hold in structured form; duplicates then land verbatim.

## Where a memory lives

A memory is spread over three stores that Mem0 manages together:

| Store | Holds | Used for |
|---|---|---|
| SQL database | the fact text, ids, timestamps, metadata, categories, history | the source of truth; `get`, `get_all`, `history` |
| vector database | the embedding of each fact | semantic search |
| entity store | the entities extracted from each fact and the links between them | boosting memories that share entities with the query; "what do we know about Alice?" questions |

On the Platform the entity store is the built-in **graph memory**: nothing to configure, and it
affects ranking rather than the shape of results. The open-source library keeps the SQL history in
SQLite and the vectors in a vector database you choose (chapter M6).

## Scoping: the ids that keep memories apart

Every memory carries identifiers, and every search filters by them. Choose them deliberately.

| Identifier | Meaning | Typical value |
|---|---|---|
| `user_id` | the person the facts are about | your application's user id, never an email address |
| `agent_id` | the agent that learned them, when several agents serve one user | `"support_bot"`, `"tutor"` |
| `run_id` | one session or task, for facts that should not outlive it | a conversation id |
| `app_id` | the application, when one account serves several | `"campus_helpdesk"` |
| `metadata` | anything else, as a dictionary you can filter on | `{"team": "billing", "source": "onboarding_form"}` |

A search with `filters={"user_id": "u1"}` sees only that user's memories. A search with no filter
is a bug in almost every application: it mixes people. Chapter M7 makes this the first item of the
isolation checklist.

## Search: four signals fused (diagram D67)

`search(query, filters=...)` embeds the query and ranks the scoped memories with several signals
at once:

- **Semantic**: vector similarity, so "what can Asha eat" finds "is vegetarian".
- **Keyword**: exact term matching, so names, ids and product codes are not lost to paraphrase.
- **Entity**: memories sharing entities with the query are boosted.
- **Temporal**: time metadata scored against temporal intent, so "when did" questions prefer dated
  memories.

The Platform combines all four; the open-source library uses vector similarity plus entity overlap.
Each result carries a single `score` in which the signals are already fused.

The levers on a search:

| Parameter | Effect |
|---|---|
| `filters` | which memories are eligible at all |
| `top_k` | how many to return (default 10) |
| `threshold` | drop results below this score |
| `rerank=True` | reorder the results with a cross-encoder for better relevance; the only lever that changes order; costs roughly 150 to 200 ms |
| `version="v2"` | the current search API on the Platform SDK, with structured `filters` |

## Reading one result

```json
{
  "id": "0d7c9f2e-...",
  "memory": "Is allergic to nuts",
  "user_id": "course_fictional_asha",
  "categories": ["health", "food"],
  "metadata": {},
  "created_at": "2026-09-05T10:12:44Z",
  "updated_at": "2026-09-05T10:12:44Z",
  "score": 0.71
}
```

`memory` is what you will paste into a prompt. `id` is what `update`, `delete` and `history` take.
`score` is relative, not a probability; compare scores within one search, not across searches.

## What this means for how you call it

- Send the **turn** (user message plus assistant reply) to `add`, not the whole conversation every
  time; the context lookup and deduplication cope with overlap, but you pay one extraction call per
  add.
- Search with the **user's latest message**, not the whole history; the query is embedded as one
  text.
- Always scope. Decide `user_id` and, if you have several assistants, `agent_id` on day one.

## Recap

- Add is context lookup, LLM fact extraction, deduplication and embedding, entity extraction; storage is additive until you update, delete or expire.
- A memory is text in SQL, a vector, and entities; `user_id`, `agent_id`, `run_id`, `app_id` and metadata keep memories apart.
- Search fuses semantic, keyword, entity and temporal signals into one score; `filters`, `top_k`, `threshold` and `rerank` are the levers.
