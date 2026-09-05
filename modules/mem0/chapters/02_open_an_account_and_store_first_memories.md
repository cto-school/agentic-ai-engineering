# Open a Mem0 account and store your first memories

By the end of this chapter a fictional user has three memories on the Platform, you have searched
them, looked at them in the dashboard, and deleted them.

## 1. Account and API key

1. Go to [app.mem0.ai](https://app.mem0.ai) and sign up with an email address, Google or GitHub.
2. In the dashboard, open **Settings → API keys** and create a key. Copy it once; it is shown once.
3. Store it where the course keeps keys: a Colab secret named `MEM0_API_KEY`, an environment
   variable, or a `.env` file. Never paste it into a cell or a chat.

The free tier covers this module many times over. Usage is counted in memories stored and API
calls; the dashboard's usage page shows both.

## 2. Install and connect

```bash
pip install mem0ai
```

```python
import os
from mem0 import MemoryClient

client = MemoryClient(api_key=os.environ["MEM0_API_KEY"])
```

## 3. Add a conversation

Mem0 takes **messages**, the same role and content list you send to a model, and extracts what is
worth keeping. Use a fictional user id; the course rule about synthetic data applies to every
hosted service.

```python
messages = [
    {"role": "user", "content": "I'm Asha. I'm vegetarian, allergic to nuts, and I prefer meetings after 10:00."},
    {"role": "assistant", "content": "Noted: vegetarian, nut allergy, meetings after 10."},
]
result = client.add(messages, user_id="course_fictional_asha")
print(result)
```

The Platform processes adds **asynchronously**: the reply is a status of `PENDING` with an
`event_id`. Extraction takes a few seconds. You can poll `GET /v1/event/{event_id}/` for
completion, or wait a moment and search.

## 4. Search

```python
hits = client.search("What can Asha eat?", filters={"user_id": "course_fictional_asha"})
for hit in hits["results"]:
    print(round(hit["score"], 2), hit["memory"])
```

Expected, in some order:

```text
0.8  Is vegetarian
0.7  Is allergic to nuts
```

Three things to notice: the memories are **facts in the third person**, not your sentences; the
meeting preference did not come back because it is not relevant to the question; and every call
carries `filters={"user_id": ...}`, without which you would search across everyone.

Now list everything the user has, regardless of relevance:

```python
everything = client.get_all(filters={"user_id": "course_fictional_asha"})
for memory in everything["results"]:
    print(memory["id"], "|", memory["memory"], "|", memory.get("categories"))
```

Each memory has an id, a text, timestamps, and automatically assigned categories such as
`food`, `health` or `preferences`.

## 5. The same thing with curl

The SDK is a thin wrapper over a REST API. Adding:

```bash
curl -X POST https://api.mem0.ai/v3/memories/add/ \
  -H "Authorization: Token $MEM0_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Asha works on the billing service."}],
       "user_id": "course_fictional_asha"}'
```

Searching:

```bash
curl -X POST https://api.mem0.ai/v3/memories/search/ \
  -H "Authorization: Token $MEM0_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What does Asha work on?", "filters": {"user_id": "course_fictional_asha"}}'
```

On Windows use `curl.exe` or `Invoke-RestMethod`, as in the Ollama module. n8n's HTTP Request node
sends exactly these requests (chapter M4).

## 6. Look in the dashboard

Open **Memories** in the dashboard and filter by the user id. You see the same rows, with the source
messages each memory was extracted from and a per-memory history. This is your first debugging tool
when an agent "remembers wrong": find the memory, read what it was extracted from, and decide
whether the extraction or the prompt was at fault.

## 7. Clean up

```python
client.delete_all(user_id="course_fictional_asha")
```

Do this at the end of every experiment. Deleting per user is also the operation you will need when a
real person asks to be forgotten (chapter M7).

## Recap

- Sign up at app.mem0.ai, create an API key, keep it in a secret; `pip install mem0ai` and `MemoryClient`.
- `add(messages, user_id=...)` extracts third-person facts asynchronously; `search(query, filters={"user_id": ...})` returns the relevant ones with scores; `get_all` lists them.
- The dashboard shows every memory with its source; `delete_all(user_id=...)` cleans up.
