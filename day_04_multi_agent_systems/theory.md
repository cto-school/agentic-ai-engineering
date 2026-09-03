# Day 4 Theory - Measured Multi-Agent Systems

> Instructor authoring source. Students receive this material embedded in the relevant notebooks and are not expected to read this file.

## Why multiple agents are not the starting point

Adding agents adds model calls, duplicated context, coordination logic, latency, cost and
new failure modes. It is justified only when a task decomposes into bounded perspectives
whose combined quality exceeds a simpler system by enough to pay for that complexity.

The engineering review project therefore begins with one general reviewer and an
objective artifact containing seeded defects. The single reviewer is allowed to win.

## Deterministic tools before more model calls

Some findings do not require model judgment. An AST can identify `eval`, mutable default
arguments and broad exceptions reproducibly. Linters, tests, type checkers and security
scanners provide objective evidence for the patterns they support.

Model reviewers are more useful for ambiguous intent, cross-cutting reasoning,
prioritisation and explanation. A strong system combines deterministic evidence with
bounded judgment rather than asking several models to rediscover facts a parser can prove.

## Specialist decomposition

A specialist role should narrow the task, not merely rename the same prompt. Correctness,
security and maintainability reviewers receive the same immutable artifact but different
evaluation criteria. They return the same `Finding` contract: category, location,
evidence, severity and recommended correction.

Structured handoffs prevent unconstrained agent conversations. The supervisor does not
need every reviewer's full chat history. It needs validated findings and enough provenance
to resolve duplicates and conflicts.

## Sequential before parallel

Run specialists sequentially first because the execution order and failures are easy to
inspect. If the branches are independent, they can then fan out in parallel and fan in at
the supervisor. Parallelism may reduce wall-clock time but does not reduce total model
calls or tokens. It may also trigger provider rate limits.

The fan-in step must be bounded. It validates fields, deduplicates, ranks, caps output and
terminates. A supervisor that can indefinitely request revisions has created another
autonomous loop rather than a controlled aggregation step.

## Deduplication is harder than matching IDs

Stable seeded IDs make the classroom evaluator simple. Real reviewers may describe the
same issue with different titles or identify one root cause at different lines. Similarity
can help group candidates, but a human may still need to resolve ambiguous merges. The
course's deterministic deduplication demonstrates orchestration and should not be mistaken
for a complete production finding-resolution system.

## Evaluating nondeterministic systems

Do not assert exact model wording. Test invariants and outcomes:

- Is every finding structurally valid?
- Does evidence refer to the supplied artifact?
- How many known defects were found?
- How many unsupported findings were reported?
- How many duplicates survived synthesis?
- How many calls and tokens were used?
- Did the system terminate within its bounds?

One run is an anecdote. Repeat model experiments with the same model, prompt version,
temperature and artifact. Report variance rather than selecting the best result.

## Capability can change the architecture conclusion

A weaker instruction-following model may benefit disproportionately from narrow prompts.
A stronger model may handle the general review well enough that specialist calls add
little value. Therefore "multi-agent is better" may actually mean "decomposition
compensated for this model under this task and prompt."

An instructor may repeat the same golden-set experiment on a currently strong reference
model. The lesson is not brand ranking. It is that model capability, cost and reliability
are architecture inputs.

## Cost and latency arithmetic

Approximate run cost as:

```text
sum of input tokens across calls
+ sum of output and reasoning tokens
+ retries
```

If the same 1,000-token artifact is sent to three specialists, the input is paid three
times unless caching or a provider feature changes the calculation. Parallel execution
may reduce elapsed time while preserving or increasing total cost.

A fair comparison records recall, false positives, calls, tokens, latency, estimated cost
and debugging complexity. The chosen system should be the smallest one that meets the
quality requirement.

## What to carry into Day 5

Days 1-4 repeatedly configure providers, validate tools, enforce limits and record events.
Day 5 extracts these repeated responsibilities into reusable infrastructure while keeping
application-specific instructions, tools and policy in agent configurations.
