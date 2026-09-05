# Limits, evaluation, and what it means for building agents

Every limit of a language model traces back to a mechanism from the earlier chapters. Knowing the
mechanism tells you which fixes can work and which are wishful thinking. This chapter is the map.

## Six limits and their causes

| Limit | Mechanism behind it | What actually helps |
|---|---|---|
| **Hallucination** (confident wrong facts) | next-token prediction rewards fluency, not truth (F3); knowledge is a pattern in MLP weights, not a database (F2) | give the facts in the prompt (retrieval, Day 2), require citations, allow "I don't know", verify with tools |
| **Knowledge cutoff** | the training data has a date (F4) | retrieval and tools for anything current; never ask the model what day it is |
| **Context limits and "lost in the middle"** | attention cost grows with the square of length (F2); models attend unevenly to long inputs | compaction and summaries (Day 3), put the important material first or last, retrieve instead of stuffing |
| **Arithmetic and long strings** | tokens split numbers and words unpredictably (F1) | a calculator tool (Day 1, n8n module); code execution |
| **Prompt injection** | system prompt, user text and tool results are one token sequence (F1, F5); instructions in fetched content look like instructions | treat everything the model reads as untrusted, keep side effects behind code and human approval (Day 3), least-privilege tools (OpenClaw module) |
| **Sycophancy and inconsistency** | preference training rewards agreeable answers (F5); sampling varies (F3) | independent checks, structured output with validation, temperature 0 where repeatability matters, evaluation over many runs (Day 4) |

The pattern: no limit here is fixable by a better prompt alone, because each is a property of the
mechanism. Prompts change the distribution; they do not change what the model is.

## How models are measured

**Benchmarks** are fixed test sets with automatic scoring: general knowledge questions, maths
competitions, coding tasks with unit tests, instruction-following checks, long-context retrieval
tests, agentic tasks such as completing a software issue. They are useful for ranking and famously
gameable: training data leaks, and models are tuned toward them.

Three practical rules for your own work, which Day 4 puts into code:

1. **Build a small evaluation set for your task** (twenty to a hundred cases with expected
   outcomes) before choosing a model or changing a prompt. Benchmarks measure someone else's task.
2. **Score with code where you can** (exact match, schema validity, tests passing) and with a model
   as judge where you must, checking the judge against a sample of human ratings.
3. **Run each case several times.** Sampling means one run is one draw from a distribution.

## Prompting, retrieval, fine-tuning: which lever

| You want to change | Lever | Why it fits |
|---|---|---|
| tone, format, role, rules for this task | prompting (system message, examples) | cheap, immediate, adjusts the distribution at inference |
| what the model knows for this request | retrieval (RAG) | puts facts in the context, the one place the model reliably reads from |
| behaviour on a narrow task at scale, or a style for thousands of calls | fine-tuning (SFT/DPO on your data) | moves the weights; poor at adding facts, good at habits and formats |
| reliability of an action | tools, validation, and code around the model | takes the decision away from sampling entirely |

Most agent problems in this course are solved by the last row.

## The mental model in ten lines

1. Text becomes tokens; tokens become vectors.
2. A stack of attention and MLP blocks refines each token's vector using everything before it.
3. The last vector becomes a probability for every possible next token.
4. One token is picked (greedy or sampled with temperature), appended, and the loop repeats.
5. Pretraining set the weights by predicting the next token over trillions of tokens; that is where knowledge and its cutoff come from.
6. Post-training taught the chat format, preferences, refusals and reasoning; it made habits, not rules.
7. Inference is a cheap parallel prefill and an expensive serial decode, with a KV cache in between.
8. Tool calls and JSON are text formats the model emits and the host parses or constrains.
9. Everything the model reads is one sequence, so anything it reads can try to instruct it.
10. Reliability comes from what you build around the model: retrieval, validation, permissions, evaluation.

Line 10 is the course.

## Recap

- Each limit (hallucination, cutoff, context, arithmetic, injection, sycophancy) is a property of a mechanism, so the fix is around the model, not in a cleverer prompt.
- Measure on your own task, with code where possible, over several runs.
- Prompting adjusts, retrieval informs, fine-tuning habituates, and code around the model makes actions reliable.
