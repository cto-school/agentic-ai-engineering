# How the AI Agent node works

This chapter is the theory the four builds rest on. It is short because the concepts are the ones
from Day 1 of the course, seen from the outside.

## Anatomy of the agent node (diagram D54)

The **AI Agent** node has one input line on its left (the user's message, or any item), one output
on its right (the final answer), and up to four sockets underneath. Sub-nodes plug into those
sockets; they have no lines of their own.

| Socket | Sub-node examples | Role |
|---|---|---|
| **Chat Model** (required) | Google Gemini Chat Model, OpenRouter Chat Model, OpenAI Chat Model, Anthropic Chat Model, Ollama Chat Model | the model that reads the conversation and decides |
| **Memory** (optional) | Simple Memory, Postgres Chat Memory, Redis Chat Memory | previous turns, keyed by a session id |
| **Tool** (optional, many) | Calculator, Wikipedia, HTTP Request Tool, Code Tool, Google Sheets Tool, Gmail Tool, Call n8n Workflow Tool, Think Tool | functions the model may ask to run |
| **Output Parser** (optional) | Structured Output Parser | forces the final answer into a JSON schema |

Inside, the node runs the loop from Day 1 section 1.5:

1. Build the message list: the **System Message** from the node's options, the memory's stored
   turns, and the incoming user text.
2. Send it to the chat model together with the schemas of every attached tool.
3. If the model replies with a tool request, run that tool sub-node, append the result as a tool
   message, and go to step 2.
4. If the model replies with text, store the turn in memory and emit it as the node's output.

The node's **Max Iterations** option (default 10) is the step limit from the manual loop: the number
of times round steps 2 and 3 before n8n stops the agent and raises an error.

## The four settings that matter

- **Prompt (User Message).** By default *Connected Chat Trigger Node*, which reads `chatInput` from
  a Chat Trigger. Choose *Define below* to build the message from any data, for example a form
  field or an email body.
- **System Message** (under *Options*). Who the agent is, what it may and may not do, how to
  format answers. Everything the course says about system prompts applies; this is where most
  behaviour is fixed.
- **Require Specific Output Format.** Enables the Output Parser socket. With a Structured Output
  Parser attached, the node validates the final answer against a JSON schema and retries once if it
  fails. This is Day 1's structured output, as a checkbox.
- **Max Iterations.** Lower it to 5 for tools that cost money; raise it for research agents.

## How tools describe themselves

A tool sub-node carries a **name** and a **description**. The model sees only those two things and
the tool's parameters. The description is the whole reason the model picks the right tool, so write
it the way you would explain the tool to a new colleague: *"Looks up the current weather for a city.
Use when the user asks about weather, temperature or rain."*

Where do a tool's arguments come from? Any parameter of a tool node can be set to
**Let the model define this parameter** (the `$fromAI(...)` expression). The model then fills that
field when it calls the tool. You will use it in N5 to let the agent choose the city to look up.

## Memory and sessions

Memory is keyed by a **session id**. The Chat Trigger provides one per chat window; a Telegram
trigger uses the chat id; a form has none, so form-triggered agents are stateless unless you supply
a key. **Simple Memory** keeps the last *N* turns (its *Context Window Length*) in n8n's own
storage; it is enough for this module and disappears when the workflow is edited or the instance
restarts. Database-backed memories survive restarts.

## Workflow or agent? Reading a canvas

When you open someone else's n8n workflow, ask of each model box:

- Is it a **Basic LLM Chain** with one model underneath? A fixed step: the model answers once and
  the line continues. The workflow author made every routing decision.
- Is it an **AI Agent** with tools underneath? The model makes some decisions. Look at the system
  message and the Max Iterations to see how tightly it is held.

Both are fine. Chapter N6 deliberately uses the agent node for a job a chain could do, so that you
see the structured output mechanism; a production version would likely use the chain.

## Recap

- The AI Agent node is the Day 1 loop in a box: model, memory, tools and an optional output parser plug in underneath.
- The System Message, the tool descriptions and Max Iterations are the three levers on its behaviour.
- Tool parameters can be filled by the model with *Let the model define this parameter*; memory needs a session id.
