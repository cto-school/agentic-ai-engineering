# Choose a model that fits a laptop without a GPU

Ollama's library has hundreds of models. Choosing badly wastes an hour of downloading and ends in an
"out of memory" message. Choosing well takes one number (your RAM) and one table.

## Names, sizes and tags

A model in Ollama is named `family:tag`. The tag usually carries the parameter count:

```text
gemma3:1b      Gemma 3, 1 billion parameters
gemma3:4b      Gemma 3, 4 billion parameters
gemma3:270m    Gemma 3, 270 million parameters
```

"Parameters" are the weights from chapter O1. More parameters means a more capable model, a larger
download, more RAM, and slower generation. The relationship is close to linear for all four.

## The memory rule of thumb

For the default 4-bit files:

```text
RAM needed  ≈  0.6 GB × (billions of parameters)  +  1.5 GB of working space
```

Your operating system, browser and editor need memory too. Plan to leave 3 GB for them.

| Tag | Download | RAM the model needs | Comfortable on | Notes |
|---|---|---|---|---|
| `gemma3:270m` | 292 MB | under 1 GB | anything | fast, simple tasks only; a fine first test |
| `gemma3:1b` | 815 MB | about 2 GB | 8 GB laptops | quick on a CPU; good summaries and rewrites |
| `gemma3:4b` | 3.3 GB | about 4 GB | 16 GB laptops, 8 GB if you close everything else | the sweet spot for this course; reads images too |
| `gemma3:12b` | 8.1 GB | about 9 GB | 16 GB with nothing else open, 32 GB | noticeably slow on a CPU |
| `gemma3:27b` | 17 GB | about 19 GB | 32 GB or more, ideally a GPU | not a laptop model |

The 1B and 270M variants are text-only and have a 32K-token context window. From 4B upward Gemma 3
accepts **images** as input and has a 128K context window.

## What to expect from speed

On a recent laptop CPU (no GPU), roughly:

- `gemma3:1b`: 15 to 30 tokens per second, faster than you can read.
- `gemma3:4b`: 4 to 10 tokens per second, about reading speed.
- `gemma3:12b`: 1 to 3 tokens per second, patience required.

The first reply after a pause is always slower: the server is loading the model from disk into RAM.
After that, replies start quickly.

## The decision (diagram D51)

```text
RAM 8 GB   →  gemma3:1b   (try gemma3:4b later with other apps closed)
RAM 16 GB  →  gemma3:4b
RAM 32 GB+ →  gemma3:12b if you want quality over speed, otherwise gemma3:4b
```

This module continues with `gemma3:4b` in the examples. If you chose 1B, substitute the tag; every
command is otherwise identical.

## Why Gemma 3, and what else exists

Gemma 3 is Google's open-weights family: permissive licence, small sizes that are genuinely useful,
built-in vision from 4B, and it follows instructions well for its size. Reasonable alternatives at
similar sizes, if you want to compare later: `llama3.2:3b` (Meta), `qwen3:4b` (Alibaba, strong at
code and multilingual text), `phi4-mini` (Microsoft). The rule of thumb above applies to all of
them.

Two things to know when browsing [ollama.com/library](https://ollama.com/library):

- A tag ending in `-it` means *instruction-tuned* (a chat model). Base models without it complete
  text instead of answering; the plain `gemma3:4b` tag is already the chat version.
- Tags such as `gemma3:4b-it-qat` are **quantisation-aware trained**: the model was trained knowing
  it would be rounded to 4 bits, so it loses less quality. Same size, slightly better answers; a
  good choice once you are comfortable.

## Recap

- RAM decides: 8 GB means `gemma3:1b`, 16 GB means `gemma3:4b`.
- Rule of thumb: about 0.6 GB per billion parameters plus working space, for 4-bit files.
- Bigger is better and slower in equal measure; the first reply is slow because the model is loading.
