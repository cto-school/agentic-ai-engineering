# Agent 3: ticket triage with structured output

The first two agents talked to a person. This one is a step in a process: a support form comes in,
the model classifies it into a fixed shape, and ordinary nodes route it (diagram D55). It shows the
Output Parser socket and the difference between the model deciding and your workflow deciding.

## Build it

### Trigger: a form

1. New workflow, `Agent 3 - Ticket triage`.
2. Add **On form submission** (the Form Trigger). Set *Form Title* to `Support request` and add
   three fields: `name` (text), `email` (email), `message` (textarea, required).
3. The node shows a **Test URL**. Open it in a new tab: the form exists already.

### The agent, with a schema

4. Add **AI Agent** after the trigger. Set *Prompt* to **Define below** and write:

```text
Classify this support request.
From: {{ $json.name }} <{{ $json.email }}>
Message: {{ $json.message }}
```

5. Attach **Google Gemini Chat Model** as before.
6. In the agent node, switch on **Require Specific Output Format**. An **Output Parser** socket
   appears. Attach **Structured Output Parser**, choose *Define using JSON Schema*, and paste:

```json
{
  "type": "object",
  "properties": {
    "category": { "type": "string", "enum": ["billing", "bug", "how-to", "other"] },
    "urgency": { "type": "string", "enum": ["low", "normal", "high"] },
    "summary": { "type": "string", "description": "one sentence, in the third person" },
    "reply_draft": { "type": "string", "description": "a polite two-sentence reply to the customer" }
  },
  "required": ["category", "urgency", "summary", "reply_draft"]
}
```

7. System message for the agent:

```text
You triage support requests for a small software company.
Urgency is high only if the customer cannot use the product at all or mentions data loss or payment failure.
Never promise refunds or dates in the reply draft.
```

Run **Execute workflow** and submit the form from the test tab with a message such as
*"I was charged twice this month and the app will not open."* The agent's output is a JSON object
with the four fields, validated against the schema. Submit nonsense and it still returns the shape,
because the parser retries once with the validation error when the first attempt fails.

### Routing by ordinary nodes

8. Add an **IF** node after the agent: condition `{{ $json.output.urgency }}` *is equal to* `high`.
9. On the **true** branch add **Gmail** (action *Send a message*), sign in with a Google account
   when it asks for credentials, and set:
   - *To*: your own address for now.
   - *Subject*: `URGENT: {{ $('AI Agent').item.json.output.category }} from {{ $('On form submission').item.json.name }}`
   - *Message*: `{{ $('AI Agent').item.json.output.summary }}`
10. On the **false** branch add **Google Sheets** (action *Append row*). Create a sheet with the
    columns `date, name, email, category, urgency, summary` and map each column from the earlier
    nodes with drag-and-drop; the date is `{{ $now.toISO() }}`.

If you would rather not connect Google accounts, replace both with **Edit Fields (Set)** nodes
that write a `route` field; the routing logic is the point, not the destination.

11. **Save**, then submit the form twice from the test tab: one urgent message, one how-to
    question. One email, one row.

## Why the shape matters

The model chose the category and the urgency. Nothing else in the workflow was decided by a model.
The IF node reads an enum that can only be `low`, `normal` or `high`, so the branch is always
well-defined; the Sheets node writes columns that always exist. Compare with letting the model write
free text and asking a second model call whether it looks urgent: the structured contract is
cheaper, testable and cannot invent a fourth branch. This is diagram D02 from Day 1 with the
validation done by the parser sub-node.

Note also what the agent did not do: it called no tools. A **Basic LLM Chain** with the same output
parser would have served, and in production you would use it. The agent node was used here so that
the *Require Specific Output Format* switch was seen in place.

## Make it real

Set the workflow to **Active** and the Form Trigger's **Production URL** becomes a public form.
Every submission is one execution. Deactivate when done.

## Recap

- Form Trigger → AI Agent with a Structured Output Parser gives a validated JSON object with enum fields.
- IF, Gmail and Google Sheets then route deterministically; the model decided the fields, the workflow decided the path.
- A Basic LLM Chain does the same when no tools are needed; use the agent node only for the loop.
