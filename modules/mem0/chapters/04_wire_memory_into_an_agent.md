# Wire memory into an agent

The integration is one pattern, and it is the same in a bare loop, in LangGraph, in n8n or in any
framework: **search before the model, add after the reply** (diagram D68). This chapter shows it
three times at increasing levels of packaging.

## The pattern in plain Python

```python
import os
from openai import OpenAI
from mem0 import MemoryClient

model = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
memory = MemoryClient(api_key=os.environ["MEM0_API_KEY"])

def reply(user_id: str, user_text: str, history: list[dict]) -> str:
    # 1. Search: what do we already know that is relevant to this message?
    hits = memory.search(user_text, filters={"user_id": user_id}, top_k=5)
    facts = "\n".join(f"- {hit['memory']}" for hit in hits["results"])

    # 2. Put the facts in the system prompt, clearly labelled as background.
    system = ("You are a helpful assistant.\n"
              "Relevant information from previous conversations:\n" + (facts or "- none"))
    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": user_text}]

    # 3. Call the model as usual.
    answer = model.chat.completions.create(model="openai/gpt-oss-120b", messages=messages).choices[0].message.content

    # 4. Add the turn so that the next conversation can use it.
    memory.add([{"role": "user", "content": user_text}, {"role": "assistant", "content": answer}], user_id=user_id)
    return answer
```

Try it with the fictional user from M2: first a conversation that states a preference, then, in a
fresh `history`, a question that depends on it. The second conversation knows the answer even though
its message list never contained the first.

Four decisions are hidden in those lines:

- **Where the facts go.** Into the system prompt, under a heading that says what they are. Models
  treat unlabelled facts as instructions; "Relevant information from previous conversations" tells
  the model they are background.
- **How many.** `top_k=5`. More facts cost tokens and dilute attention; Day 3's context budget
  applies.
- **What to add.** The turn pair, after the reply. Adding the whole history every turn re-extracts
  the same facts and pays for it.
- **When not to add.** Skip `add` for turns that are pure task chatter ("thanks", "run it again").
  A cheap rule such as "only add turns longer than a few words" saves most of the extraction cost.

## The same pattern as a LangGraph node

The LangGraph track's CampusAI graph has a chatbot node that reads `state["messages"]` and calls
the model. Memory slots in around that call. The user id travels in the state so that every node
sees it:

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
    mem0_user_id: str

def chatbot(state: State):
    messages = state["messages"]
    user_id = state["mem0_user_id"]
    memories = mem0.search(messages[-1].content, filters={"user_id": user_id})   # search first
    context = "Relevant information from previous conversations:\n" + "\n".join(
        f"- {m['memory']}" for m in memories["results"])
    system = SystemMessage(content="You are a helpful assistant.\n" + context)
    response = llm.invoke([system] + messages)                                     # then the model
    mem0.add([{"role": "user", "content": messages[-1].content},
              {"role": "assistant", "content": response.content}], user_id=user_id)  # then add
    return {"messages": [response]}
```

Nothing else in the graph changes. Persistence of the *conversation* is still the checkpointer's
job (LangGraph track G5); Mem0 holds what should survive *across* threads (G6 used a store for the
same purpose, by hand). If you want the agent to decide when to remember, expose `add` and
`search` as tools instead of calling them in the node; the trade-off is the one Day 3 draws between
a deterministic policy and a model's judgement.

## In n8n, with the HTTP Request node

The n8n module's chat assistant (N4) becomes memory-backed with two HTTP Request nodes around the
AI Agent, both using a header credential `Authorization: Token <key>`:

1. Before the agent: **POST** `https://api.mem0.ai/v3/memories/search/` with body
   `{"query": "{{ $json.chatInput }}", "filters": {"user_id": "{{ $json.sessionId }}"}}`.
   Then an **Edit Fields** node that joins `results[].memory` into one string.
2. In the agent's system message: `Relevant information from previous conversations: {{ $('Edit Fields').item.json.facts }}`.
3. After the agent: **POST** `https://api.mem0.ai/v3/memories/add/` with the user message and the
   agent's `output` as two messages and the same `user_id`.

Use a stable user id from your trigger (Telegram chat id, form email hash), not the Chat Trigger's
session id, or memory resets with every chat window.

## Scoping in practice

- One assistant, many users: `user_id` only.
- Several assistants for the same user (a tutor and a scheduler): add `agent_id`, so the tutor does
  not surface scheduling facts, and search with both.
- Facts that should die with the task ("for this ticket, the customer is on plan B"): add with
  `run_id`, and never search them from another run.

## Recap

- Search with the latest user message, label the results as background in the system prompt, call the model, then add the turn pair.
- In LangGraph the user id rides in the state and the node wraps the model call; the checkpointer still owns the conversation.
- In n8n the same two REST calls sit around the AI Agent node; scope every call with a stable user id.
