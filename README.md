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

Students should normally open the single master notebook for the current day: `day_01_complete.ipynb` through `day_05_complete.ipynb`. Each master notebook contains a linked contents list, all guided sections, checkpoints, exercises, and the integrated daily project. The 45 files inside the day-specific `notebooks/` folders remain available as focused standalone lessons and are the maintained source of truth.

## Interactive course portal

The React portal in [`course-portal/`](course-portal/) provides a collapsible five-day lesson tree, in-browser theory and code reading, architecture views, progress tracking, notebook downloads, and Google Colab launch links. After cloning the repository:

```powershell
cd course-portal
pnpm install
pnpm dev
```

Once the GitHub repository URL is final, enter `owner/repository` in the portal's Colab setup. Every lesson then receives its corresponding one-click Colab link.

Instructors should also use the [five-day classroom timetable](instructor/five_day_timetable.md). All student-facing theory is embedded directly in the relevant notebooks.

Six [pivotal coding exercise notebooks](exercises/README.md) replace selected copy-and-run steps with small implementation stubs and deterministic behavioural checks.

## Validate the repository

After installing the required packages, run:

```powershell
py build_student_learning_materials.py
py validate_course.py
```

The first command idempotently embeds the maintained theory sources and rebuilds the six exercise notebooks after any day-specific generator is run. The validator checks notebook JSON and code-cell syntax, compiles reference Python,
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
