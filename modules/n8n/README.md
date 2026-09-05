# n8n module — Four agents on a visual canvas

**Outcome:** an n8n Cloud account, the theory needed to read any n8n agent workflow, and four
working agents built click by click: a chat assistant with memory, a research agent with tools, a
support-ticket triage that returns structured data and routes it, and a supervisor that delegates
to specialist workflows.

n8n runs in the browser; nothing is installed. The module is independent of the five days and of
the notebook tracks, although students who have done Day 1 will recognise every concept: the model,
the tool loop, structured output, memory and the supervisor all reappear as boxes on a canvas.

| Chapter | File | You learn | You do |
|---|---|---|---|
| N1 | `01_what_n8n_is.md` | workflows, triggers, nodes, executions, credentials; where agents fit | read a workflow diagram |
| N2 | `02_open_an_n8n_cloud_account.md` | the Cloud trial, the editor, credentials, executions | open an account and get a Gemini key into it |
| N3 | `03_how_an_agent_node_works.md` | the AI Agent node and its sub-nodes, expressions, workflow versus agent | none yet; theory for the four builds |
| N4 | `04_agent_1_chat_assistant_with_memory.md` | Chat Trigger, chat model, Simple Memory, system message | build and test a chat assistant |
| N5 | `05_agent_2_research_agent_with_tools.md` | tools: Wikipedia, Calculator, HTTP Request, `$fromAI` | build an agent that looks things up and computes |
| N6 | `06_agent_3_ticket_triage_with_structured_output.md` | Form Trigger, Structured Output Parser, IF, Gmail and Google Sheets | build a triage workflow that routes by urgency |
| N7 | `07_agent_4_supervisor_and_running_agents_well.md` | Call n8n Workflow Tool, sub-workflows, limits, errors, cost, export | build a supervisor with two specialists; operate it |

Diagrams D53 to D56 in [`diagrams/source/n8n.md`](../../diagrams/source/n8n.md).
