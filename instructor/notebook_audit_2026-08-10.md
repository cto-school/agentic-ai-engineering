# Notebook Content Audit — 10 August 2026

> **Remediation status — 11 August 2026:** The audit was critically reviewed and its
> substantive findings were implemented. Checklist-style padding was rejected. Days 3–5
> received tailored beginner guidance; Day 3 gained model-proposed actions; Day 4 gained
> validated provider-backed general/specialist reviewers and telemetry; Day 5 gained live
> OpenRouter/Ollama adapters, cancellation, durable checkpoints, and policy-gated MCP
> discovery. All 38 notebooks now include tailored outcomes, expected observations,
> exercises, recaps, and diagram references. Offline code paths for all 23 Day 3–5
> notebooks were executed successfully. Remaining pre-delivery checks require external
> credentials or a clean environment and are tracked below.

## Remaining external validation after remediation

- Execute Days 1–2 after installing their staged dependencies in a clean environment.
- Run the OpenRouter smoke path for Days 1, 3, 4, and 5 with the issued classroom model.
- Execute Mem0/LangSmith guided cells with synthetic data and verify current quotas/UI.
- Install the pinned stable MCP SDK and execute the real stdio server/client cell.
- Pilot with beginners and adjust density based on observed learning, not word counts.

## Audit purpose

This is a beginner-classroom audit of all 38 notebooks. It evaluates whether a final-
year engineering student who is new to agentic AI can learn from the notebooks in
sequence—not merely whether their JSON and Python syntax are valid.

The audit did not rewrite notebook content. Because every day's notebooks are generated
by `build_notebooks.py`, approved corrections should be made in those generators and
then regenerated; editing `.ipynb` files directly would be overwritten.

## Executive verdict

The **course architecture and concept order are strong**. Day 1 is the closest to a
complete beginner teaching day, Day 2 is a usable guided skeleton, and Days 3–5 contain
sound reference ideas but are too compressed to serve as the promised primary teaching
material without substantial expansion.

The repository is technically coherent but **not yet classroom-release ready**. The
largest issue is not formatting: several advanced “agent” lessons currently demonstrate
deterministic application logic while leaving the live model-driven implementation as
prose. That is useful for stable testing, but students also need to build and observe the
actual model/configuration path before calling the result an agentic system.

## Evidence snapshot

| Day | Notebooks | Markdown theory words | Audit assessment |
|---|---:|---:|---|
| Day 1 | 7 | 1,803 | Closest to classroom-ready; needs expected outputs and diagram links |
| Day 2 | 8 | 1,167 | Good progression; explanations and exercises are too brief |
| Day 3 | 9 | 609 | Reference demonstrations, not yet full beginner lessons |
| Day 4 | 7 | 679 | Evaluation design is good; model-driven multi-agent implementation is missing |
| Day 5 | 7 | 636 | Harness structure is good; live provider and real MCP path need completion |

Days 3–5 average roughly 60–100 theory words per notebook. That is insufficient for
new terms such as compaction, provenance, interrupts, fan-out/fan-in, supervisor,
runtime, registry, protocol, and checkpoint when those terms are also paired with new
code and product exposure.

## Release-blocking findings

### P0.1 — Day 4 does not yet build actual model-driven reviewers

The single reviewer and specialist reviewers in `src/review_team/reviewers.py` are
deterministic string-pattern rules. This is an excellent offline oracle for testing the
workflow, but it does not teach students how to configure three model roles, request
structured findings, handle malformed model output, or preserve provider usage.

Notebook 2 describes a live-model replacement and Notebook 7 calls it optional. For the
course objective “diving into multi-agent systems,” at least one required path must run
the same OpenRouter model as a general reviewer and as bounded specialists. The
deterministic implementation should remain as the mock baseline.

Required correction:

1. Add a shared OpenRouter reviewer adapter returning validated `Finding` objects.
2. Give general, correctness, security, and maintainability roles separate scoped prompts.
3. Save raw response, validation outcome, provider tokens, latency, and estimated cost.
4. Run the single and specialist configurations on the same artifact.
5. Keep retries bounded and fall back to supplied recorded/model-mock responses.
6. Clearly state that the seeded-rule 9/9 result tests orchestration only.

### P0.2 — Day 5 does not yet run a live AI provider through the harness

