# Why agents need a memory layer, and what Mem0 is

A language model remembers nothing between calls. Every notebook in this course sends the whole
message list every time, and Day 3 spends a morning on what to do when that list grows too long.
Memory, for an agent, is never inside the model; it is something your program keeps and feeds back.
**Mem0** is a product that does that keeping for you.

## Three kinds of memory, one problem each

| Kind | Question it answers | Where the course builds it |
|---|---|---|
| **Conversation memory** | what was said in *this* session | Day 3.1 and 3.2: the message list, trimmed and summarised |
| **Long-term memory** | what we know about *this person or agent* across sessions | Day 3.3: a small store of facts with a lifecycle |
| **Knowledge** | what is true in the world or the company | Day 2: retrieval over documents |

Mem0 is about the middle row. Its job is to turn raw conversations into durable facts about a user
("prefers meetings after 10:00", "is allergic to nuts", "works on the billing service"), keep them
per person, and hand back the relevant ones when a new conversation starts. It is not a knowledge
base and not a chat history, although it can be misused as either.

## What a memory layer does (diagram D65)

Sitting beside the agent loop, a memory layer offers four operations:

1. **add**: give it the messages of a turn; it extracts facts worth keeping and stores them.
2. **search**: give it the new user message; it returns the stored facts that are relevant.
3. **get, update, delete**: inspect and change what it holds, per memory or per user.
4. **history**: see how a memory changed over time.

The agent calls *search* before it calls the model and puts the results into the system prompt,
then calls *add* after the reply. Chapter M4 is exactly that pattern; chapters M2 and M3 are what
happens inside *add* and *search*.

What the layer removes from your code is the part Day 3.3 made you write by hand: deciding which
sentences are facts, writing them in a normal form, deduplicating, embedding, filtering by user,
ranking. What it does **not** remove, and Day 3.4 already warned you about, is consent, isolation
between users, retention, deletion on request, and deciding what is worth remembering at all.
Chapter M7 returns to those.

## Three ways to run it

| | Mem0 Platform | Open-source library | Self-hosted server |
|---|---|---|---|
| where memories live | Mem0's cloud | your process, on your disk | your machine or server, in Postgres |
| what you need | an API key | Python, an LLM and an embedder (Ollama works) | Docker |
| retrieval | semantic + keyword + entity + temporal signals, reranking | vector search plus entity overlap | the same server code as the Platform's API shape |
| dashboard | yes | no | yes |
| cost | free tier, then per memory and per call | your own compute and model calls | your own compute and model calls |
| best for | products and this module's first half | laptops, experiments, privacy-first setups | teams that need the API and dashboard on their own hardware |

The module uses the **Platform** for chapters M2 to M5 because it needs no installation and shows
the fullest feature set, then chapter M6 runs the **library** on a laptop with the Gemma model from
the Ollama module and stands up the **server** with one command. Everything you learn about add,
search and scoping is the same in all three.

## What you will need

- A Mem0 account (free) and an API key: chapter M2.
- Python 3.10 or newer with `pip install mem0ai`, or curl. The calls are five lines; there is no
  agent code to write until chapter M4, and even that is a dozen lines.
- For chapter M6, Ollama with `gemma3:4b` and an embedding model, or Docker.

## Recap

- Memory lives outside the model; a memory layer keeps durable facts per user and returns the relevant ones on demand.
- Mem0 gives you add, search, get, update, delete and history; it removes extraction and retrieval plumbing, not your responsibilities for consent, isolation and retention.
- Platform for the fastest start, the open-source library for a laptop, the self-hosted server for your own infrastructure; the operations are identical.
