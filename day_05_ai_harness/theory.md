# Day 5 Theory - Runtime, Harness and MCP

> Instructor authoring source. Students receive this material embedded in the relevant notebooks and are not expected to read this file.

## Why consolidate the earlier projects

By Day 5, several applications repeat the same responsibilities: load model
configuration, describe tools, validate arguments, enforce policy, limit steps, record
events and save continuation state. Copying this code into every agent makes safety fixes
inconsistent. A reusable runtime centralises the execution lifecycle.

This course uses **harness** as an umbrella term for the environment around an agent. In
industry, related terms include agent runtime, orchestration layer and agent platform.
The exact vocabulary varies; the responsibilities are transferable.

## Configuration versus runtime

An agent configuration describes application-specific behavior: instructions, allowed
tools, model settings and limits. The runtime executes that configuration. A research
agent and a safe task agent should use one runtime without sharing inappropriate tools or
permissions.

A provider adapter hides API-specific request and response shapes behind a small
interface. Switching mock, OpenRouter or Ollama should not rewrite policy or the registry.
Provider metadata such as tokens, cost, latency and errors should still be preserved in
events.

## Registry, validation and policy

A tool registry stores names, descriptions, input schemas, executors and local risk
classifications. Discovery answers "what capabilities are visible?" Validation answers
"are these arguments structurally acceptable?" Policy answers "may this agent execute
this action now?" These are separate decisions.

The runtime should fail closed on unknown tools, invalid arguments and disallowed actions.
It should never ask the same model that proposed an action to make the authoritative
permission decision.

## Events and checkpoints

Events are append-only observations such as run started, model completed, policy decided
and tool completed. A trace groups events belonging to one run. A checkpoint stores
continuation state so a paused run can resume.

A checkpoint is not an audit log, and an event log is not enough to resume execution.
Durable approval needs the exact pending action and a stable run identifier. Sensitive
arguments should be redacted or omitted from telemetry where possible.

## Retries, timeouts and retry budgets

Network calls fail. A runtime should apply a timeout and may retry transient failures such
as temporary rate limits. Retries must be bounded and recorded. Exponential backoff with
jitter helps avoid many clients retrying simultaneously.

Do not retry every failure. Invalid arguments, policy denial and most authentication
errors will not improve on repetition. Consequential tools require an idempotency strategy
before automatic retry. The runtime should have both a step budget and a retry budget so
one failing provider does not consume unlimited time or credit.

## Cost attribution

Record model, prompt/configuration version, input tokens, output tokens, reasoning tokens,
estimated cost and run ID. This makes it possible to compare agents and enforce classroom
budgets. Cost belongs to the complete run, including retries and specialist calls, not
only the final response.

The included API credit is a controlled learning resource. Mock mode should be used while
debugging application logic; live calls should be used when model behavior is the subject
of the exercise.

## MCP: protocol, not permission

Model Context Protocol lets a client initialise a session, discover server capabilities
and invoke them through a common contract. A server may expose tools, resources or prompts.
The protocol improves interoperability; it does not establish trust.

An MCP tool description and its results are untrusted external content. Before importing
a discovered tool, the harness should consider server origin, schema, local risk,
permitted agents, arguments, timeout, output handling and logging. A server changing its
advertised tools must not silently expand application authority.

The Day 5 rule is therefore:

```text
discovery is not authorization
```

The client discovers the tool, the harness classifies it, local policy authorises or
pauses it, and only then does the protocol call occur.

## Mapping the course to production systems

| Course term | Common production terminology |
|---|---|
| Provider adapter | model client/provider layer |
| Agent configuration | agent definition/profile |
| Harness runtime | agent runtime/orchestration layer |
| Tool registry | tool/plugin registry |
| Policy | authorization or guardrail middleware |
| Events | tracing/telemetry |
| Checkpoint store | durable execution/state persistence |
| MCP client | protocol integration layer |

Production SDKs package different subsets of these responsibilities. Students should be
able to open an unfamiliar SDK and locate where its model calls, tools, policy, state and
events live rather than assuming the SDK itself is the architecture.

## What the mini harness does not provide

The classroom harness is intentionally not a production platform. It does not provide
enterprise identity, operating-system sandboxing, remote MCP authentication, distributed
workers, deployment or guaranteed model quality. Its purpose is to make the essential
boundaries visible so students can recognise and evaluate larger systems later.

## Automation is a trigger, not intelligence

A scheduler can start a run every day, but scheduling alone is ordinary automation. The
agentic decision is whether new evidence warrants a change and which permitted action to
propose. Policy then decides whether the exact proposal may proceed.

The Website Maintenance Agent demonstrates a production-shaped cycle at classroom scale:
fetch a real or cached public update, compare it with durable processed-item state, create
a structured website proposal, apply guardrails, pause for approval, write a real local
file, verify the result and record events. The scheduler should call one bounded `check`
operation; it should not contain hidden business logic.

An optional LLM judge may score whether the proposed update is faithful to its source.
That judge belongs after deterministic checks and before approval or publication. It is
advisory because it can be inconsistent, biased toward fluent text or influenced by the
content it evaluates. File-path, schema, source, build and permission checks remain
authoritative application code.
