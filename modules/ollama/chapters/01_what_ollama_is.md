# What Ollama is, and what "running a model locally" means

Everywhere else in this course a model lives on someone else's computer. You send a request over the
internet, a data centre runs the model, and the reply comes back. That is convenient, but it costs
money per token, it needs a network connection, and your text leaves your machine.

**Ollama** is a small program that runs open-weights language models on your own computer and
exposes them through the same kind of interface. Nothing leaves your laptop, nothing is billed, and
the model keeps working on a train with no signal.

## The three things you are actually downloading

A "model" on disk is not a program. It is three things bundled together:

1. **Weights.** Billions of numbers, the result of training (the LLM Foundation module explains
   where they come from). For Gemma 3 with 4 billion parameters, that is 4 billion numbers.
2. **A tokenizer.** The table that turns your text into token ids and back.
3. **A chat template.** The exact text layout the model was trained to see: where the system
   message goes, how a user turn and an assistant turn are marked.

Ollama stores all of this in one file format, **GGUF**, and keeps a small manifest per model so that
`ollama run gemma3:4b` knows which file to load and how to talk to it.

## Why it fits on a laptop: quantisation

Each weight was trained as a 16-bit or 32-bit number. Stored that way, a 4-billion-parameter model
needs about 8 GB of memory before it has read a single word. **Quantisation** rounds each weight to
4 bits (or 5, 6, 8). The model becomes three to four times smaller and slightly less precise, and
in practice the difference is hard to notice for everyday use. The Gemma 3 files Ollama downloads
by default are 4-bit quantised; `gemma3:4b` is a 3.3 GB download.

Rule of thumb you will use in chapter O3: a 4-bit model needs roughly **0.6 GB of RAM per billion
parameters**, plus one to two gigabytes of working space for the conversation.

## No graphics card is fine

A dedicated GPU makes generation faster because it multiplies large matrices quickly. Without one,
Ollama runs the same model on the CPU using ordinary system RAM. It is slower (a few words per second
instead of tens), but the answers are the same. Everything in this module assumes a laptop with
integrated graphics and 8 or 16 GB of RAM.

## How the pieces fit (diagram D50)

Ollama is two programs that talk to each other:

- **The server** (`ollama serve`). It starts when you install Ollama, sits in the background, and
  listens on `http://localhost:11434`. It loads a model into memory on first use, keeps it there
  for a few minutes in case the next request arrives, then unloads it.
- **The client.** The `ollama` command in your terminal is one client. A Python script is another.
  A chat app is a third. They all send HTTP requests to the server; the server owns the model.

The server runs the model with a runtime built on **llama.cpp**, a C++ library written specifically
to run quantised models efficiently on ordinary CPUs. You never see llama.cpp; it is the reason the
whole thing is possible on your laptop.

## Before the next chapter: know your machine

Find out two numbers. They decide which model size you install in O3.

```powershell
# Windows: total memory in GB, and the processor name
(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
(Get-CimInstance Win32_Processor).Name
```

```bash
# macOS
sysctl -n hw.memsize | awk '{print $1/1024/1024/1024 " GB"}'
sysctl -n machdep.cpu.brand_string
```

```bash
# Linux
free -g
lscpu | grep 'Model name'
```

Write the RAM figure down. Also check free disk space: the models in this module need between 1 GB
and 4 GB each.

## Recap

- Ollama runs open-weights models on your machine and serves them at `localhost:11434`.
- A model on disk is weights, a tokenizer and a chat template in one GGUF file; 4-bit quantisation makes it small enough for a laptop.
- No GPU means slower generation, not worse answers. Know your RAM before choosing a model.
