# Agentic AI Engineering

A five-day, project-based course for final-year engineering students who are new to agentic AI.

The course teaches students to first configure and use agentic systems, then understand their parts, and only later engineer reusable infrastructure around them.

## Learning journey

```text
Day 1: Model -> Structured Output -> Tool -> Agent
Day 2: Knowledge -> Retrieval -> RAG -> State
Day 3: Memory -> Planning -> Safety -> Human Approval
Day 4: Workflow -> Multi-Agent -> Observability -> Evaluation
Day 5: Runtime -> Tool Registry -> Guardrails -> MCP -> Harness -> Automation
```

The recurring learning pattern is:

```text
BUILD -> OBSERVE -> BREAK -> IMPROVE
```

## Course projects

| Day | Project | Main outcome |
|---|---|---|
| 1 | Smart Research Assistant | A bounded tool-using agent |
| 2 | Engineering Knowledge Assistant | A citation-producing RAG agent |
| 3 | Safe Personal Task Agent | An agent with memory and approval-controlled actions |
| 4 | Engineering Design Review Team | A measured single-agent versus multi-agent review system |
| 5 | Mini AI Harness + Website Maintenance Agent | A reusable runtime operating a guarded, persistent, scheduled workflow |

## Start here

1. Read [the course syllabus](syllabus/course_syllabus.md).
2. Complete [the installation guide](setup/installation_guide.md).
3. Check [accounts and API keys](setup/accounts_and_api_keys.md).
4. Start with [Day 1](day_01_model_tools_agent/README.md).

Students open one Google Colab notebook per day: `day_01_complete.ipynb` through `day_05_complete.ipynb`. Each day notebook is the **source of truth**: a short setup, the guided sections in order, one hands-on exercise with a commented reference solution, and the integrated daily project. The files inside each day's `notebooks/` folder are derived from the day notebook by `split_day_notebooks.py` so the course portal can show one lesson at a time; do not edit them by hand.

Every day notebook is fully self-contained: no repository clone, no local files, no `.env`. The data a day needs (document corpus, golden set, safety cases, seeded code artifact, harness configs, update feeds) is created by the notebook itself, and the reference `src/` packages are an optional packaged version of the same designs for instructors.

## How the lessons teach

Every lesson is a step-by-step build: a short explanation, then a code cell that does one thing and prints labelled output, with comments where a beginner needs them. Each lesson contains at most one **Try it yourself** prompt, immediately followed by a fully commented worked solution, and ends with a **Checkpoint** (answers folded under *Show answer*) and a three-line **Recap**. Every notebook runs completely without an API key in deterministic mock mode; live model calls are used only where model behaviour is the lesson and always fall back to mock on failure.

## API key

