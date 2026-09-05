# Agent 4: a supervisor with specialist workflows, and running agents well

The last build is a small multi-agent system (diagram D56): a supervisor that talks to the user and
delegates to two specialist workflows, each of which is an agent of its own. The second half of the
chapter is about operating what you have built: limits, failures, cost and export.

## Build the specialists first

A workflow becomes a tool for another workflow when it starts with the trigger **When Executed by
Another Workflow**. Build two.

### Specialist A: Researcher

1. New workflow `Specialist - Researcher`. Add **When Executed by Another Workflow**; set *Input
   data mode* to *Define using fields below* and add one field `question` (string).
2. Add **AI Agent**, *Prompt* → *Define below* → `{{ $json.question }}`. Attach Gemini, the
   **Wikipedia** tool and the **Calculator** tool. System message: `Answer factual questions with
   sources from Wikipedia. Reply in at most 80 words.`
3. **Save**. Nothing else; the agent's output is what the caller receives.

### Specialist B: Writer

1. New workflow `Specialist - Writer`, same trigger, one input field `brief` (string).
2. **AI Agent** with `{{ $json.brief }}` as prompt, Gemini underneath, no tools. System message:
   `Turn the brief into a friendly three-sentence message for a general audience. Do not add facts.`
3. **Save**.

## Build the supervisor

1. New workflow `Agent 4 - Supervisor`. **When chat message received → AI Agent**, Gemini, Simple
   Memory.
2. Attach two **Call n8n Workflow Tool** sub-nodes to the Tool socket:
   - Name `researcher`, *Workflow* → `Specialist - Researcher`, description: `Finds and checks
     facts. Give it one clear question.` Map the input `question` to *Let the model define this
     parameter*.
   - Name `writer`, *Workflow* → `Specialist - Writer`, description: `Turns checked facts into a
     short friendly message. Give it the facts as a brief.` Map `brief` the same way.
3. System message:

```text
You are a supervisor. You do not answer factual questions yourself.
For facts, call researcher. To phrase a message for a reader, call writer with the facts you have.
Return the writer's text to the user, followed by one line naming the tools you used.
```

4. **Save**, open **Chat**, and send:

```text
Write a short welcome note for new students that mentions when the University of Bologna was founded.
```

Open **Executions**. The supervisor's run shows two tool calls; each specialist workflow has its own
execution in its own list, with its own model calls. That separation is the reason to build it this
way: each specialist can be tested alone from its editor with a sample input, versioned alone, and
given only the tools it needs. Day 4 of the course measures when this is worth the extra calls;
here you can see the cost directly in the execution counts.

## Running agents well

**Limits.** Every AI Agent has *Max Iterations*; every workflow has a timeout (Settings → *Timeout
Workflow*). Set both. A looping agent with an HTTP tool can burn hundreds of calls in a minute.

**Errors.** In workflow Settings, choose an **Error Workflow**: a separate workflow with an *Error
Trigger* that emails or messages you when any run fails. For tool nodes, the node's Settings tab has
*On Error* → *Continue* so one failed lookup does not kill the run; the model then sees the error
text and can try something else, which is the *handle_tool_errors* idea from the LangGraph track.

**Cost.** Two meters: n8n executions (each run of each workflow counts once, sub-workflows included)
and model tokens (in the Gemini node's output for every call). A supervisor with two specialists is
three executions and at least four model calls per question. Prefer a single agent with tools until
you can name what the split buys.

**Guardrails.** The system message is not a security boundary. Anything the user types is in the
same message list as your instructions, and a tool that fetches a web page brings the page's text
into that list too. Give agents only the tools the task needs, keep write actions (send email,
append row) behind an IF node or a human approval step (n8n has a *Wait* node and Slack/Gmail
approval nodes for exactly this), and read the Day 3 sections on permissions when you build anything
that acts.

**Sessions in production.** Simple Memory is per-instance and not durable. For a Telegram bot,
swap the Chat Trigger for **Telegram Trigger**, use the chat id as the memory session key, and add
a **Telegram** *send message* node after the agent.

**Export and import.** Workflow menu (three dots, top right) → **Download** gives a JSON file of the
drawing, credentials excluded. **Import from file** in the same menu restores it anywhere, including
a self-hosted n8n after the trial ends. Export all four agents now.

## Where this connects

| n8n | Course |
|---|---|
| AI Agent node with tools | Day 1 tool loop; LangChain `create_agent` |
| Structured Output Parser | Day 1 structured output |
| Simple Memory, session id | Day 3 conversation memory |
| Call n8n Workflow Tool | Day 4 specialists and supervisor; LangGraph subgraphs |
| Max Iterations, timeouts, Error Workflow | Day 3 and Day 5 limits and observability |

## Recap

- A workflow that starts with *When Executed by Another Workflow* becomes a tool; a supervisor calls two of them through *Call n8n Workflow Tool*.
- Each specialist runs, is tested and is billed as its own execution.
- Set Max Iterations and timeouts, add an error workflow, keep write actions behind checks, and export your workflows as JSON.
