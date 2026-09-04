# Day 4 Theory - Measured Multi-Agent Systems

> Instructor authoring source. Students receive this material embedded in the relevant notebooks and are not expected to read this file.

## Why multiple agents are not the starting point

Adding agents adds model calls, duplicated context, coordination logic, latency, cost and
new failure modes. It is justified only when a task splits into bounded perspectives whose
combined quality beats a simpler system by enough to pay for that complexity.

So today we do not argue about it. We build one general reviewer, one reviewer plus
deterministic tools, and a three-specialist team with a supervisor, run all three over the
same artifact with a hidden answer key, and read the numbers.

We run that comparison twice, against two different reviewers: one with real blind spots,
and one that is already strong. The winner is not the same both times. **The single
reviewer is allowed to win, and in one of the two runs it does.**

## Deterministic tools before more model calls

Some findings need no model judgement at all. A Python parser can prove that a file calls
`eval`, that a function has a mutable default argument, and that an `except Exception:`
handler exists. Linters, tests, type checkers and security scanners give objective
evidence for the patterns they support, for free, in milliseconds, with the same answer
every time.

Model reviewers earn their cost on ambiguous intent, cross-cutting reasoning,
prioritisation and explanation. A strong system pairs deterministic evidence with bounded
judgement instead of paying three models to rediscover facts a parser already proved.

One consequence matters for measurement: a static checker has never heard of your answer
key, so it invents its own finding ids. Your evaluator therefore has to match a finding to
a defect by *location*, exactly as it must for a real model.

## Specialist decomposition

A specialist role must narrow the task, not merely rename the same prompt. Our
correctness, security and maintainability reviewers all read the same immutable artifact
but answer different questions, and all return the same `Finding` contract: category,
location, evidence, severity, recommendation, and which role produced it.

That contract is the **handoff**. It is what crosses the boundary between agents - not
personas, not hidden reasoning, not a full chat transcript. The supervisor does not need
each reviewer's conversation; it needs validated records with enough provenance to resolve
duplicates and conflicts.

Narrowing a prompt does not create knowledge the reviewer never had. If the generalist
cannot see a subtle business rule, the specialist with a narrower prompt usually cannot
see it either. Decomposition redistributes attention; it does not add capability.

## Sequential before parallel

Say the words precisely:

- **Fan-out**: one step launches several independent branches.
- **Shared state**: what all the branches read. Here it is the immutable artifact text.
  Nothing mutates it, which is exactly why the branches are safe to run at the same time.
- **Fan-in**: one step collects every branch's results and combines them.

Run the branches sequentially first, because the order and any failure are easy to read.
Then, if the branches truly do not depend on one another, run them in threads. Wall-clock
time drops because the calls wait on the network together. The number of calls, the tokens
and the bill do not drop at all - and parallel calls hit provider rate limits sooner.

The fan-in step must be bounded: validate fields, merge duplicates, rank, cap the output,
stop. A supervisor that can keep asking for revisions has become another autonomous loop
rather than a controlled aggregation step - and it must report what it merged and what it
truncated, or the cap silently deletes findings.

## Deduplication is harder than matching IDs

If every reviewer reuses the same seeded id, deduplication is a dictionary lookup. Real
reviewers do not. A static checker calls it `AST-EVAL-20`; a model calls it
`MODEL-SEC-20-3`; a human calls it "unsafe eval". Same defect, three ids, three survivors
in your final report.

So the supervisor merges on a rule that does not depend on shared ids: same category, and
lines close enough to be the same place. That rule is *live*, and it can be wrong. Two
genuinely different security defects on adjacent lines will be **falsely merged** and the
second one is lost. Loosen the rule and you hide real defects; tighten it and duplicates
survive. There is no setting that is right for every artifact, which is why production
systems keep a human in the merge loop.

Evaluation needs the same discipline. Credit each known defect **once**: three reviewers
reporting the same problem is one defect found plus two duplicates, never three finds.

## Evaluating nondeterministic systems

Do not assert exact model wording. Assert invariants and measure outcomes:

- Is every finding structurally valid?
- Does the evidence quote the supplied artifact?
- How many known defects were found, counted once each?
- How many unsupported findings (false positives) were reported?
- How many duplicates survived synthesis, and how many did the supervisor merge?
- How many calls and tokens were used, according to the provider?
- Did the system terminate within its bounds, and what did it truncate?

Telemetry must be measured, never invented. A step that makes no model call reports zero
tokens and says "no model call"; it does not borrow a plausible-looking estimate. A tidy
number in a results table that nothing actually produced is worse than no number.

One run is an anecdote. Repeat model experiments with the same model, prompt version,
temperature and artifact, and report the variance rather than the best result.

## Capability can change the architecture conclusion

A weaker instruction-following model can benefit a lot from narrow prompts. A stronger
model may handle the general review well enough that the specialist calls add nothing.
So "multi-agent is better" usually means "decomposition compensated for *this* reviewer on
*this* task with *this* prompt."

Our two scenarios make that explicit and measurable rather than rhetorical. In the
`blind_spots` scenario the team finds 9/9 where one reviewer finds 5/9, and the extra
calls are clearly worth it. In the `strong_generalist` scenario the team finds exactly
what one reviewer already found, for three times the calls and tokens, plus duplicates to
merge and three times the surface area to debug. Same code, same artifact, opposite
verdict.

Multi-agent is not worth it when: one reviewer already reaches the quality bar; the extra
recall costs more than the defects it catches; the sub-tasks are not genuinely
independent; or the failure you keep hitting is a capability gap that a narrower prompt
cannot fill.

## Cost and latency arithmetic

Approximate run cost as:

```text
sum of input tokens across calls
+ sum of output and reasoning tokens
+ retries
```

Send the same 1,000-token artifact to three specialists and you pay for that input three
times, unless caching or a provider feature changes the arithmetic. Parallel execution can
cut elapsed time while leaving total cost identical or higher.

A fair comparison records recall, false positives, duplicates, calls, tokens, latency,
estimated cost and debugging burden. Then choose the **smallest** system that meets the
quality requirement.

## What to carry into Day 5

Days 1-4 repeatedly configure providers, validate tool and model output, enforce limits,
fall back safely and record events. Day 5 pulls those repeated responsibilities into
reusable infrastructure while keeping application-specific instructions, tools and policy
in agent configuration.
