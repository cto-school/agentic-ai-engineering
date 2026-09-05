# Inside the Transformer

Between the embedding matrix from chapter F1 and the probabilities of chapter F3 sits the
**Transformer**, the architecture behind every current large language model. It is a stack of
identical blocks, each of which does two things: let every token look at the tokens before it, and
then think about what it saw. Diagram D61 draws one block; this chapter explains it in words.

## The residual stream

Picture each token's vector as a lane running from the bottom of the model to the top. The blocks
do not replace the vector; they **add** to it. Each block reads the lane, computes an adjustment,
and adds it back. This "residual stream" is why models with 30 to 100 blocks can be trained: the
original signal is never lost, only refined.

## Part 1: attention

The vector for the token `it` in "the cup fell off the table and it broke" needs to know that `it`
refers to the cup. **Attention** is the mechanism that moves information between positions.

For each token, the block computes three smaller vectors by multiplying with learned matrices:

- a **query**: what am I looking for?
- a **key**: what do I contain?
- a **value**: what will I pass on if someone looks at me?

The token's query is compared with the key of every earlier token (a dot product gives a score).
The scores go through a softmax so they sum to one, and the token collects a weighted sum of the
earlier tokens' values. `it` ends up with a high weight on `cup` and pulls its meaning across.

Three details that matter downstream:

- **Causal masking.** A token may only attend to tokens before it. That is what makes the model a
  next-token predictor rather than a fill-in-the-blank model, and what makes the KV cache possible
  (chapter F6).
- **Heads.** Each block runs attention several times in parallel with different matrices (32 heads
  in a 7B model). One head may track grammar, another coreference, another which line of code a
  bracket belongs to. Their outputs are concatenated.
- **Cost.** Every token compares with every earlier token. Attention work grows with the *square*
  of the sequence length. This is the reason long contexts are slow and expensive, and the reason
  context management (Day 3) exists.

## Part 2: the feed-forward network

After attention, each token's vector, on its own, passes through a small two-layer neural network
(the **MLP**): expand to a wider vector, apply a non-linearity, contract back. This is where most
of the parameters live, roughly two thirds, and most of what looks like stored knowledge. Facts
such as "the capital of France is Paris" are patterns in these matrices. Attention moves
information around; the MLP transforms it.

Newer models replace the single MLP with a **mixture of experts**: several MLPs of which a router
picks two or so per token. The model has many parameters in total but uses a fraction per token,
which is how a model like GPT-OSS-120B (the course's default) runs cheaply.

## Normalisation, and the whole stack

Before each of the two parts, the vector is normalised (scaled to a standard size) so that training
stays stable. A block is therefore: normalise, attend, add; normalise, MLP, add. A model is that
block repeated: 32 times for a 7B model, 80 or more for the largest. All blocks have the same
shape and different learned weights.

Sizes, for a sense of scale (a typical 7-billion-parameter open model):

| Quantity | Value |
|---|---|
| vocabulary | 128,000 tokens |
| vector width | 4,096 numbers |
| blocks | 32 |
| attention heads per block | 32 |
| MLP hidden width | 14,336 |
| parameters | about 7 billion |

Gemma 3's 4B model (Ollama module) is the same design at smaller widths; the 270M model is the same
design again.

## The last step: from vector to vocabulary

At the top of the stack, the final vector of the *last* token is multiplied by one more matrix (the
"unembedding", often the embedding matrix reused) to give one number per vocabulary entry: the
**logits**. A large logit means "this token is a likely continuation". Chapter F3 turns logits into
a choice.

Note that only the last position produces the next token, but every position was computed. During
training that is not waste: each position is predicting *its* next token, so one pass over a
document gives a training signal at every token.

## It is all matrix multiplication

Nothing above is a rule or a lookup. Attention, the MLP and the unembedding are multiplications of
the token matrix by learned weight matrices, with a softmax and a non-linearity between them. That
is why GPUs matter (they multiply large matrices fast), why quantisation works (the numbers in the
matrices can be rounded), and why nobody can point at the line of code that "knows" a fact.

## Recap

- A Transformer is a stack of identical blocks that add refinements to each token's vector: attention (move information between positions) then an MLP (transform it).
- Attention is causal and its cost grows with the square of the context length; most parameters and most stored knowledge sit in the MLPs.
- The final vector of the last token is projected to one logit per vocabulary entry.
