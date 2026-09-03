# Conceptual Answer Key

These are compact instructor answers for discussion and notebook recap questions. Accept different wording when the reasoning is sound.

## Day 1

**When is a deterministic workflow preferable to an agent?** When the valid steps are known, the path should be predictable, and model-based routing adds no useful flexibility.

**Why validate tool arguments?** Model output is untrusted input. Validation prevents malformed or unauthorized arguments from reaching real code.

**Why bound the loop?** Tool errors, ambiguous results, or repeated model requests can otherwise create unbounded calls and cost.

**What makes a system agentic?** The model selects among permitted actions based on current state, observes results, and continues toward a goal inside explicit limits.

## Day 2

**Why separate retrieval and answer evaluation?** A wrong answer can arise because evidence was not found or because the model mishandled good evidence. The remedies differ.

**Is retrieved text trusted?** No. It is external data and may contain irrelevant content or instructions. Treat it as evidence, not authority over system policy.

**Why keep a keyword baseline?** It is fast, inspectable, and often strong for exact identifiers. It also makes the value and failure modes of semantic retrieval visible.

**What is context engineering here?** Selecting, ordering, labeling, and limiting the evidence and state supplied to the model—not merely writing a prompt.

## Day 3

**How do context, state, and memory differ?** Context is what the model sees now; state is application data used during execution; memory is information deliberately retained across turns or runs.

**Why is storing everything unsafe?** It increases privacy exposure, stale-data risk, retrieval noise, and prompt-injection persistence.

**Why approve the action rather than the prose?** The consequential object is the structured action with exact arguments. Friendly prose can hide a dangerous operation.

**Why does idempotency matter?** Retries and resumes must not repeat a side effect such as sending or charging twice.

## Day 4

**Why not begin with multiple agents?** They add calls, latency, coordination failures, and evaluation complexity. Use them only when specialization or decomposition produces measured benefit.

**What should remain deterministic?** Routing constraints, permissions, merging rules, deduplication, budgets, and failure handling wherever possible.

**How should systems be compared?** On the same cases, compare task quality together with latency, model calls, token usage or cost, and failure behaviour.

**Does giving an agent more tools only affect capability?** No. It expands its action space, permissions, error surface, and testing burden, so capability changes architecture.

## Day 5

**What is an AI harness?** In this course, it is the reusable runtime around model calls and tools: configuration, registry, policy, events, checkpoints, limits, and integrations.

**Why keep provider configuration outside agent logic?** It makes model routes replaceable, testable, and centrally constrained without rewriting domain behaviour.

**What is the difference between a retry and a resume?** A retry repeats a failed operation under a policy; a resume reconstructs a larger run from a durable checkpoint. Both require idempotency analysis.

**Why is an MCP server not automatically trusted?** Protocol compatibility says how systems communicate, not whether a server, tool description, returned content, or requested action is safe.

## Cross-course architecture

The final chain is:

```text
Model → Tool → Agent → Knowledge → Memory → Safety
      → Observability → Multi-Agent → Harness
```

This is a learning sequence, not a claim that every application needs every layer. A good design uses the smallest set of layers that satisfies the task and its risk constraints.

