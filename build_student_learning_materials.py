"""Embed theory in teaching notebooks and build the six pivotal exercise notebooks.

Run this after the day-specific notebook generators. It is idempotent.
The day-level theory Markdown files are authoring sources, not student prerequisites.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
THEORY_TAG = "embedded-course-theory"
LIVE_TAG = "required-live-observation"


THEORY_MAP = {
    "day_01_model_tools_agent": {
        "Why this day exists": "01_first_model_call.ipynb",
        "What a model call actually contains": "01_first_model_call.ipynb",
        "Why structured output matters": "03_structured_outputs.ipynb",
        "Why the application owns termination": "05_manual_agent_loop.ipynb",
        "Error compounding": "05_manual_agent_loop.ipynb",
        "Workflow or agent?": "06_langgraph_agent.ipynb",
        "What to carry into Day 2": "07_project_research_assistant.ipynb",
    },
    "day_02_knowledge_and_state": {
        "Why retrieval is an application problem": "01_documents_and_chunks.ipynb",
        "Why documents become chunks": "01_documents_and_chunks.ipynb",
        "Establish a lexical baseline first": "02_keyword_search.ipynb",
        "What embeddings do - and do not do": "03_embeddings_and_semantic_search.ipynb",
        "Context engineering": "04_basic_rag.ipynb",
        "Diagnosing a bad answer": "06_retrieval_evaluation.ipynb",
        "Citations and abstention": "05_citations_and_abstention.ipynb",
        "Indirect prompt injection begins here": "07_retrieval_tool_and_state.ipynb",
        "What to carry into Day 3": "08_project_knowledge_assistant.ipynb",
    },
    "day_03_memory_and_safety": {
        "Three different places information can live": "01_conversation_history.ipynb",
        "Context budgets and compaction": "02_context_compaction.ipynb",
        "What deserves persistent memory": "03_custom_persistent_memory.ipynb",
        "Managed memory products": "04_mem0_platform.ipynb",
        "Plans are proposals": "05_small_plans.ipynb",
        "Tools that change the world": "06_tools_with_side_effects.ipynb",
        "Guardrails: the umbrella term": "07_permissions_and_approval.ipynb",
        "Human approval is a state transition": "07_permissions_and_approval.ipynb",
        "Idempotency": "08_observability_and_safety_evaluation.ipynb",
        "Direct and indirect prompt injection": "08_observability_and_safety_evaluation.ipynb",
        "Observability and evaluation": "08_observability_and_safety_evaluation.ipynb",
        "What to carry into Day 4": "09_project_safe_task_agent.ipynb",
    },
    "day_04_multi_agent_systems": {
        "Why multiple agents are not the starting point": "01_seeded_artifact_and_golden_set.ipynb",
        "Deterministic tools before more model calls": "03_deterministic_checks.ipynb",
        "Specialist decomposition": "04_parallel_specialist_reviewers.ipynb",
        "Sequential before parallel": "04_parallel_specialist_reviewers.ipynb",
        "Deduplication is harder than matching IDs": "05_supervisor_synthesis.ipynb",
        "Evaluating nondeterministic systems": "06_comparative_evaluation.ipynb",
        "Capability can change the architecture conclusion": "06_comparative_evaluation.ipynb",
        "Cost and latency arithmetic": "06_comparative_evaluation.ipynb",
        "What to carry into Day 5": "07_project_engineering_review_team.ipynb",
    },
    "day_05_ai_harness": {
        "Why consolidate the earlier projects": "01_what_is_a_harness.ipynb",
        "Configuration versus runtime": "02_model_configuration_and_runtime.ipynb",
        "Registry, validation and policy": "03_tool_registry.ipynb",
        "Permissions, approval and limits": "04_permissions_and_limits.ipynb",
        "Events and checkpoints": "05_events_logs_and_checkpoints.ipynb",
        "Retries, timeouts and retry budgets": "05_events_logs_and_checkpoints.ipynb",
        "Cost attribution": "05_events_logs_and_checkpoints.ipynb",
        "MCP: protocol, not permission": "06_mcp_client.ipynb",
        "Mapping the course to production systems": "07_project_mini_harness.ipynb",
        "What the mini harness does not provide": "07_project_mini_harness.ipynb",
        "Automation is a trigger, not intelligence": "09_project_website_maintenance_agent.ipynb",
    },
}


def split_theory(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^## (.+)$", text, flags=re.MULTILINE))
    result = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        title = match.group(1).strip()
        result[title] = text[match.start():end].strip()
    return result


def embed_theory() -> int:
    changed = 0
    for day, mapping in THEORY_MAP.items():
        sections = split_theory(ROOT / day / "theory.md")
        grouped: dict[str, list[str]] = {}
        for title, notebook in mapping.items():
            if title not in sections:
                raise KeyError(f"Missing theory section {title!r} in {day}")
            grouped.setdefault(notebook, []).append(sections[title])
        for notebook, blocks in grouped.items():
            path = ROOT / day / "notebooks" / notebook
            nb = json.loads(path.read_text(encoding="utf-8"))
            cells = [c for c in nb["cells"] if THEORY_TAG not in c.get("metadata", {}).get("tags", [])]
            theory_cell = {
                "cell_type": "markdown",
                "metadata": {"tags": [THEORY_TAG]},
                "source": ("## Concept briefing\n\n" + "\n\n".join(blocks) + "\n").splitlines(True),
            }
            insert_at = 2 if len(cells) > 1 else 1
            nb["cells"] = [*cells[:insert_at], theory_cell, *cells[insert_at:]]
            path.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
            changed += 1
    return changed


LIVE_OBSERVATIONS = {
    "day_01_model_tools_agent/notebooks/01_first_model_call.ipynb":
        "Send one bounded prompt through the issued OpenRouter route and save the response plus usage record. If service access fails, inspect the instructor-captured trace and continue in mock mode.",
    "day_02_knowledge_and_state/notebooks/04_basic_rag.ipynb":
        "Generate one grounded answer with the live model using supplied evidence, then compare it with the deterministic fallback. Do not use live availability as a grading condition.",
    "day_03_memory_and_safety/notebooks/09_project_safe_task_agent.ipynb":
        "Let the live model propose one synthetic action. The same Python guardrails and approval boundary must control it. Use the captured proposal trace if the provider is unavailable.",
    "day_04_multi_agent_systems/notebooks/06_comparative_evaluation.ipynb":
        "Run one single-reviewer and one bounded specialist comparison with the issued model. Preserve raw structured results; use the captured comparison if the service is unavailable.",
    "day_05_ai_harness/notebooks/09_project_website_maintenance_agent.ipynb":
        "Choose one bounded live observation: fetch up to three public releases or obtain one OpenRouter update proposal. Stop before approval. The cached source and captured trace are the outage fallback.",
}


def embed_live_observations() -> int:
    for relative, text in LIVE_OBSERVATIONS.items():
        path = ROOT / relative
        nb = json.loads(path.read_text(encoding="utf-8"))
        cells = [c for c in nb["cells"] if LIVE_TAG not in c.get("metadata", {}).get("tags", [])]
        live_cell = {
            "cell_type": "markdown", "metadata": {"tags": [LIVE_TAG]},
            "source": ("## Required live observation\n\n" + text + "\n").splitlines(True),
        }
        nb["cells"] = [*cells[:-1], live_cell, cells[-1]] if len(cells) > 1 else [*cells, live_cell]
        path.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    return len(LIVE_OBSERVATIONS)


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip().splitlines(True)}


def code(text: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.strip().splitlines(True)}


EXERCISES = [
    {
        "day": "day_01_model_tools_agent", "file": "08_exercise_manual_agent_loop.ipynb",
        "title": "Day 1.8 — Pivotal Exercise: Complete the Manual Agent Loop",
        "why": "A tool-using agent is an application-controlled loop. The model proposes either a tool request or a final answer; Python validates, dispatches, records the observation, and decides whether another step is allowed. Day 1.5 built this loop with you; here you write it alone.",
        "contract": "Implement `run_agent`. Reject unknown tools with `ValueError`, append every tool result to `messages` as `{\"role\": \"tool\", \"name\": ..., \"content\": ...}`, return the final text, and raise `RuntimeError` when `max_steps` is exhausted.",
        "starter": '''def run_agent(model, tools, messages, max_steps=4):
    """Run a bounded observe-dispatch-append loop and return final text.

    model(messages) returns either
        {"type": "final", "text": "..."}                       -> return the text
        {"type": "tool", "name": "...", "arguments": {...}}    -> run the tool, append, loop
    """
    # TODO: repeat for at most max_steps
    # TODO: ask model(messages) for the next response
    # TODO: return response["text"] when type == "final"
    # TODO: validate the tool name, run tools[name](**arguments)
    # TODO: append {"role": "tool", "name": ..., "content": ...} to messages
    # TODO: after the loop, raise RuntimeError("step limit reached")
    raise NotImplementedError("Complete the agent loop")''',
        "check": '''def run_checks():
    calls = []
    def add(a, b):
        calls.append((a, b))
        return a + b

    # Case 1: one tool request, then a final answer.
    responses = iter([
        {"type": "tool", "name": "add", "arguments": {"a": 2, "b": 3}},
        {"type": "final", "text": "The result is 5."},
    ])
    history = [{"role": "user", "content": "Add 2 and 3"}]
    assert run_agent(lambda messages: next(responses), {"add": add}, history) == "The result is 5."
    assert calls == [(2, 3)], "the tool must run exactly once with the model's arguments"
    assert any(item.get("role") == "tool" for item in history), "the tool result must be appended"

    # Case 2: an unknown tool must be rejected BEFORE anything runs.
    bad = iter([{"type": "tool", "name": "delete_everything", "arguments": {}}])
    try:
        run_agent(lambda messages: next(bad), {"add": add}, [{"role": "user", "content": "x"}])
    except ValueError:
        pass
    else:
        raise AssertionError("an unknown tool name must raise ValueError")

    # Case 3: a model that never answers must be stopped by the step limit.
    forever = lambda messages: {"type": "tool", "name": "add", "arguments": {"a": 1, "b": 1}}
    try:
        run_agent(forever, {"add": add}, [{"role": "user", "content": "x"}], max_steps=3)
    except RuntimeError:
        pass
    else:
        raise AssertionError("the loop must raise RuntimeError after max_steps")
    print("PASS: dispatch, unknown-tool rejection, and step limit all behave correctly")

try:
    run_checks()
except NotImplementedError:
    print("Not implemented yet. Complete the starter cell above, or study the reference solution below and re-run this cell.")''',
        "solution": '''# --- Reference solution: read it line by line, then re-run the check cell above ---
def run_agent(model, tools, messages, max_steps=4):
    """Run a bounded observe-dispatch-append loop and return final text."""
    for step in range(1, max_steps + 1):                 # bounded: the loop can never run forever
        response = model(messages)                        # 1. ask the model what to do next
        if response["type"] == "final":                   # 2a. it answered -> we are done
            return response["text"]
        if response["type"] != "tool":                    # anything else is a protocol error
            raise ValueError(f"Unexpected response type: {response['type']!r}")
        name = response["name"]
        if name not in tools:                             # 2b. validate BEFORE executing anything
            raise ValueError(f"Unknown tool requested: {name!r}")
        result = tools[name](**response["arguments"])     # 3. the HOST runs the function, not the model
        messages.append({"role": "tool", "name": name, "content": str(result)})  # 4. record the observation
        print(f"step {step}: ran {name}{response['arguments']} -> {result}")
    raise RuntimeError(f"Stopped after {max_steps} steps without a final answer")  # 5. safe termination

print("Reference run_agent defined. Re-run the check cell above to see PASS.")''',
        "explain": [
            ("Why must the application, rather than the model, own tool execution and termination?",
             "The model only emits text that <em>looks like</em> a request. Only the host can check the tool exists, validate the arguments, decide whether it is allowed, actually run it, and count steps. If the model owned termination, a confused or malicious prompt could loop forever or call anything."),
            ("Why is the unknown-tool check placed before <code>tools[name](...)</code> and not after?",
             "Once a function has run, its side effects have happened. Validation must come first so a bad request is rejected with zero effects."),
        ],
    },
    {
        "day": "day_02_knowledge_and_state", "file": "09_exercise_rag_context.ipynb",
        "title": "Day 2.9 — Pivotal Exercise: Assemble RAG Context",
        "why": "Retrieval results are not automatically model context. The application must select, order, label, and limit evidence. That boundary affects grounding, citations, latency, and resistance to irrelevant text.",
        "contract": "Implement `build_context`. Preserve rank order, label each included chunk as `[source | section]`, stay within the character budget, and skip rather than truncate a chunk that does not fit.",
        "starter": '''def build_context(chunks, character_budget):
    """Return one string of labelled evidence blocks that fits the budget.

    Each chunk is {"source": str, "section": str, "text": str}.
    Block format:  [source | section]\\ntext      Blocks are separated by a blank line.
    """
    # TODO: walk the chunks in the given (ranked) order
    # TODO: build the labelled block for each chunk
    # TODO: include the block only if the whole block still fits the budget
    # TODO: join the included blocks with "\\n\\n"
    raise NotImplementedError("Complete context assembly")''',
        "check": '''def run_checks():
    chunks = [
        {"source": "a.md", "section": "Safety", "text": "Wear eye protection."},
        {"source": "b.md", "section": "Power", "text": "Verify protective earth."},
        {"source": "c.md", "section": "Noise", "text": "This distractor should not fit."},
    ]
    result = build_context(chunks, 90)
    print("Assembled context (", len(result), "characters ):")
    print(result)
    assert len(result) <= 90, "the budget is a hard limit"
    assert "[a.md | Safety]" in result and "Wear eye protection." in result
    assert "[b.md | Power]" in result and "Verify protective earth." in result
    assert result.index("[a.md") < result.index("[b.md"), "rank order must be preserved"
    assert "This distractor" not in result, "a chunk that does not fit is skipped, never cut"
    assert "[c.md" not in result, "a skipped chunk must not leave a dangling label"
    print("PASS: context is labelled, ordered, bounded, and never truncated")

try:
    run_checks()
except NotImplementedError:
    print("Not implemented yet. Complete the starter cell above, or study the reference solution below and re-run this cell.")''',
        "solution": '''# --- Reference solution: read it line by line, then re-run the check cell above ---
def build_context(chunks, character_budget):
    blocks = []                                   # the blocks we decided to include
    used = 0                                      # characters spent so far
    for chunk in chunks:                          # ranked order in, ranked order out
        block = f"[{chunk['source']} | {chunk['section']}]\\n{chunk['text']}"
        separator = 2 if blocks else 0            # "\\n\\n" costs 2 characters between blocks
        if used + separator + len(block) > character_budget:
            print(f"skip  {chunk['source']}: {len(block)} chars would exceed the budget")
            continue                              # skip the WHOLE chunk; never cut it in half
        blocks.append(block)
        used += separator + len(block)
        print(f"keep  {chunk['source']}: {used}/{character_budget} chars used")
    return "\\n\\n".join(blocks)

print("Reference build_context defined. Re-run the check cell above to see PASS.")''',
        "explain": [
            ("What changes when top-k grows but the context budget does not?",
             "More candidates compete for the same space. Lower-ranked chunks are skipped, so a larger top-k only helps if the ranking is good; if it is poor, a relevant chunk ranked 6th is still lost. This is why Day 2.6 measures retrieval separately."),
            ("Why is skipping a chunk better than truncating it?",
             "A half chunk can end mid-sentence and change meaning, and its citation label would point at text the model never saw. Complete blocks keep every citation verifiable."),
        ],
    },
    {
        "day": "day_03_memory_and_safety", "file": "10_exercise_history_compaction.ipynb",
        "title": "Day 3.10 — Pivotal Exercise: Compact Conversation History",
        "why": "Conversation history grows without bound unless the application manages it. Compaction trades verbatim detail for a smaller representation, so its preservation rules must be explicit and testable.",
        "contract": "Return a new list without modifying the input. Preserve short histories unchanged. For longer histories, create one system summary containing older user facts and tool outcomes, followed by the most recent `keep_recent` messages.",
        "starter": '''def compact_history(messages, keep_recent=2):
    """Return a compacted copy of messages.

    Short history (len <= keep_recent + 1): return an unchanged copy.
    Longer history: [ {"role": "system", "content": summary}, *last keep_recent messages ]
    The summary must mention older user facts and tool outcomes; assistant small talk may be dropped.
    """
    # TODO: never mutate the input list
    # TODO: return a copy when the history is already short
    # TODO: summarize older user and tool messages into one system message
    # TODO: keep the most recent messages verbatim
    raise NotImplementedError("Complete history compaction")''',
        "check": '''def run_checks():
    history = [
        {"role": "user", "content": "My preferred unit is millimetres."},
        {"role": "assistant", "content": "Noted."},
        {"role": "tool", "content": "calculation completed: 25 mm"},
        {"role": "user", "content": "Use that result in the report."},
    ]
    compacted = compact_history(history, keep_recent=2)
    print("Before:", len(history), "messages   After:", len(compacted), "messages")
    for message in compacted:
        print(f"  {message['role']:>9}: {message['content']}")
    assert len(history) == 4 and history[0]["content"].startswith("My preferred"), "input must not be mutated"
    assert len(compacted) == 3
    assert compacted[0]["role"] == "system" and "millimetres" in compacted[0]["content"], "older user facts survive in the summary"
    assert compacted[-2:] == history[-2:], "recent messages stay verbatim"

    short = history[:2]
    kept = compact_history(short, keep_recent=2)
    assert kept == short and kept is not short, "short histories are returned as an unchanged copy"
    print("PASS: history is bounded, essential information is retained, input is untouched")

try:
    run_checks()
except NotImplementedError:
    print("Not implemented yet. Complete the starter cell above, or study the reference solution below and re-run this cell.")''',
        "solution": '''# --- Reference solution: read it line by line, then re-run the check cell above ---
def compact_history(messages, keep_recent=2):
    if len(messages) <= keep_recent + 1:          # nothing worth compacting
        return list(messages)                      # a copy, so the caller's list is untouched
    older, recent = messages[:-keep_recent], messages[-keep_recent:]
    facts = []
    for message in older:                          # decide what deserves to survive
        if message["role"] == "user":
            facts.append(f"user said: {message['content']}")
        elif message["role"] == "tool":
            facts.append(f"tool result: {message['content']}")
        # assistant acknowledgements such as "Noted." carry no facts and are dropped
    summary = {"role": "system", "content": "Summary of earlier conversation: " + " | ".join(facts)}
    return [summary, *recent]                      # one summary + the verbatim recent tail

print("Reference compact_history defined. Re-run the check cell above to see PASS.")''',
        "explain": [
            ("Which details are unsafe to summarize away?",
             "Anything that still governs future behaviour: an unresolved approval request, an exact constraint (a deadline, a unit, a budget), a safety instruction, or a pending action id. Those belong in explicit application state, not only in a lossy summary."),
            ("Where should an unresolved approval request live: summary, state, or both?",
             "State, always: the approval boundary in Day 3.7 must be able to find the exact proposed action. The summary may mention it for the model's benefit, but the application must not rely on the summary to enforce it."),
        ],
    },
    {
        "day": "day_03_memory_and_safety", "file": "11_exercise_action_policy.ipynb",
        "title": "Day 3.11 — Pivotal Exercise: Enforce Action Policy",
        "why": "A model proposal is not authorization. Policy evaluates a structured action against available capabilities and approval state before any side-effecting handler runs.",
        "contract": "Deny unknown tools. Permit read-only tools. Permit a side-effecting tool only when its exact `action_id` is in `approved_action_ids`. Return `(allowed, reason)`.",
        "starter": '''def evaluate_action(action, allowed_tools, approved_action_ids):
    """Return (allowed: bool, reason: str).

    action        -> {"action_id": "a1", "tool": "search", ...}
    allowed_tools -> {"search": {"side_effect": False}, "send_email": {"side_effect": True}}
    """
    # TODO: reject unknown tools before considering approval
    # TODO: allow read-only tools
    # TODO: require the exact action_id to be approved for side effects
    raise NotImplementedError("Complete action policy")''',
        "check": '''def run_checks():
    allowed = {"search": {"side_effect": False}, "send_email": {"side_effect": True}}
    cases = [
        ({"action_id": "a1", "tool": "search"},     set(),  True,  "read-only tool runs without approval"),
        ({"action_id": "a2", "tool": "send_email"}, set(),  False, "side effect without approval is blocked"),
        ({"action_id": "a2", "tool": "send_email"}, {"a2"}, True,  "side effect with exact approval runs"),
        ({"action_id": "a2", "tool": "send_email"}, {"a9"}, False, "approval for a different action id does not transfer"),
        ({"action_id": "a3", "tool": "delete_all"}, {"a3"}, False, "unknown tool is denied even if 'approved'"),
    ]
    for action, approvals, expected, label in cases:
        allowed_flag, reason = evaluate_action(action, allowed, approvals)
        print(f"{'ALLOW' if allowed_flag else 'DENY ':5} {action['tool']:<10} approvals={sorted(approvals)!s:<8} -> {reason}")
        assert allowed_flag == expected, label
    print("PASS: capability and exact-action approval are enforced")

try:
    run_checks()
except NotImplementedError:
    print("Not implemented yet. Complete the starter cell above, or study the reference solution below and re-run this cell.")''',
        "solution": '''# --- Reference solution: read it line by line, then re-run the check cell above ---
def evaluate_action(action, allowed_tools, approved_action_ids):
    tool = action.get("tool")
    if tool not in allowed_tools:                              # 1. unknown capability -> fail closed
        return False, f"unknown tool {tool!r}"
    if not allowed_tools[tool]["side_effect"]:                 # 2. read-only -> no approval needed
        return True, "read-only tool"
    if action.get("action_id") in approved_action_ids:         # 3. side effect -> exact id must be approved
        return True, "side effect approved for this exact action id"
    return False, "side effect requires approval"              # 4. default: do not run

print("Reference evaluate_action defined. Re-run the check cell above to see PASS.")''',
        "explain": [
            ("Why is approving the exact structured action safer than approving a sentence such as 'send it'?",
             "'Send it' does not say what, to whom, or with which content. If the draft or recipients change after the sentence was spoken, the approval silently covers something the person never saw. An action id binds approval to one exact payload."),
            ("Why must the unknown-tool check come first?",
             "Otherwise an approval set containing a stray id could authorize a tool nobody declared. Capability is checked before approval so approval can never widen the capability list."),
        ],
    },
    {
        "day": "day_04_multi_agent_systems", "file": "08_exercise_supervisor_merge.ipynb",
        "title": "Day 4.8 — Pivotal Exercise: Merge Specialist Findings",
        "why": "Specialists may overlap, disagree, or fail. Deterministic aggregation makes the supervisor boundary inspectable and avoids spending another model call on rules ordinary code can enforce.",
        "contract": "Ignore results whose `status` is not `ok`, keep the first copy of each finding `id`, and sort the survivors by descending `severity` then ascending `id`.",
        "starter": '''def merge_findings(results):
    """Return one deduplicated, ranked list of findings.

    results -> [{"status": "ok", "findings": [{"id": "F1", "severity": 3}, ...]},
                {"status": "error", "error": "timeout"}, ...]
    """
    # TODO: skip results whose status is not "ok"
    # TODO: keep only the first finding seen for each id
    # TODO: sort by (-severity, id)
    raise NotImplementedError("Complete supervisor merge")''',
        "check": '''def run_checks():
    results = [
        {"status": "ok", "findings": [{"id": "F2", "severity": 2}, {"id": "F1", "severity": 3}]},
        {"status": "error", "error": "timeout"},
        {"status": "ok", "findings": [{"id": "F1", "severity": 3}, {"id": "F3", "severity": 1}]},
    ]
    merged = merge_findings(results)
    print("Merged:", [(item["id"], item["severity"]) for item in merged])
    assert [item["id"] for item in merged] == ["F1", "F2", "F3"], "dedupe by id, tolerate the failed specialist"

    # Severity must win over id order: Z1 (severity 4) comes before A9 (severity 1).
    tricky = [{"status": "ok", "findings": [{"id": "A9", "severity": 1}, {"id": "Z1", "severity": 4}]}]
    assert [item["id"] for item in merge_findings(tricky)] == ["Z1", "A9"], "sort by severity first, then id"
    print("PASS: merge is deterministic, deduplicated, ranked, and tolerant of partial failure")

try:
    run_checks()
except NotImplementedError:
    print("Not implemented yet. Complete the starter cell above, or study the reference solution below and re-run this cell.")''',
        "solution": '''# --- Reference solution: read it line by line, then re-run the check cell above ---
def merge_findings(results):
    first_seen = {}                                        # id -> finding (first copy wins)
    for result in results:
        if result.get("status") != "ok":                   # a failed specialist must not erase the others
            print("skipping failed specialist:", result.get("error"))
            continue
        for finding in result["findings"]:
            first_seen.setdefault(finding["id"], finding)  # setdefault keeps the first copy
    return sorted(first_seen.values(), key=lambda f: (-f["severity"], f["id"]))  # high severity first, then id

print("Reference merge_findings defined. Re-run the check cell above to see PASS.")''',
        "explain": [
            ("Why can id-based deduplication still miss semantic duplicates?",
             "Two specialists can describe the same defect with different ids or different wording. A stable key built from category and line number catches more, but it can also falsely merge two different problems on the same line. Day 4.5 shows why the supervisor keeps both evidence references."),
            ("Why sort by severity before id?",
             "The report is read top-down by a busy engineer. Ordering by id would bury a critical finding under cosmetic ones; the id is only a tiebreaker to keep the output deterministic."),
        ],
    },
    {
        "day": "day_05_ai_harness", "file": "08_exercise_tool_registry.ipynb",
        "title": "Day 5.8 — Pivotal Exercise: Build a Capability-Aware Tool Registry",
        "why": "A harness needs one controlled place for tool discovery and dispatch. The registry connects model-visible schemas to host-owned handlers while policy limits which capabilities a configuration receives.",
        "contract": "Reject duplicate registrations with `ValueError`. Show schemas only for granted capabilities. Raise `KeyError` for an unknown tool and `PermissionError` for an ungranted one before the handler is called.",
        "starter": '''class ToolRegistry:
    def __init__(self):
        self._tools = {}   # name -> {"schema": ..., "handler": ..., "capability": ...}

    def register(self, name, schema, handler, capability):
        """Register once; a second registration of the same name raises ValueError."""
        raise NotImplementedError("Complete registration")

    def schemas_for(self, granted_capabilities):
        """Return the schemas of tools whose capability is granted (least-privilege discovery)."""
        raise NotImplementedError("Complete filtered discovery")

    def dispatch(self, name, arguments, granted_capabilities):
        """Unknown name -> KeyError. Ungranted capability -> PermissionError. Otherwise call the handler."""
        raise NotImplementedError("Complete protected dispatch")''',
        "check": '''def run_checks():
    registry = ToolRegistry()
    registry.register("add", {"name": "add", "parameters": {"a": "number", "b": "number"}},
                      lambda a, b: a + b, "math.read")
    print("visible with math.read :", [s["name"] for s in registry.schemas_for({"math.read"})])
    print("visible with nothing   :", [s["name"] for s in registry.schemas_for(set())])
    assert len(registry.schemas_for({"math.read"})) == 1
    assert registry.schemas_for(set()) == []
    assert registry.dispatch("add", {"a": 4, "b": 5}, {"math.read"}) == 9

    for label, call, expected in [
        ("ungranted dispatch", lambda: registry.dispatch("add", {"a": 1, "b": 1}, set()), PermissionError),
        ("unknown tool", lambda: registry.dispatch("nope", {}, {"math.read"}), KeyError),
        ("duplicate registration", lambda: registry.register("add", {}, lambda: None, "math.read"), ValueError),
    ]:
        try:
            call()
        except expected as exc:
            print(f"{label:<23} -> {type(exc).__name__}: {exc}")
        else:
            raise AssertionError(f"{label} must raise {expected.__name__}")
    print("PASS: registry centralizes discovery, dispatch, and capability checks")

try:
    run_checks()
except NotImplementedError:
    print("Not implemented yet. Complete the starter cell above, or study the reference solution below and re-run this cell.")''',
        "solution": '''# --- Reference solution: read it line by line, then re-run the check cell above ---
class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name, schema, handler, capability):
        if name in self._tools:                                    # one name, one handler
            raise ValueError(f"tool {name!r} is already registered")
        self._tools[name] = {"schema": schema, "handler": handler, "capability": capability}

    def schemas_for(self, granted_capabilities):
        # Discovery is filtered so the model is never tempted by tools it may not use ...
        return [t["schema"] for t in self._tools.values() if t["capability"] in granted_capabilities]

    def dispatch(self, name, arguments, granted_capabilities):
        if name not in self._tools:                                # fail closed on unknown names
            raise KeyError(f"unknown tool {name!r}")
        tool = self._tools[name]
        if tool["capability"] not in granted_capabilities:         # ... and enforced AGAIN here
            raise PermissionError(f"capability {tool['capability']!r} not granted for {name!r}")
        return tool["handler"](**arguments)                        # only now does the host run it

print("Reference ToolRegistry defined. Re-run the check cell above to see PASS.")''',
        "explain": [
            ("Why must filtered schemas and protected dispatch both exist?",
             "Filtering schemas reduces temptation: the model never sees a tool it may not use. But a model can still name a hidden tool, and code paths other than the model can call dispatch. Only the check inside dispatch actually prevents execution."),
            ("Why raise an exception instead of returning None for an ungranted call?",
             "A silent None can be mistaken for a successful empty result. An exception stops the run, is recorded as an event, and forces the caller to handle the denial explicitly."),
        ],
    },
]


def build_exercises() -> int:
    for item in EXERCISES:
        explain_html = "\n\n".join(
            f"**{question}**\n\n<details><summary>Show answer</summary>\n\n{answer}\n\n</details>"
            for question, answer in item["explain"]
        )
        cells = [
            md(f"# {item['title']}\n\nThis is the day's one hands-on implementation lab. It uses no API key. "
               "Try the starter cell first; a fully commented reference solution follows the check so you can compare or catch up."),
            md(f"## Why this mechanism matters\n\n{item['why']}"),
            md(f"## Contract\n\n{item['contract']}\n\nBefore coding, write one sentence predicting the easiest mistake to make."),
            code(item["starter"]),
            md("## Behavioural check\n\nRun this after completing the starter cell. If you have not finished, it prints a hint instead of failing. "
               "A passing check proves the listed contract examples, not every possible input."),
            code(item["check"]),
            md("## Reference solution\n\nRead this even if your check passed: compare each commented line with your version, then re-run the check cell above."),
            code(item["solution"]),
            md(f"## Explain\n\n{explain_html}"),
        ]
        notebook = {
            "cells": cells,
            "metadata": {
                "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                "language_info": {"name": "python", "version": "3.11"},
            },
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        path = ROOT / item["day"] / "notebooks" / item["file"]
        path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
    return len(EXERCISES)

if __name__ == "__main__":
    print(f"Embedded theory into {embed_theory()} notebooks")
    print(f"Embedded {embed_live_observations()} required live-observation cells")
    print(f"Built {build_exercises()} exercise notebooks")
    from build_master_notebooks import main as build_master_notebooks
    build_master_notebooks()