`build_provider()` supports mock mode and raises `NotImplementedError` for OpenRouter and
Ollama. The notebook asks students to implement the OpenRouter route as an exercise, but
the capstone requirement is a reusable AI harness, not only a mock workflow engine.

Required correction:

1. Move or adapt the tested Day 1 OpenRouter provider behind the Day 5 provider interface.
2. Preserve structured tool calls and provider usage metadata.
3. Show one research run in mock mode and one bounded run through OpenRouter.
4. Keep Ollama as an optional adapter, not a required repeated code listing.
5. Add provider failure and malformed-response handling to harness events.

### P0.3 — The real MCP core lab is commented out and has not been executed

The fake MCP client correctly teaches the discover/call shape, but the student-facing
real stdio cell is commented. The installed development environment did not contain the
MCP SDK, so the instructor server/client pair has only been syntax checked.

Required correction:

1. Establish and lock the classroom MCP SDK version after a clean install.
2. Execute the supplied server through `sys.executable` on Windows.
3. Make real discovery and one read-only call a required guided cell when the SDK is present.
4. Keep fake mode as the explicit outage fallback.
5. Import the discovered schema into the local registry, assign a local risk level, then
   invoke through policy so “discovery is not authorization” is demonstrated in code.

### P0.4 — Days 3–5 need full beginner instructional expansion

Most advanced notebooks contain only two markdown cells and two or three code cells.
They frequently introduce a concept, execute finished reference code, and end with a
discussion prompt. Students do not see enough intermediate construction or expected
state changes.

Every required notebook should contain:

- what students already know;
- two or three concrete learning outcomes;
- the new problem before the new term;
- a small build step rather than only importing the final implementation;
- an observation table or expected output description;
- one deliberately triggered failure;
- the improvement and why it works;
- a short modification exercise;
- a checkpoint answer students can explain without reading code;
- a recap distinguishing the new layer from earlier layers;
- a clear required/optional/fallback label.

## High-priority cross-course findings

### P1.1 — Diagrams exist but are not linked from notebooks

All 18 Mermaid diagrams now exist outside the notebooks, as intended, but none of the
notebooks points students to the relevant diagram. Add a short “Architecture reference”
markdown cell with a relative link and text alternative at the moment each relationship
becomes difficult to hold mentally.

Do not place the complete layer map in Day 1. Preserve progressive disclosure.

### P1.2 — Expected outputs are rarely stated

Beginners need to know whether a long dictionary, empty list, pause state, or abstention
is correct. Add a compact expected-observation note after important cells. Avoid baking
unstable live-model wording into the notebook; state shapes and invariants instead.

Examples:

- “You should see `pending_approval`, and the simulated sent list must remain empty.”
- “The exact wording may vary, but the result must include a citation.”
- “The multi-agent run should record three reviewer calls before supervisor synthesis.”

### P1.3 — Required, optional, and instructor-demo paths need visual consistency

The course policy is correct, but labels vary across notebooks. Use the same callout
convention everywhere:

- **Required — all students**
- **Choose one — OpenRouter or mock fallback**
- **Optional product exposure**
- **Instructor demonstration**
- **Extension after the core project**

This is especially important for Ollama, direct OpenAI, Mem0, LangSmith, Langfuse,
LangGraph interrupts, live multi-agent A/B, and MCP.

### P1.4 — Notebook setup cells assume the current working directory

Days 3–5 infer the day directory from `Path.cwd()` and only handle execution from the day
folder or `notebooks` folder. Jupyter launched from the repository root may produce the
wrong path. Introduce one shared, visible `find_course_root()` helper or a robust upward
search for the day directory. Teach the behavior once before hiding it in a helper.

### P1.5 — Notebook execution has not been tested end-to-end

The validator checks JSON and parses code cells, but it does not execute every notebook
in a clean kernel. Top-to-bottom execution is required because state leakage, path
assumptions, missing downloads, asynchronous cells, and live-service branches are not
detected by syntax validation.

Add a notebook execution profile:

- offline/mock notebooks executed automatically;
- optional hosted cells tagged and skipped in CI;
- live-service smoke notebooks run manually before delivery;
- output-cleared student copies generated only after known-good execution.

### P1.6 — Student work is mostly discussion, not code modification

