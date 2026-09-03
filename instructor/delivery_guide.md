# Instructor Delivery Guide

This guide is for classroom delivery of the five-day course. It complements the
student notebooks; it is not a script that must be read verbatim.

## Before the course

1. Review `syllabus/locked_decisions.md` and do not add framework breadth during delivery.
2. Run `py validate_course.py` in a clean environment.
3. Test OpenRouter from the classroom network and prepare mock-mode instructions.
4. Issue individually named OpenRouter keys with the agreed lifetime budget and expiry.
5. Confirm students can open Jupyter, import the core packages, and access the repository.
6. Create optional Mem0 and LangSmith demonstrations using synthetic course identities.
7. Pin and test the MCP SDK with `day_05_ai_harness/instructor_mcp_server.py`.
8. Keep completed outputs or screenshots for API-dependent demonstrations.

Never troubleshoot one student's live API account in front of the whole class while
everyone waits. Move that student to mock mode, preserve the lesson flow, and return
to account setup during a break.

## Recurring teaching rhythm

Every notebook should follow this verbal rhythm:

1. **Build:** run the smallest working version.
2. **Observe:** inspect messages, state, retrieved chunks, decisions, or events.
3. **Break:** trigger the supplied limitation deliberately.
4. **Improve:** add one layer that addresses that limitation.
5. **Explain:** ask a student to name what changed and what remains unsolved.

Do not begin with the final architecture vocabulary. Introduce a term after students
experience the problem it names.

## Day 1 — Model, tool, and bounded agent

Teaching outcome: students can distinguish model output, host-executed tools, and an
agent loop.

- Begin in mock mode, then make one OpenRouter call.
- Show the complete direct OpenAI alternative once; do not repeat it later.
- Inspect raw model responses before adding structured output.
- Emphasize that a tool call is a request, not execution.
- End by changing the maximum-step value and forcing termination.

Checkpoint question: “Which part actually executed the Python function?”

Likely misconception: the model directly accesses the internet or local files.

## Day 2 — Knowledge and state

Teaching outcome: students can trace document ingestion through retrieval to a cited
answer and evaluate retrieval separately from generation.

- Let keyword search fail before introducing embeddings.
- Display chunks and scores; do not hide them behind a chat interface.
- Make abstention a success case when evidence is absent.
- Run the golden set before changing retrieval parameters.
- Explain that RAG context is not permanent model learning or personal memory.

Checkpoint question: “Was the wrong answer caused by retrieval or generation?”

## Day 3 — Memory, safety, and approval

Teaching outcome: students can separate history, summary, persistent memory, policy,
and human approval.

- Use a deliberately tiny context budget.
- Demonstrate memory inspection, correction, and deletion before Mem0.
- Use fictional identities for Mem0 and LangSmith.
- Show that an injection-style prompt cannot change Python policy.
- Reject an approval first; approval is not the default classroom click.

Checkpoint question: “What data was saved, why, for whom, and how is it deleted?”

## Day 4 — Measured multi-agent comparison

Teaching outcome: students can justify or reject multi-agent decomposition using
evidence rather than novelty.

- Hide the golden defect file during the first independent review.
- Run the single-reviewer baseline before naming specialist roles.
- Add deterministic checks before additional model calls.
- Inspect structured handoffs and supervisor deduplication.
- Treat the deterministic 9/9 result as orchestration validation, not model evidence.
- If running OpenRouter A/B trials, preserve raw outputs and repeat the experiment.

Checkpoint question: “What quality gain paid for the additional calls and complexity?”

## Day 5 — Mini harness and MCP

Teaching outcome: students can identify reusable infrastructure and explain why tool
discovery is not authorization.

- Compare the earlier application-specific loops before showing the harness modules.
- Load two JSON agent configurations through the same runtime.
- Fail argument validation, deny a destructive tool, and hit a step limit.
- Pause and resume a simulated external action using the saved checkpoint.
- Run fake MCP discovery first, then the instructor stdio server.
- Classify the discovered MCP tool locally before allowing invocation.

Checkpoint question: “If an MCP server advertises a tool, what still must our harness decide?”

## Classroom fallback ladder

1. Retry one bounded hosted request.
2. Switch the affected notebook to its deterministic mock path.
3. Use saved instructor output for discussion of provider-specific fields.
4. Continue local tools, retrieval, SQLite, evaluation, and policy exercises.
5. Defer optional hosted UI exposure rather than sacrificing core concepts.

## End-of-course demonstration

Ask each student or team to demonstrate one project and explain:

- the model's role and the host application's role;
- where state, knowledge, and memory live;
- what tool action is permitted, paused, or denied;
- which events prove what happened;
- one measured result and one remaining limitation;
- what the Day 5 harness reuses without erasing application-specific policy.

No marks rubric is prescribed here; the emphasis is a working, explainable system.
