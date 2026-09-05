# Customise a model with a Modelfile, and fix the usual problems

A **Modelfile** is a recipe: start from a downloaded model, fix a system prompt and parameters, and
give the result a name. It is the local equivalent of the "configure the model's behaviour" step in
Day 1, and it means you never retype `/set system` again.

## Create a tutor model

Make a file called `Modelfile` (no extension) with this content:

```text
FROM gemma3:4b

# 0 is deterministic; 0.3 keeps explanations steady but not robotic
PARAMETER temperature 0.3

# tokens of context the model can see; more costs RAM
PARAMETER num_ctx 8192

SYSTEM """
You are a patient tutor for a course on AI agents.
Answer in plain language, at most 120 words, and end with one question
that checks whether the student understood.
"""
```

Build it and run it:

```bash
ollama create tutor -f Modelfile
ollama run tutor
```

```text
>>> What is a tool call?
```

`ollama list` now shows `tutor:latest`. It shares the underlying weights with `gemma3:4b`, so it
costs almost no extra disk space. `ollama show tutor --modelfile` prints the recipe back, which is
also how you can inspect the chat template of any model.

Useful `PARAMETER` lines:

| Parameter | Meaning | Typical |
|---|---|---|
| `temperature` | randomness of word choice | 0 to 1 |
| `num_ctx` | context window in tokens | 4096 to 32768 |
| `num_predict` | maximum tokens in a reply | 256 to 2048 |
| `top_p` | sample only from the most likely words summing to this probability | 0.9 |
| `repeat_penalty` | discourage repeating phrases | 1.1 |

## Server settings through environment variables

The server reads a few variables at start-up. Set them in the tray app's settings on Windows and
macOS, or in `systemctl edit ollama` on Linux, then restart Ollama.

| Variable | Purpose |
|---|---|
| `OLLAMA_MODELS` | store models on another drive, for example `D:\ollama-models` |
| `OLLAMA_KEEP_ALIVE` | how long a model stays loaded after the last request (`10m`, `1h`, `-1` for always) |
| `OLLAMA_CONTEXT_LENGTH` | default context window when a request does not set one |
| `OLLAMA_HOST` | address to listen on; `0.0.0.0` exposes the server to your network |
| `OLLAMA_NUM_PARALLEL` | how many requests to serve at once (each one costs RAM) |

Leave `OLLAMA_HOST` alone unless you need another device to reach the server. The server has no
authentication: anything that can reach the port can run the model.

## Problems you will meet

**"model requires more system memory (x GiB) than is available (y GiB)".** The model does not
fit. Close other applications, or use a smaller tag (`gemma3:1b`), or lower `num_ctx`.

**The first answer takes ten seconds, later ones start instantly.** Normal. The delay is the model
loading from disk. Raise `OLLAMA_KEEP_ALIVE` if you dislike it.

**Answers are very slow and the fan is loud.** Also normal for a CPU. Check `ollama ps`: if the
`SIZE` column is close to your RAM, the machine is swapping to disk; choose a smaller model.

**"Error: could not connect to ollama app" or "connection refused".** The server is not running.
Start the tray/menu-bar app, or run `ollama serve` in a terminal and keep it open.

**"listen tcp 127.0.0.1:11434: bind: address already in use".** A server is already running. You
do not need a second one; close the terminal and use the existing server.

**"pull model manifest: file does not exist".** Typo in the tag. Check the exact name on
[ollama.com/library](https://ollama.com/library).

**Nonsense or repeated words.** Raise `repeat_penalty` slightly, lower `temperature`, and check that
you are running an instruction-tuned tag rather than a base model.

**The model does not use the GPU.** Integrated graphics are not supported for acceleration; CPU is
expected on the laptops this module targets.

**Disk is filling up.** `ollama list` shows sizes; `ollama rm <tag>` deletes. Blob files are shared
between models built from the same base, so removing a Modelfile-derived model frees very little.

## Where to go from here

- Run any course notebook locally against `tutor` or `gemma3:4b` using the two-string substitution from O5.
- In n8n (the n8n module) the *Ollama Chat Model* node talks to a self-hosted n8n on the same machine; n8n Cloud cannot reach your laptop.
- The LLM Foundation module explains what quantisation, temperature and context windows do inside the model.

## Recap

- A Modelfile fixes a base model, a system prompt and parameters under a new name; `ollama create` builds it.
- Environment variables set server behaviour: where models live, how long they stay loaded, who can reach the port.
- Most failures are memory or a missing server; the fix is a smaller model or `ollama serve`.
