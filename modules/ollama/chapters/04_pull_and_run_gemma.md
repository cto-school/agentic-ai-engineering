# Pull Gemma 3 and use it from the terminal

Everything in this chapter is the `ollama` command. Replace `gemma3:4b` with the tag you chose in O3.

## Download the model

```bash
ollama pull gemma3:4b
```

You see a progress bar per layer, then `success`. The download is resumable: if it stops, run the
same command again. Check what you have:

```bash
ollama list
```

```text
NAME          ID              SIZE      MODIFIED
gemma3:4b     a2af6cc3eb7f    3.3 GB    2 minutes ago
```

## Talk to it

```bash
ollama run gemma3:4b
```

The first start takes a few seconds while the model is loaded into RAM. Then you get a prompt:

```text
>>> Explain in two sentences what a tokenizer does.
```

Type, press Enter, and the answer streams word by word. The conversation keeps its history until you
leave, so follow-up questions work ("make that simpler"). Leave with `/bye` or Ctrl+D.

To paste several lines at once, wrap them in triple quotes:

```text
>>> """
Summarise this in one line:
Ollama runs models locally. It exposes an HTTP API on port 11434.
"""
```

`ollama run` also accepts the prompt on the command line, prints the answer and exits, which is
handy in scripts:

```bash
ollama run gemma3:4b "Give me three names for a study-group app."
```

## Slash commands inside the chat

| Command | What it does |
|---|---|
| `/?` | list the commands |
| `/show info` | model family, parameter count, quantisation, context length |
| `/show system` | the current system prompt |
| `/set system You are a terse assistant.` | change the system prompt for this session |
| `/set parameter temperature 0.2` | change a sampling parameter (0 is deterministic, 1 is creative) |
| `/set parameter num_ctx 8192` | set the context window in tokens (more RAM) |
| `/save tutor` | save the current settings as a new model named `tutor` |
| `/clear` | forget the conversation so far |
| `/bye` | exit |

Try this sequence and watch the answers change:

```text
>>> /set system You answer only with a numbered list of at most three items.
>>> How do I revise for an exam?
>>> /set parameter temperature 0
>>> How do I revise for an exam?
>>> How do I revise for an exam?
```

With temperature 0 the last two answers are identical. That is the difference between sampling and
picking the most likely word, which the LLM Foundation module explains from the inside.

## Images (4B and larger)

Gemma 3 from 4B upward reads images. Put the path to a PNG or JPEG in the prompt:

```text
>>> What is in this picture? C:\Users\you\Pictures\whiteboard.jpg
```

Ollama notices the file path, loads the image and sends it with your question.

## Manage the models on disk

```bash
ollama ps            # which models are loaded in memory right now, and for how long
ollama stop gemma3:4b   # unload it from memory (the file stays on disk)
ollama show gemma3:4b   # details: parameters, context length, licence, template
ollama rm gemma3:1b     # delete a model you no longer want
ollama pull gemma3:4b   # run again later to fetch an updated version
```

`ollama ps` is worth reading once. The `PROCESSOR` column says `100% CPU` on a laptop without a
GPU, and the `UNTIL` column shows when the server will unload the model if no request arrives
(five minutes by default).

## Recap

- `ollama pull`, then `ollama run`, then talk; `/bye` to leave.
- Slash commands change the system prompt and sampling parameters without leaving the chat; `/save` keeps them.
- `ollama list`, `ps`, `stop`, `show` and `rm` manage what is on disk and in memory.
