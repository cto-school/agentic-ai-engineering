# From text to tokens to vectors

A language model is a function. It takes a sequence of numbers in and produces a list of
probabilities out: one probability for every possible next piece of text. Everything else, the chat,
the tool calls, the reasoning, is built by calling that function many times. This chapter is about
the "numbers in" half (diagram D60).

## Tokens, not words, not letters

The model never sees letters. Before anything happens, a **tokenizer** cuts your text into
**tokens**, pieces from a fixed vocabulary, and replaces each with its id number.

```text
"Tokenization is not complicated."
→ ["Token", "ization", " is", " not", " complicated", "."]
→ [ 3404, 2065, 374, 539, 17395, 13 ]
```

Why pieces? Whole words would need a vocabulary of millions (every word in every language, every
misspelling, every name) and still meet words never seen. Single characters would make the
vocabulary tiny but every sentence very long, and the model would spend its capacity re-learning
spelling. Sub-word pieces are the compromise: common words are one token, rare words are a few
pieces, and anything at all can be spelled out from bytes if necessary.

Typical vocabularies have 32,000 to 260,000 tokens. In English, one token is about three quarters of
a word: 100 tokens is roughly 75 words. Code and non-Latin scripts cost more tokens per idea, which
is why the same request is more expensive in Hindi than in English.

## Byte-pair encoding, the algorithm most tokenizers use

**BPE** builds the vocabulary from data. Start with the 256 byte values as the only tokens. Then,
repeatedly:

1. Count how often every adjacent pair of tokens occurs across the training text.
2. Take the most frequent pair and **merge** it into a new token.
3. Add the merge to a list, and repeat.

After a few thousand merges, common syllables and words are single tokens. To tokenize new text,
apply the merges in the same order. The merge list *is* the tokenizer; it is shipped with the
model, and a model only works with the tokenizer it was trained with.

The simulation below trains a small BPE tokenizer on a few paragraphs about this course, right in
your browser, so you can watch merges appear. Slide the number of merges up and see words fuse
together; type your own sentence and count its tokens.

<!-- widget:tokenizer -->

Things to try:

- With 0 merges, every character is a token. Watch the count fall as merges are added.
- Type a word that appears in the training text (`agent`) and one that does not (`xylophone`).
  The first becomes one token; the second stays in pieces.
- Type a number with many digits, or a string of emoji. Tokenizers are bad at both, and this is why
  models are bad at arithmetic on long numbers: they never see the digits as one thing.

## Special tokens

The vocabulary also contains tokens that never come from text: markers for the start and end of a
document, and, after post-training, markers for the roles in a chat, such as *begin user turn* and
*end assistant turn*. A chat is not sent to the model as JSON with roles; the chat template (chapter
F5) writes it out as one long token sequence with these markers in it. Keep this in mind when
prompt injection comes up in chapter F7: to the model, your system message and a web page a tool
fetched are just tokens in the same sequence.

## From ids to vectors: embeddings

A token id is a label, not a quantity; id 3404 is not "more" than id 374. The first thing the model
does is look each id up in a table, the **embedding matrix**, and take out a vector: a list of a
few thousand numbers (4,096 in a typical 7-billion-parameter model). Those numbers are learned
during training, and they end up encoding meaning: tokens that appear in similar contexts get
similar vectors. Day 2 of the course uses the same idea for search; here it is the model's first
layer.

Position matters too, since "dog bites man" and "man bites dog" contain the same tokens. Each
position's vector is adjusted by a **positional encoding** so that the model can tell first from
second. Modern models use a rotation scheme (RoPE) that makes relative distances easy to use, which
is part of why long contexts work at all.

After this step the input is a matrix: one row of 4,096 numbers per token. Chapter F2 is what
happens to that matrix.

## What this explains elsewhere in the course

- **Cost and limits are counted in tokens** because tokens are what the model processes; the
  `usage` field in Day 1's first reply is counting exactly these.
- **Context windows** (32K, 128K, 1M) are the maximum number of tokens in one call, input and
  output together.
- **Ollama's `num_ctx`** and the models' RAM needs (Ollama module) grow with the number of tokens
  kept in play.

## Recap

- The model receives token ids, not text; a BPE tokenizer builds its vocabulary by merging frequent pairs, and the merge list ships with the model.
- One token is about three quarters of an English word; other scripts, code and digits cost more.
- Each id becomes a learned vector plus position information; chats are one token sequence with special role markers.
