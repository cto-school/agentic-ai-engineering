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

Students should normally open the single master notebook for the current day: `day_01_complete.ipynb` through `day_05_complete.ipynb`. Each master notebook starts with one **Environment setup** cell (Colab clone and install, or local `.env` loading), then a linked contents list, all guided sections, one hands-on exercise with a commented reference solution, and the integrated daily project. The 45 files inside the day-specific `notebooks/` folders remain available as focused standalone lessons and are the maintained source of truth.

## How the lessons teach

Every lesson is a step-by-step build: a short explanation, then a code cell that does one thing and prints labelled output, with comments where a beginner needs them. Each lesson contains at most one **Try it yourself** prompt, immediately followed by a fully commented worked solution, and ends with a **Checkpoint** (answers folded under *Show answer*) and a three-line **Recap**. Every notebook runs completely without an API key in deterministic mock mode; live model calls are used only where model behaviour is the lesson and always fall back to mock on failure.

## API key and `.env` file

Day 1 Lesson 1 walks through creating the `.env` file: copy `.env.example` to `.env` in the repository root (next to `README.md`), put `OPENROUTER_API_KEY=...` in it, never commit it. Every notebook's setup cell loads that file automatically. On Google Colab the master notebook's setup cell asks for the key instead and keeps it only in that runtime.

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
py build_student_learning_materials.py
py validate_course.py
```

The first command idempotently embeds the maintained theory sources (`day_*/theory.md`), rebuilds the six exercise notebooks, and regenerates the five master notebooks. The per-day `build_notebooks.py` and `enrich_day1_day2_notebooks.py` generators are archived: the lesson notebooks are hand-maintained and those scripts refuse to run without `--force`. The validator checks notebook JSON and code-cell syntax, compiles reference Python,
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

The final notebook set contains 45 progressive notebooks, including six pivotal exercise notebooks and one operational website-maintenance capstone. Days 3–5 have been executed
end-to-end in offline mode; live-provider and hosted-product smoke checks remain part of
the instructor's pre-delivery checklist because they depend on credentials, quotas,
network policy, and current SDK behavior.
