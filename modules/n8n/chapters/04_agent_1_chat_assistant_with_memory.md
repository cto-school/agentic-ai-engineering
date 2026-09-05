# Agent 1: a chat assistant with memory

Three nodes. When it works, you have used the model socket, the memory socket and the system
message, and you can test any agent from the built-in chat window.

## Build it

1. **Create a workflow** and name it `Agent 1 - Chat assistant`.
2. Click the plus button, search **Chat Trigger**, and add **When chat message received**. Leave
   its settings alone. A **Chat** button appears at the bottom of the canvas.
3. Click the plus on the trigger's output line, search **AI Agent**, add it. Its *Prompt* is
   already *Connected Chat Trigger Node*.
4. Click the **Chat Model** socket under the agent (the plus with a model icon). Search
   **Google Gemini Chat Model** and add it. Select the credential from N2. In **Model**, pick
   `models/gemini-2.5-flash` or the newest *flash* model listed.
5. Click the **Memory** socket. Add **Simple Memory**. Leave *Session ID* on *Connected Chat
   Trigger Node* and *Context Window Length* at 5.
6. Open the AI Agent node, expand **Options**, add **System Message**, and paste:

```text
You are Studybuddy, a tutor for a course on AI agents.
Explain in plain language, at most 120 words per reply.
When the student asks something you cannot know (their personal data, live facts),
say so instead of guessing.
```

7. **Save**.

The canvas reads: *When chat message received → AI Agent*, with *Google Gemini Chat Model* and
*Simple Memory* hanging underneath the agent.

## Test it

Open the **Chat** panel at the bottom and send three messages in order:

```text
My name is Aurora and I am studying tool calling.
What is a tool call?
What was my name again?
```

The third answer should be "Aurora". Now open the *Simple Memory* node: its output shows the stored
turns. Set *Context Window Length* to 1, click **Chat** again with a fresh session (the refresh
icon in the chat panel), repeat the three messages, and watch the assistant forget. That is the
memory socket doing exactly what the message list did in Day 1 section 1.1: the model has no
memory; the host supplies it.

## Read the execution

Open the **Executions** tab and click the latest run. Click the AI Agent node: the left panel shows
the input item (`chatInput`, `sessionId`), the right shows `output`. Click the Gemini node: you see
the exact message list that was sent, system message first, and the token usage. This view is the
equivalent of printing `messages` in the notebook, and you will use it in every later chapter.

## Make it public (optional)

The Chat Trigger has a **Make Chat Publicly Available** option. Switch it on, set *Mode* to
*Hosted Chat*, **Save**, switch the workflow to **Active**, and the trigger shows a URL you can open
in another browser or send to a friend. Turn it off again when done: every message someone sends
costs an execution and a model call.

## Variations to try

- Replace *Google Gemini Chat Model* with **OpenRouter Chat Model** and the model
  `openai/gpt-oss-120b` to use the course's key and model.
- Add a second system-message rule ("Always end with a question") and confirm it holds across turns.
- Set the Gemini node's *Temperature* (under Options) to 0 and send the same question twice.

## Recap

- Chat Trigger → AI Agent, with a chat model and Simple Memory underneath, is the smallest agent.
- Memory is a sub-node keyed by session; shrink its window and the assistant forgets, exactly as in Day 1.
- The Executions tab shows the real message list and token counts for every model call.