Students work in Google Colab. The setup cell at the top of each day notebook looks for a Colab secret named `OPENROUTER_API_KEY` (key icon in Colab's left sidebar), then an environment variable, and otherwise asks once; pressing Enter keeps the notebook in mock mode. Instructors running locally can still put the key in a `.env` file copied from `.env.example`.

## Separate tracks: LangGraph and LangChain

Two more self-contained Colab notebooks sit outside the day sequence. Each grows one project through
short iterations; there are no exercises, and both run on a built-in mock chat model without a key.

**LangGraph track** (`langgraph_track/langgraph_complete.ipynb`) teaches LangGraph from scratch and is
fully self-contained. CampusAI, a university helpdesk assistant, starts as a three-node graph with
no model in it and gains, one section at a time: a model node and reducers, tools and the agent
loop, structured output and routing with subgraphs, a checkpointer with context management, a
store for long-term memory, retrieval by meaning, permissions and human approval (including a
prompt-injection attack), retries and limits, parallel fan-out with `Send`, tools served over MCP,
a supervisor with specialists and a handoff, streaming with tracing, evaluation and a taste of
LangSmith, scheduled unattended runs, and finally one assembled system. See [the track README](langgraph_track/README.md).

**LangChain track** (`langchain_track/langchain_complete.ipynb`) teaches agents with LangChain 1.x on top of LangGraph.

`langchain_track/langchain_complete.ipynb` is one more self-contained Colab notebook that teaches
the same ideas through **LangChain 1.x** (`create_agent`, tools, middleware, structured output) and
**LangGraph** (persistence, interrupts, explicit workflows). Students grow one agent, OpsPilot,
fourteen times: model call, tool loop by hand, `create_agent()`, hardened tools, structured output,
conversation memory, long-term memory, retrieval, planning, middleware and permissions,
human-in-the-loop, an explicit graph, a supervisor with specialists, and streaming with tracing.
There are no exercises; each section is theory, a sketch, runnable commented code and a recap.
Without a key the notebook runs on a built-in mock chat model, so every mechanism can be studied for
free. See [the track README](langchain_track/README.md). The portal lists both tracks in a separate
sidebar group beside the five-day path.

## Standalone modules: Ollama, n8n, OpenClaw, LLM Foundation and Mem0

Five short modules under [`modules/`](modules/README.md) sit beside the days and the tracks and
are **not notebooks**: each is a sequence of Markdown chapters with theory, architecture diagrams
(`diagrams/source/ollama.md`, `n8n.md`, `openclaw.md`, `llm_foundation.md`, `mem0.md`) and step-by-step
instructions, read in the portal's "Standalone modules" group or straight from the folder. None
of them is part of the five-day timetable and none depends on another.

- **Ollama** (6 chapters): run Gemma 3 on a laptop without a GPU, from the terminal and from
  programs, with a Modelfile and the OpenAI-compatible endpoint the course's helper can use.
- **n8n** (7 chapters): open an n8n Cloud account (no installation) and build four agents on the
  visual canvas: chat with memory, tools, structured-output triage, and a supervisor with
  specialist workflows.
- **OpenClaw** (7 chapters): open an AWS account without living as root, launch an Ubuntu EC2
  machine, log in over SSH and disable root and password access, then install OpenClaw, connect
  a Telegram bot and run it on a Gemini API key.
- **LLM Foundation** (7 chapters): how a language model is built, trained and run, from tokens
  and the Transformer to sampling, pretraining, post-training, inference and limits, with two
  in-browser simulations in the portal (a trainable BPE tokenizer and a next-token predictor).
- **Mem0** (7 chapters): a memory layer for agents: the Platform account and first memories, how
  add and search work inside, the search-then-add pattern in plain Python, LangGraph and n8n,
  shaping what is remembered, running Mem0 locally with Ollama or as a self-hosted server, and a
  recall-and-isolation evaluation with privacy and operations duties.

## Interactive course portal

The React portal in [`course-portal/`](course-portal/) provides a collapsible five-day lesson tree, in-browser theory and code reading, architecture views, progress tracking, notebook downloads, and Google Colab launch links. After cloning the repository:

```powershell
cd course-portal
pnpm install
pnpm dev
```

Colab links default to `cto-school/agentic-ai-engineering` on `main`; a different fork or branch can be entered on the portal's **Getting started** page (stored in the browser) and in `REPO_URL` inside `build_master_notebooks.py`.

Instructors should also use the [five-day classroom timetable](instructor/five_day_timetable.md). All student-facing theory is embedded directly in the relevant notebooks.

Six [pivotal coding exercise notebooks](exercises/README.md), one per day (two on Day 3), provide a small implementation stub, a deterministic behavioural check, and a commented reference solution.

## Validate the repository

After installing the required packages, run:

```powershell
py split_day_notebooks.py
py validate_course.py
```

The first command derives the lesson notebooks from the five day notebooks and the two track notebooks. The older generators (`build_master_notebooks.py`, `build_student_learning_materials.py`, the per-day `build_notebooks.py`, `enrich_day1_day2_notebooks.py`) worked in the opposite direction and are archived: they refuse to run without `--force`. The validator checks notebook JSON and code-cell syntax, compiles reference Python,
runs dependency-compatible offline tests, and confirms key teaching documents. It
reports tests skipped because a staged dependency is not installed.

## Course design

- OpenRouter with GPT-OSS is the consistent classroom inference route.
- Ollama is an optional local-provider comparison; mock mode is always available.
- Direct OpenAI API usage is shown once as an optional alternative.
- Notebooks contain contextual theory and guided implementation.
- Reusable logic belongs in ordinary Python modules.
- Detailed architectural diagrams live outside notebooks.
- Every project must support a mock mode for fast, deterministic testing.
- Terminology is introduced only after students encounter the problem it solves.
- Hosted services use synthetic course data only.

See [locked curriculum decisions](syllabus/locked_decisions.md) for the design baseline.

## Repository status

This repository contains the approved course architecture, project specifications,
setup plan, templates, glossary, and diagram plan. All five days now include complete
beginner-facing notebooks, ordinary-Python reference implementations, mock/local
paths, data, and tests. The repository is ready for an instructor pilot and
clean-machine/live-service validation before classroom delivery.

The five day notebooks contain 39 sections, including one hands-on exercise per day (two on Day 3, the second as a worked Try-it) and one operational website-maintenance capstone. Days 3–5 have been executed
end-to-end in offline mode; live-provider and hosted-product smoke checks remain part of
the instructor's pre-delivery checklist because they depend on credentials, quotas,
network policy, and current SDK behavior.
