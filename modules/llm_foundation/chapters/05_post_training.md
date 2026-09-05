# Post-training: from text completer to assistant

The base model from chapter F4 can write anything and wants nothing. **Post-training** is the set
of much smaller training stages that teach it the shape of a conversation, the habit of being
helpful, the boundaries it should keep, and, most recently, how to think before answering (diagram
D62, later stages). Every model you call in this course has been through some version of it.

## Stage 1: supervised fine-tuning (SFT)

Take tens of thousands to a few million example conversations: a user turn and the ideal assistant
reply, written by people or generated and filtered. Format each with the **chat template**, the
fixed layout of special tokens that marks who is speaking:

```text
<|start|>system<|sep|>You are a helpful assistant.<|end|>
<|start|>user<|sep|>What is a tool call?<|end|>
<|start|>assistant<|sep|>A tool call is ...<|end|>
```

(The exact tokens differ per model family; `ollama show gemma3:4b --modelfile` prints Gemma's.)

Then continue training with the same next-token objective as pretraining, but only on the
assistant's tokens. After SFT the model has learned the template: when it sees the start of an
assistant turn, it produces an answer, and when the answer is done it emits the end token. That end
token is what stops the loop in chapter F3. The system message is nothing more than the first
segment of this template, which is why it steers but cannot guarantee anything: it is text the
model was trained to weight heavily, not a rule.

SFT also teaches formats: markdown, JSON on request, code blocks, and the tool-call syntax that
chapter F6 explains.

## Stage 2: learning from preferences (RLHF and relatives)

SFT copies examples. It cannot easily teach "be less verbose", "do not make up citations", "decline
this class of request politely", because those are judgments about *which of two answers is
better*, not a single right answer.

The classic method, **RLHF** (reinforcement learning from human feedback):

1. Sample two or more replies from the model for the same prompt.
2. Have people (or a strong model with a rubric) say which is better.
3. Train a **reward model** to predict that preference.
4. Adjust the language model with reinforcement learning (PPO) to produce replies the reward model
   scores highly, with a penalty for drifting too far from the SFT model.

A simpler method that skips the reward model, **DPO** (direct preference optimisation), trains
directly on the pairs and is now common in open models. The outcome is the same: helpfulness,
honesty about uncertainty, tone, safety behaviour and refusals are shaped here. It is also where
**sycophancy** comes from: people prefer agreeable answers, so the reward model learns to reward
them.

## Stage 3: reasoning with verifiable rewards

Since 2024 a third stage has become standard for the strongest models. For tasks with a checkable
answer (maths, code that must pass tests, logic puzzles, tool use with a known correct call), the
model is allowed to write a long **chain of thought** before its answer, and reinforcement learning
rewards it when the final answer is right. No human labels are needed; the checker is the reward.
Models trained this way learn to plan, to verify their own steps, and to backtrack, which is the
behaviour that "reasoning" or "thinking" models expose as a hidden or visible thinking section.
The reasoning effort settings some APIs offer control how many thinking tokens the model spends.

This stage is why tool calling has become reliable: models are trained, with rewards, on producing
well-formed calls and using results correctly. It is also expensive at inference time, since the
thinking tokens are output tokens.

## The result, and what it did not change

After post-training you have a chat model. It still predicts the next token, one at a time, from
the same Transformer with slightly adjusted weights. Post-training touches perhaps a thousandth of
the compute of pretraining and adds little knowledge; it changes *behaviour*, which tokens the model
prefers to produce in which situations.

Some consequences worth keeping:

- **A system prompt is trained influence, not enforcement.** Guardrails that must hold belong in
  code (Day 3).
- **Refusals and politeness are learned habits** that a cleverly worded prompt can sometimes
  route around; that is the whole field of jailbreaking.
- **Different providers post-train differently**, which is why models with similar benchmark scores
  feel different to work with, and why Day 4's comparative evaluation exists.
- **Fine-tuning your own model** is SFT or DPO on your data. It changes style and format cheaply;
  it is a poor way to add facts, which is what retrieval (Day 2) is for.

## Recap

- SFT teaches the chat template and the habit of answering; the end-of-turn token it learns is what stops generation.
- RLHF or DPO shapes preferences (helpfulness, honesty, refusals, and unfortunately sycophancy) from comparisons rather than examples.
- Reinforcement learning with verifiable rewards trains reasoning and reliable tool use; none of this adds knowledge or makes prompts into rules.
