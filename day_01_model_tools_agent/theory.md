# Day 1 Theory - From Model Calls to Bounded Agents

> Instructor authoring source. Students receive this material embedded in the relevant notebooks and are not expected to read this file.

## Why this day exists

A language model is a generator, not an application. It receives a finite context and
predicts a continuation. It does not automatically know your files, execute Python, or
continue working until a goal is complete. An agentic application is created when host
code gives the model a limited set of possible actions, carries state between turns,
executes approved actions, and decides when the run must stop.

Day 1 removes the apparent magic from this process. By the end, students should be able
to point to the exact line that sends a request, the exact data that describes a tool,
the exact function that executes it, and the exact condition that terminates the loop.

## What a model call actually contains

A typical request contains a model identifier, ordered messages, optional tool schemas,
and generation controls. Messages are not merely a chat transcript. Their roles tell the
provider how each piece should be interpreted:

- `system`: standing instructions and boundaries;
- `user`: the current task or supplied information;
- `assistant`: previous model output, including tool requests;
- `tool`: an observation produced by host-executed code.

The provider serializes this request into a form the model can process. The model sees
tokens representing instructions, messages and tool descriptions. It does not receive a
live Python function. When it appears to "call" a tool, it is generating structured
tokens that name a function and propose arguments. The host application parses those
tokens, validates the arguments, applies policy, calls ordinary code, and returns the
result in another message.

This distinction is load-bearing:

```text
model proposes structured tokens
-> application validates and authorizes
-> Python executes
-> application records the observation
-> model sees the observation on the next call
```

If the model invents a tool name, supplies the wrong type, or requests a prohibited
action, nothing should happen unless the application accepts the request.

## Why structured output matters

Free-form text is useful for people but unreliable for software. A program cannot safely
assume every response contains the same headings, fields or value types. A schema turns
this ambiguity into a contract. Validation does not make the model correct; it makes a
particular class of failure visible.

Consider a confidence field. The sentence "confidence is high" may be understandable to
a person but difficult to compare. A schema can require a number between 0 and 1. If the
model returns `4.5`, validation rejects it instead of quietly sending bad data deeper into
the application.

The correct mental model is:

- schema validity asks whether the response has an acceptable shape;
- factual evaluation asks whether its claims are correct;
- policy asks whether a requested action is permitted.

These are different checks and should not be collapsed into one model prompt.

## Why the application owns termination

After one tool result, the model may ask for another tool or return a final answer. That
creates a loop whose length is not known in advance. It is tempting to write "stop when
finished" in the system message and trust the model. That is not an execution limit. A
confused model can repeat the same request, alternate between tools, or continue refining
an already adequate answer. Each turn consumes time, tokens and money.

Host code therefore enforces a maximum number of steps. Reaching the limit is not the
same as crashing. A good runtime returns a visible status such as `max_steps` together
with the partial trace. Reporting incomplete work honestly is safer than pretending the
run completed.

## Error compounding

Multi-step systems amplify small error rates. Suppose, only for illustration, that each
model decision has a 95% chance of being acceptable and that errors are independent. The
chance that ten decisions are all acceptable is:

```text
0.95 ^ 10 = approximately 0.60
```

The independence assumption is simplistic, but the lesson is useful: a system with many
model decisions can be much less reliable than any single impressive response suggests.
This motivates bounded loops, deterministic validation, fewer calls, clear tools and
evaluation of complete trajectories rather than isolated answers.

## Workflow or agent?

Not every problem needs an agent. Use ordinary code or a deterministic workflow when the
steps and decision rules are known. Use a hybrid workflow when most steps are fixed but
one bounded judgment benefits from a model. Consider an agent when the next action cannot
be fully predetermined, the action set is small, failures are containable, and success
can be evaluated.

Ask:

1. Are the steps known in advance?
2. Can normal code make the decision reliably?
3. Does the model genuinely add judgment rather than decoration?
4. What is the consequence of a wrong action?
5. Is there a strict step and tool boundary?
6. Can we observe and evaluate the result?

If these questions have weak answers, the correct design is often a workflow, not an
agent.

## What to carry into Day 2

Day 1 creates a bounded model-and-tool system, but the model still relies on information
inside its request or learned during training. Day 2 introduces external knowledge. The
agent loop remains the same; the new question is how to retrieve the right evidence and
prove the answer used it.
