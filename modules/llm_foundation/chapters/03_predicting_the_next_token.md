# Predicting the next token

The model's output is a list of logits, one per vocabulary entry. This chapter is about the last
few millimetres: turning that list into one token, then doing it again, and what the settings you
have been passing to every API call actually change (diagram D64).

## Logits to probabilities: softmax

The logits are unbounded numbers. **Softmax** exponentiates each and divides by the sum, so they
become positive and add up to one: a probability distribution over the next token. A logit two units
higher than another means about seven times the probability.

## Choosing: greedy or sampling

Two ways to pick one token from the distribution:

- **Greedy**: take the most probable. Deterministic; the same prompt always gives the same reply.
  It tends to produce flat, repetitive text, because the most probable next word is usually the
  safest one.
- **Sampling**: draw one token at random with the given probabilities. A token with probability
  0.05 is chosen one time in twenty. Replies vary between runs, and often read better.

**Temperature** reshapes the distribution before sampling by dividing every logit by *T*:

- *T* below 1 sharpens: the most likely token gets even more of the mass. At *T* = 0 it is greedy.
- *T* = 1 is the distribution the model learned.
- *T* above 1 flattens: unlikely tokens get a real chance, and past about 1.5 the text drifts into
  nonsense.

**Top-p** (nucleus sampling) keeps only the most likely tokens whose probabilities add up to *p*
(0.9, say) and samples among those, cutting off the long tail of barely-plausible tokens. **Top-k**
keeps the *k* most likely instead. Providers expose one or more of these; Ollama's Modelfile
`PARAMETER` lines set them locally.

The simulation below is a tiny language model trained on a few paragraphs about the course: it
counts which word followed which two words, which is a **trigram** model. It is nothing like a
Transformer inside, but its output is the same kind of thing, a probability distribution over the
next token, so temperature and sampling behave identically. Give it a start, look at the
distribution, then let it write.

<!-- widget:next-token -->

Things to try:

- Set the temperature to 0 and generate twice: identical text. Set it to 1 and generate twice.
- Set it to 2 and watch rare continuations win; the text stops making sense within a sentence.
- Type a start that the training text never contained. The model has no counts, falls back to
  shorter contexts, and finally to guessing by frequency alone. This is a toy version of what a real
  model does when your question is outside what it saw: it still produces fluent text.

## Autoregression: one token at a time

A reply is produced by a loop: run the model on the prompt, pick a token, append it to the
sequence, run again. A 300-word answer is about 400 passes through the whole network. Each pass
sees everything before it, including the tokens the model itself just chose, which is why an early
wrong word tends to be defended rather than corrected: the model is predicting what plausibly follows
its own text.

The loop stops when the model emits an **end-of-turn** token, or when the caller's maximum output
length is reached (`max_tokens`; a reply that ends mid-sentence usually hit this limit).

## Why fluent and wrong go together

Nothing in this chapter checked a fact. The model produces the distribution that its training data
makes most likely, and sampling picks from it. If the training text contained many confident
sentences of the form "X was founded in YEAR", the model will produce a confident sentence of that
form for an X it knows nothing about, with a plausible year. That is a **hallucination**: not a
malfunction, but the mechanism working on the wrong input. Chapter F7 is about what to do; Day 2's
retrieval with citations and abstention is the course's main answer.

## What the API parameters mean, now

| Parameter | Effect inside the model |
|---|---|
| `temperature` | divides logits before softmax; 0 is greedy |
| `top_p`, `top_k` | truncate the distribution before sampling |
| `max_tokens` | cap on the number of loop iterations |
| `stop` | strings that end the loop early |
| `seed` | fixes the random draws, so sampling repeats (when the provider supports it) |
| `logprobs` | return the probabilities of the chosen tokens, useful for confidence checks |

Day 1 section 1.2 sets temperature and watches the reply change; you now know what changed.

## Recap

- Softmax turns logits into probabilities; greedy takes the top one, sampling draws by probability.
- Temperature sharpens or flattens the distribution before the draw; top-p and top-k cut its tail.
- A reply is one token per pass, appended and fed back, until an end token or the length cap; fluency and truth are produced by different things.
