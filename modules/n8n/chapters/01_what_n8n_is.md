# What n8n is, and where agents fit in it

**n8n** is a workflow automation tool. You draw a workflow on a canvas: a box that starts it, boxes
that do something, and lines that pass data between them. n8n then runs that drawing, every time
the start condition happens, without you writing the plumbing. It has several hundred ready-made
boxes for services such as Gmail, Google Sheets, Slack, Telegram, HTTP APIs and databases, and,
since 2024, a set of boxes for language models and agents.

If you have done Day 1 of this course, think of n8n as the host application from diagram D01, drawn
instead of coded.

## The five words you need (diagram D53)

- **Workflow.** One drawing. It has a name, an on/off switch, and a version history.
- **Trigger.** The first node. It decides *when* the workflow runs: a chat message arrives, a form
  is submitted, a schedule fires, a webhook is called, a Telegram message comes in.
- **Node.** Any box. Each node receives items, does one thing, and passes items on. An *HTTP
  Request* node calls a URL; a *Google Sheets* node appends a row; an *IF* node sends items down
  one of two branches.
- **Item.** The unit of data flowing along a line: one JSON object. Nodes usually receive a list
  of items and process each one. A form submission is one item; reading a sheet gives one item per
  row.
- **Execution.** One run of a workflow, from trigger to end. n8n records every execution with the
  input and output of every node, which is your debugger.

Two more you meet in chapter N2: **credentials** (API keys and logins stored once and reused by
nodes) and **expressions** (`{{ $json.email }}`, a way to refer to data from earlier nodes inside a
node's settings).

## Cloud versus self-hosted

n8n is open source. You can run it on your own machine or server (a single Docker command), or use
**n8n Cloud**, where the n8n company hosts it for you. This module uses n8n Cloud because it needs
no installation and gives every student the same environment. Everything you build exports as a
JSON file that imports unchanged into a self-hosted n8n later.

The one practical difference for this course: n8n Cloud runs on n8n's servers, so it cannot reach a
model running on your laptop through Ollama. Cloud workflows use hosted models, and this module
uses Google's Gemini through a free API key.

## Where the agent goes

n8n's **AI Agent** node is a box that contains the loop you wrote by hand in Day 1: it sends the
conversation to a model, and if the model asks for a tool, n8n runs the tool and sends the result
back, until the model produces a final answer. The model, the memory and the tools are plugged into
the bottom of the agent node as *sub-nodes*, which is the subject of chapter N3.

This gives you two ways to use a model in n8n, and the difference is the same one this course draws
everywhere:

- A **workflow with a model step in it**: the path is fixed; a *Basic LLM Chain* node asks the model
  one question and the next node always runs. Predictable, cheap, easy to debug.
- An **agent**: the model chooses which tools to call and when to stop. Flexible, and in need of the
  limits and checks the rest of this course teaches.

Most real n8n automations are the first kind with a little of the second inside them. The four
builds in this module are agents because the agent node is what needs explaining; you will see
where a plain chain would have done.

## What you are going to build

| Chapter | Agent | Trigger | Sub-nodes | The idea it demonstrates |
|---|---|---|---|---|
| N4 | Chat assistant | chat message | Gemini + Simple Memory | model and memory |
| N5 | Research agent | chat message | Gemini + Wikipedia + Calculator + HTTP Request | the tool loop |
| N6 | Ticket triage | form submission | Gemini + Structured Output Parser, then IF | structured output and routing |
| N7 | Supervisor | chat message | Gemini + two workflows used as tools | delegation to specialists |

## Recap

- n8n runs drawings: a trigger, nodes that each do one thing, items flowing between them, and a recorded execution per run.
- n8n Cloud needs no installation; this module uses it with a Gemini API key, because cloud servers cannot reach a local Ollama.
- The AI Agent node holds the tool loop; its model, memory and tools plug in underneath as sub-nodes.
