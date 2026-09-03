# Course Model and Routing Policy

## Primary classroom candidate

`openai/gpt-oss-120b` through OpenRouter is the initial standard model.

It is selected for classroom validation because it supports agent-oriented work such as function calling and structured output, while hosted inference removes dependence on student RAM and GPU capability.

`openai/gpt-oss-20b` is retained for model-size and cost comparisons, not assumed to be the default for advanced labs.

Model availability, pricing, provider behaviour, and supported parameters must be verified immediately before each delivery.

Official references:

- [OpenRouter GPT-OSS 120B](https://openrouter.ai/openai/gpt-oss-120b)
- [OpenRouter GPT-OSS 20B](https://openrouter.ai/openai/gpt-oss-20b)
- [OpenRouter tool calling](https://openrouter.ai/docs/guides/features/tool-calling)
- [OpenRouter structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs)

## Request controls

Course code should centralize:

```text
model: openai/gpt-oss-120b
reasoning effort: low
maximum output: 800 tokens by default
maximum agent steps: 5
maximum multi-agent revisions: 2
provider parameter support: required
provider price ceiling: verified before delivery
```

Reasoning tokens count toward output usage, so high/default reasoning must not be enabled accidentally in repetitive labs. For multi-turn tool use, preserve provider-returned reasoning details when the selected reasoning model requires them; they need not be displayed to students.

## Student budget

Each student key is configured with:

- USD 1 lifetime maximum
- No automatic reset
- Course-end expiry
- Individually identifiable label
- Model/provider guardrail where available

Expected course consumption should be measured using an instructor key after all five projects exist. The USD 1 value is a safety ceiling, not a target.

## Required benchmark

Evaluate the exact classroom configuration on:

1. Direct response without tools
2. Structured response validation
3. Correct calculator selection
4. Correct knowledge-search selection
5. Two sequential tool calls
6. Invalid tool arguments and recovery
7. Unknown question and cautious response
8. Termination within the application limit
9. Day 2 RAG citation behaviour
10. Day 3 approval classification
11. Day 4 parallel-review structured findings

Record correctness, schema validity, calls, input/output/reasoning tokens, elapsed time, provider, and cost.

## Provider routing

Prefer providers that support all requested parameters. Apply an instructor-approved maximum input/output price and deliberately choose whether routing optimizes price, throughput, or tool-call reliability.

Do not embed a provider-specific price ceiling permanently without reviewing current pricing.

## Optional Ollama route

Ollama is used in a provider-portability lab for students with suitable hardware. The exact local comparison model is selected after the same Day 1 behaviour benchmark.

This lab should demonstrate:

- Same application architecture with another provider
- Local privacy/offline advantages
- Hardware and latency constraints
- Model capability as an engineering constraint

## Optional direct OpenAI route

Students with their own OpenAI API access see one complete official-SDK example in the first notebook. It is not repeated throughout the course.

## Mock route

The deterministic mock provider remains mandatory for testing control flow without network calls, latency, or API cost. It does not stand in for a real model-quality test.