Many exercises ask students to discuss or “try” a change but provide no incomplete cell,
assertion, or success condition. Add small edits such as:

- implement one validator;
- change a retrieval parameter and record the metric;
- add one policy case;
- add a specialist without changing supervisor code;
- register one new tool through configuration;
- classify a discovered MCP tool and prove denial.

Keep exercises local and bounded; do not require students to write large files from scratch.

## Day-by-day audit

### Day 1 — Model → Tool → Agent

Overall: **minor-to-moderate revision**.

Strengths:

- Best use of Build–Observe–Break–Improve in the repository.
- Model routes are introduced once with OpenRouter as the classroom default.
- Structured output precedes tool calling.
- Manual loop precedes LangGraph.
- Step limits and mock behavior are visible.

Required improvements:

- Add explicit learning outcomes to Notebooks 1 and 4 and the project notebook.
- Add invariant-based expected outputs to all seven notebooks.
- Link D01–D05 at the relevant notebook stage.
- Add prerequisite reminders before Pydantic and LangGraph notebooks.
- In Notebook 4, visually separate “model requested a tool” from “Python executed it.”
- In Notebook 6, deliberately trigger or inspect a graph routing failure; it currently
  lacks the “Break” portion found in the manual-loop lesson.
- Add one short recap to each notebook, not only a checkpoint question.

Notebook disposition:

| Notebook | Status | Main change |
|---|---|---|
| 01 First model call | Revise | Outcomes, expected response shape, route decision aid |
| 02 Model behavior | Light revise | Expected variability and recap |
| 03 Structured outputs | Light revise | Mock fallback and schema-error expected output |
| 04 Tool calling | Revise | Outcomes, execution-boundary diagram, explicit invariants |
| 05 Manual loop | Light revise | Expected trace and message-count exercise |
| 06 LangGraph | Revise | Deliberate routing failure and D05 link |
| 07 Project | Light revise | Project outcomes, submission artifact, expected behavior |

### Day 2 — Knowledge → Retrieval → RAG → State

Overall: **moderate revision**.

Strengths:

- Correct pedagogical order: inspect documents, keyword baseline, embeddings, RAG,
  citations, evaluation, retrieval as a tool, integrated project.
- Retrieval and answer evaluation are separated.
- The corpus is small, fictional, inspectable, and redistribution-safe.
- Abstention and citations are application-level behaviors rather than prompt slogans.

Required improvements:

- Expand each notebook to explain inputs and outputs before importing the completed module.
- Add learning outcomes and D06/D07 links.
- Show an expected chunk object, score interpretation, answer state, and evaluation row.
- Explain deterministic TokenHash embeddings as a teaching/mock mechanism before showing
  sentence transformers; students must not confuse them with production semantic quality.
- Make the Chroma and sentence-transformer download path clearly optional/fallback-aware.
- Add a concrete failure investigation worksheet: query, retrieved chunks, expected chunk,
  generator result, suspected layer, proposed change.
- Add at least one code modification exercise per notebook.

Notebook disposition:

| Notebook | Status | Main change |
|---|---|---|
| 01 Documents/chunks | Revise | Chunk rationale, expected record, D06 |
| 02 Keyword search | Revise | Explain ranking and record the failure |
| 03 Embeddings | Revise | Mock-vs-real distinction, download fallback, score caveat |
| 04 Basic RAG | Revise | Prompt/context anatomy and retrieval-vs-generation failure |
| 05 Citations/abstention | Revise | Citation invariant and explicit success cases |
| 06 Retrieval evaluation | Revise | Metric calculation before helper call |
| 07 Retrieval tool/state | Revise | State snapshots and context/state/memory contrast |
| 08 Project | Revise | Completion rubric and diagnostic exercise |

### Day 3 — Memory → Planning → Safety → Approval

Overall: **major expansion required**.

Strengths:

- Correct distinction between conversation history, compaction, and persistent memory.
- Transparent SQLite memory precedes Mem0.
- Policy is authoritative Python code.
- Approval pauses before execution, rejection is demonstrated, and injection-style cases
  cannot alter policy.
- Hosted products use synthetic data.

Required improvements:

