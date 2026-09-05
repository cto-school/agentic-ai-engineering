# LLM Foundation module diagram sources

## D60 — From text to tokens to vectors

```mermaid
flowchart LR
    T["Text"] -->|"BPE merges"| K["Tokens"]
    K -->|"vocabulary lookup"| I["Token ids"]
    I -->|"embedding matrix"| V["Vectors, one per token"]
    V -->|"+ position"| M["Input matrix for the Transformer"]
```

Text alternative: the tokenizer splits text into sub-word tokens using its merge list, each token becomes an id, each id is looked up in the embedding matrix to give a vector, and positional information is added before the matrix enters the Transformer.

## D61 — One Transformer block

```mermaid
flowchart TD
    X["Token vectors in"] --> N1["Normalise"]
    N1 --> AT["Attention: each token reads earlier tokens"]
    AT -->|"add to residual stream"| X2["Token vectors"]
    X2 --> N2["Normalise"]
    N2 --> MLP["Feed-forward network: transform each token"]
    MLP -->|"add to residual stream"| Y["Token vectors out"]
    Y -->|"repeat for every block, then unembed"| L["Logits over the vocabulary"]
```

Text alternative: a block normalises the token vectors, lets each token attend to earlier tokens and adds the result, then normalises again, transforms each token with a feed-forward network and adds that too; the blocks repeat, and the final vector of the last token is projected to one logit per vocabulary entry.

## D62 — How a model is trained

```mermaid
flowchart LR
    D["Trillions of cleaned tokens"] --> P["Pretraining: predict the next token"]
    P --> B["Base model: completes text"]
    B --> S["SFT on example conversations with a chat template"]
    S --> R["RLHF or DPO on preferences"]
    R --> V["RL with verifiable rewards: reasoning and tool use"]
    V --> C["Chat model you call"]
```

Text alternative: pretraining on trillions of tokens produces a base model that completes text; supervised fine-tuning teaches the chat template, preference training shapes helpfulness and refusals, and reinforcement learning with checkable rewards adds reasoning and reliable tool use, yielding the chat model.

## D63 — Inference: prefill, decode and the KV cache

```mermaid
flowchart LR
    PR["Prompt tokens"] -->|"one parallel pass"| PF["Prefill"]
    PF --> KV["KV cache: keys and values per token"]
    PF --> T1["First token"]
    T1 --> DE["Decode: one token per pass"]
    KV --> DE
    DE -->|"append, store keys and values"| KV
    DE -->|"until end token or max_tokens"| OUT["Reply, streamed as it appears"]
```

Text alternative: the prompt is processed in one parallel prefill pass that fills the KV cache and yields the first token; decode then produces one token per sequential pass, reading and extending the cache, until an end token or the length cap, streaming tokens as they appear.

## D64 — From logits to the chosen token

```mermaid
flowchart LR
    L["Logits"] -->|"divide by temperature"| S["Softmax: probabilities"]
    S -->|"top-p or top-k"| C["Truncated distribution"]
    C -->|"greedy or sample"| T["Chosen token"]
    T -->|"append and run again"| L
```

Text alternative: logits are divided by the temperature and turned into probabilities by softmax, the tail is cut by top-p or top-k, one token is chosen greedily or by sampling, and it is appended to the sequence before the model runs again.
