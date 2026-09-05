# Standalone modules

Five self-contained modules sit beside the five-day course and the two notebook tracks. They are
**not** notebooks: each is a short sequence of Markdown chapters with theory, architecture diagrams
and step-by-step instructions, read in the course portal or straight from this folder. None of them
requires the others, and none is part of the five-day timetable.

| Module | Folder | Chapters | What you end up with |
|---|---|---|---|
| Ollama | [`ollama/`](ollama/README.md) | 6 | Gemma 3 running locally on an ordinary laptop, driven from the terminal and from programs |
| n8n | [`n8n/`](n8n/README.md) | 7 | An n8n Cloud account and four working agents built on the visual canvas |
| OpenClaw | [`openclaw/`](openclaw/README.md) | 7 | An always-on personal assistant on your own hardened AWS EC2 machine, reachable through Telegram, powered by Gemini |
| LLM Foundation | [`llm_foundation/`](llm_foundation/README.md) | 7 | A working mental model of how a large language model is built, trained and run, with two in-browser simulations |
| Mem0 | [`mem0/`](mem0/README.md) | 7 | A memory layer for your agents: the Platform, how add and search work, wiring into an agent, running it locally, evaluation and privacy |

## Conventions

- Each module folder has a `README.md` that lists its chapters in order, and a `chapters/` folder
  with one Markdown file per chapter, numbered `01_`, `02_`, and so on.
- Every chapter starts with a level-one heading (its title), ends with a three-line **Recap**, and
  references its architecture diagrams by id (`D50`, `D51`, ...). The diagram sources live in
  [`diagrams/source/`](../diagrams/source/) in one file per module.
- Commands are written for the shell named in the fence (`bash` for macOS, Linux and the EC2
  machine; `powershell` for Windows). Placeholders are written in angle brackets, `<like-this>`.
- The portal's beginner guide for each chapter (idea, picture, steps, the thing to keep straight,
  the common mistake, what to check) lives in `course-portal/content/lesson-guides.json` and
  `common-mistakes.json`, keyed by the chapter file name.

To add or rename a chapter: edit the module README table, the chapter file, the two portal JSON
files and the `diagramMap` in `course-portal/scripts/build-course-content.mjs`, then run
`pnpm content` and `pnpm align` inside `course-portal/`.
