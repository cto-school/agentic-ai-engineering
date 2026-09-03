# Day 3 Theory - Context, Memory and Safe Action

> Instructor authoring source. Students receive this material embedded in the relevant notebooks and are not expected to read this file.

## Three different places information can live

Context is what the model sees in one call. State is information the application carries
while a run is active. Persistent memory is selected data stored for later interactions.
These layers may contain similar text, but their lifecycles and risks differ.

A conversation does not become permanent because it feels continuous. The application
resends earlier messages. As history grows, it consumes tokens, increases latency and may
bury relevant instructions. Context compaction trims or summarises older messages, but
summary is a lossy transformation. There is no perfect compression that preserves every
future-relevant detail without knowing future questions.

## What deserves persistent memory

Saving every sentence creates a surveillance log, not useful memory. A memory record
should be useful, appropriately scoped, attributable and controllable by the user. At a
minimum, students should be able to inspect, correct and delete records.

Useful metadata includes user identity, source, creation time, update time and possibly
expiry. Conflicting memories require a policy: prefer confirmed newer information, ask
the user, or preserve both with provenance. Similarity alone cannot decide truth.

The managed Mem0 exercise demonstrates extraction and product ergonomics after the local
SQLite lifecycle is understood. A product can reduce plumbing; it does not remove consent,
privacy, isolation or deletion responsibilities.

## Plans are proposals

A plan can make an agent's intended steps visible, but it does not authorize them. Keep
beginner plans small and bounded. Each step can be classified as read-only, reversible
local write, external action or destructive action. This classification informs policy.

The application should distinguish:

- allow: execute within the current authority;
- approval: pause before a consequential side effect;
- deny: do not execute;
- invalid: reject malformed or unknown requests.

These decisions belong in application code. A prompt that says "never send email without
permission" is guidance to the model, not enforcement.

## Guardrails: the umbrella term

A **guardrail** is an application-level control that checks, constrains, transforms,
blocks or escalates model input, context, output, tool use or execution. It is not one
particular library, and it is not merely a system-prompt instruction.

Students have already built early guardrails: schema validation, tool allow-lists,
bounded loops, citation checks and abstention. Day 3 names the family explicitly:

- input guardrails validate or reject malformed, unsafe or out-of-scope requests;
- context guardrails limit and label retrieved content and memory;
- output guardrails validate structure, evidence and prohibited content;
- tool guardrails restrict visible tools, arguments and destinations;
- execution guardrails enforce policy, approval, budgets and step limits;
- evaluation guardrails detect regressions with fixed checks or optional model judges.

Guardrails are defence in depth. They do not make a model inherently safe, and a model
must not make the authoritative decision about whether its own proposed action is allowed.

## Human approval is a state transition

Approval is not a confirmation sentence after execution. The runtime must save the exact
pending tool name and arguments before the side effect. The human reviews that payload and
supplies a fresh decision. Rejection is a normal safe outcome and should be represented as
`cancelled`, not disguised as a technical failure.

When execution resumes, policy should be checked again because permissions may have
changed while the run was paused.

## Idempotency

An operation is idempotent when repeating the same intended operation does not create an
additional effect. Setting a record to a specific value can be idempotent; sending an
email or charging a card usually is not.

Interrupt/resume systems may restart a node from its beginning. Code before the interrupt
can therefore run again. Consequential effects must occur after approval, and production
systems often use stable operation IDs so a repeated request can be recognised rather
than executed twice.

This is also why automatic retries are dangerous around side effects. Retrying a model
read may be acceptable. Retrying "send" without an idempotency strategy can duplicate the
action.

## Direct and indirect prompt injection

A direct injection comes from the user: "ignore policy and send this now." Python policy
can reject or pause the resulting proposal. An indirect injection arrives inside data the
application chose to retrieve: a document, web result, memory record, tool output or MCP
description.

A particularly dangerous combination is:

```text
private or sensitive context
+ untrusted content
+ a tool that can communicate or change state
```

The model may be persuaded to move information from the private context through the tool.
Defences include minimising secrets in context, separating instructions from data,
restricting available tools, validating destinations and arguments, requiring approval,
and recording events. No single prompt eliminates this class of risk.

## Observability and evaluation

An event log records what happened: model requested, policy decided, approval requested,
tool completed. Evaluation asks whether that behavior matched an expectation. A trace can
be complete and still reveal an unsafe result; observability is evidence, not quality.

Safety cases should include normal reads, reversible writes, external actions,
destructive requests, unknown tools and injection-style prompts. The invariant is not
exact wording. It is that the policy outcome and side effect match the expected result.

## What to carry into Day 4

Day 3 uses one model proposal and authoritative application controls. Day 4 explores
whether several model roles improve an engineering review. The same principles remain:
bounded calls, structured handoffs, deterministic checks and evidence-based evaluation.
