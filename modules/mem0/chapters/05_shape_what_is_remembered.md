# Shape what is remembered

Out of the box Mem0 remembers whatever its extraction model finds noteworthy. For a real
application that is both too much (it will keep "user said thanks") and too little (it does not know
that your domain cares about "preferred database engine"). These Platform features put you in
charge, and each maps to a call or a dashboard setting.

## Custom instructions: tell the extractor what matters

A project-level instruction steers extraction for every add. Set it once in the dashboard
(**Project → Custom instructions**) or with the client:

```python
client.update_project(custom_instructions="""
Remember the user's dietary restrictions, allergies, scheduling preferences,
and which product features they use.
Do not remember greetings, small talk, or one-off task details.
Never store payment card numbers or passwords, even if the user says them.
""")
```

The instruction is added to the extraction prompt. It is the memory equivalent of the system
message: strong influence, not enforcement, so the last line is a defence in depth and chapter M7
adds a check in code.

## Custom categories: name your domain

Memories are tagged with categories automatically (`food`, `health`, `preferences`, `work`).
Replace or extend the set with your own so that dashboards and filters speak your language:

```python
client.update_project(custom_categories=[
    {"dietary": "food restrictions, allergies and preferences"},
    {"scheduling": "availability, time-zone and meeting preferences"},
    {"product_usage": "features the user relies on or has trouble with"},
])
```

Search results then carry these names in `categories`, and `get_all` can filter on them.

## Metadata: facts about the fact

Anything you know when you call `add` can ride along and be filtered later:

```python
client.add(messages, user_id="course_fictional_asha",
           metadata={"source": "onboarding_form", "team": "billing", "confidence": "stated"})
```

Filtering is structured (`filters={"AND": [{"user_id": "..."}, {"metadata": {"team": "billing"}}]}`),
so metadata is how you build "only facts from verified sources" or "only this team's context".

## Expiration: memories with a shelf life

A fact that is true for a month should not surface in a year. `expiration_date` keeps the memory
but stops it from being returned after the date:

```python
client.add([{"role": "user", "content": "I'm travelling until the 20th, reply by email only."}],
           user_id="course_fictional_asha", expiration_date="2026-09-20")
```

Expired memories remain visible in `get_all` and the dashboard for audit; they simply stop being
relevant. This is the retention lever chapter M7 asks you to decide on.

## Update, delete, history

When a fact changes, change the memory rather than adding a contradiction:

```python
memory_id = hits["results"][0]["id"]
client.update(memory_id, text="Prefers meetings before 09:00")
client.history(memory_id)          # every version, with timestamps
client.delete(memory_id)           # one memory
client.delete_all(user_id="course_fictional_asha")   # everything about one user
```

`history` is what you show an auditor or a user who asks "why does it think that?". `delete_all`
per user is the right-to-erasure operation.

## Export: get your data out

Memories can be exported in a schema you define, so that a migration to the open-source library or
to your own store never depends on the dashboard:

```python
job = client.create_memory_export(schema={"memory": "str", "categories": "list[str]", "created_at": "str"},
                                  filters={"user_id": "course_fictional_asha"})
export = client.get_memory_export(memory_export_id=job["id"])
```

Day 3.4's comparison table listed "an export you must request" against the hosted service; this is
that request.

## Webhooks and the asynchronous client

Because adds are processed asynchronously, two mechanisms let a system react without polling:

- **Webhooks** (dashboard → Project → Webhooks): Mem0 calls a URL of yours on memory add, update
  or delete. An n8n Webhook trigger is a fine receiver for a first experiment.
- **`AsyncMemoryClient`**: the same methods as `MemoryClient`, awaitable, for agents that already run
  on an event loop and want to fire `add` without waiting.

```python
from mem0 import AsyncMemoryClient
client = AsyncMemoryClient(api_key=os.environ["MEM0_API_KEY"])
await client.add(messages, user_id="course_fictional_asha")
```

## A tuning routine

1. Run twenty realistic conversations for a fictional user through `add`.
2. Read `get_all` in the dashboard. Mark each memory *keep*, *noise* or *missing*.
3. Fix noise and missing with custom instructions; fix vocabulary with categories.
4. Delete all, re-run, and count again. Stop when noise is rare and nothing important is missing.

Chapter M7 turns step 2 into a repeatable test.

## Recap

- Custom instructions steer extraction; custom categories name your domain; metadata makes facts filterable.
- Expiration retires facts on a date; update, delete and history change and explain them; export gets them out.
- Webhooks and the async client fit memory into event-driven systems; tune with a twenty-conversation review.