- Convert Notebook 1's model exercise into a runnable OpenRouter-or-mock comparison.
- Build compaction in stages: measure budget, trim badly, observe lost fact, then summarize.
- Explain SQLite table fields and show persistence across store reopening.
- Demonstrate a conflicting memory and require explicit correction/deletion.
- Verify the current Mem0 lifecycle including search, inspection, and deletion—not only add/search.
- Build a small plan representation before calling `make_plan()` and show status changes.
- In the side-effect notebook, first call tools directly to expose the danger, then route
  through policy in the next lesson.
- Add a runnable LangGraph interrupt/resume notebook section or clearly mark it instructor-only.
- Separate local event fields, trace concepts, safety evaluation, and hosted LangSmith into
  digestible stages.
- Make the final project combine model-proposed structured actions with the policy runtime;
  currently the notebook constructs `ActionRequest` directly.

All nine Day 3 notebooks require revision; Notebooks 1, 2, 4, 7, 8, and 9 require major
expansion rather than editorial polishing.

### Day 4 — Workflow → Multi-Agent → Evaluation

Overall: **major implementation and teaching expansion required**.

Strengths:

- Seeded artifact and golden defects make comparison measurable.
- Deterministic checks correctly precede additional model roles.
- Findings have a shared structured contract.
- Fan-out/fan-in is bounded and supervisor work is narrow.
- The single reviewer is explicitly allowed to win.

Required improvements:

- Resolve P0.1 by adding the required live/model-mock reviewer adapter.
- Hide the golden answer key until after the student's first review; the current notebook
  reveals it in the same linear execution path.
- Add an editable student finding table before revealing expected IDs.
- Teach recall and false positives with a hand calculation before using `evaluate()`.
- Introduce concurrency only after running the same three specialists sequentially.
- Show one malformed or unsupported finding rejected at the handoff boundary.
- Demonstrate a duplicate with different wording so supervisor limitations are visible.
- Include at least one repeated live-model trial and variance discussion.
- Link D12–D15.

All seven notebooks need revision. Notebooks 2, 4, 6, and 7 are release blockers until
the actual model-driven comparison exists.

### Day 5 — Reusable AI Harness and MCP

Overall: **major implementation and teaching expansion required**.

Strengths:

- The module boundaries are sensible and deliberately small.
- Two configurations use one runtime.
- Tool schemas and risk levels are centralized.
- Policy, checkpoints, events, and step limits are application-owned.
- The fake MCP path gives deterministic outage coverage.

Required improvements:

- Resolve P0.2 and P0.3.
- Begin by showing duplicated snippets from Days 1 and 3 and ask students to identify
  repetition before naming the harness modules.
- Build the registry with one tool in the notebook before importing `build_demo_registry()`.
- Show a denied destructive action in the notebook, not only approval and limits.
- Explain why rejection should probably be `cancelled`, not `failed`, and improve the schema.
- Persist a checkpoint to SQLite or JSON and prove it survives a new runtime instance;
  the current in-memory store does not demonstrate restart recovery.
- Show event schema invariants and redaction rules.
- Register the real discovered MCP tool through local schema/risk/policy before calling it.
- Add D16–D18 links.
- End with a side-by-side definition exercise: agent, workflow, framework, protocol,
  runtime, harness.

All seven notebooks need revision. Notebooks 2, 5, 6, and 7 require major work.

## Proposed remediation order

1. Implement Day 5 OpenRouter provider adapter because it can be reused by Day 4.
2. Implement Day 4 structured live/model-mock reviewer roles and comparative telemetry.
3. Validate and integrate the real MCP stdio path through the harness policy layer.
4. Expand Day 3 notebooks and integrate model-proposed actions.
5. Expand Day 4 and Day 5 theory, build steps, expected observations, and exercises.
6. Enrich Day 2 explanations and exercises.
7. Polish Day 1 consistency, expected outputs, recaps, and diagram references.
8. Add robust path setup and notebook execution automation across all days.
9. Run a clean-machine offline execution, then live OpenRouter/hosted smoke tests.
10. Conduct the beginner pilot and shorten only after observing actual learner friction.

## Definition of classroom-ready

A notebook is classroom-ready when a fresh student kernel can run the required path;
the student knows what to observe; one limitation is deliberately reproduced; the next
layer visibly fixes that limitation; optional services have a working fallback; and the
student completes a bounded code change with an objective success condition.

Passing syntax checks alone does not satisfy this definition.
