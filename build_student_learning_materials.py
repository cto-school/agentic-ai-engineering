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
        "What deserves persistent memory": "03_custom_persistent_memory.ipynb",
        "Plans are proposals": "05_small_plans.ipynb",
        "Guardrails: the umbrella term": "07_permissions_and_approval.ipynb",
        "Human approval is a state transition": "07_permissions_and_approval.ipynb",
        "Idempotency": "07_permissions_and_approval.ipynb",
        "Direct and indirect prompt injection": "07_permissions_and_approval.ipynb",
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
        "title": "Pivotal Exercise - Complete the Manual Agent Loop",
        "why": "A tool-using agent is an application-controlled loop. The model proposes either a tool request or a final answer; Python validates, dispatches, records the observation, and decides whether another step is allowed.",
        "contract": "Implement `run_agent`. Reject unknown tools, append every tool result to `messages`, return final text, and raise `RuntimeError` when `max_steps` is exhausted.",
        "starter": '''def run_agent(model, tools, messages, max_steps=4):
    """Run a bounded observe-dispatch-append loop and return final text."""
    # TODO: repeat for at most max_steps
    # TODO: ask model(messages) for the next response
    # TODO: return response["text"] for type == "final"
    # TODO: validate and dispatch requests of type == "tool"
    # TODO: append {"role": "tool", "name": ..., "content": ...}
    raise NotImplementedError("Complete the agent loop")''',
        "check": '''calls = []
def add(a, b):
    calls.append((a, b)); return a + b

responses = iter([
    {"type": "tool", "name": "add", "arguments": {"a": 2, "b": 3}},
    {"type": "final", "text": "The result is 5."},
])
history = [{"role": "user", "content": "Add 2 and 3"}]
assert run_agent(lambda messages: next(responses), {"add": add}, history) == "The result is 5."
assert calls == [(2, 3)]
assert any(item.get("role") == "tool" for item in history)
print("PASS")''',
        "reflection": "Why must the application, rather than the model, own tool execution and termination? Add a test for an unknown tool and one for a model that never returns a final answer.",
    },
    {
        "day": "day_02_knowledge_and_state", "file": "09_exercise_rag_context.ipynb",
        "title": "Pivotal Exercise - Assemble RAG Context",
        "why": "Retrieval results are not automatically model context. The application must select, order, label, and limit evidence. That boundary affects grounding, citations, latency, and resistance to irrelevant text.",
        "contract": "Implement `build_context`. Preserve rank order, label each included chunk, stay within the character budget, and skip rather than truncate a chunk that does not fit.",
        "starter": '''def build_context(chunks, character_budget):
    # Each chunk has source, section, and text.
    # Format each block with a source/section label followed by its text.
    # TODO: assemble complete chunks within the budget
    raise NotImplementedError("Complete context assembly")''',
        "check": '''chunks = [
    {"source": "a.md", "section": "Safety", "text": "Wear eye protection."},
    {"source": "b.md", "section": "Power", "text": "Verify protective earth."},
    {"source": "c.md", "section": "Noise", "text": "This distractor should not fit."},
]
result = build_context(chunks, 90)
assert len(result) <= 90
assert "[a.md | Safety]" in result and "Wear eye protection." in result
assert "This distractor" not in result
print(result); print("PASS")''',
        "reflection": "What changes when top-k grows but the context budget does not? Add a test proving that no included chunk is cut mid-sentence.",
    },
    {
        "day": "day_03_memory_and_safety", "file": "10_exercise_history_compaction.ipynb",
        "title": "Pivotal Exercise - Compact Conversation History",
        "why": "Conversation history grows without bound unless the application manages it. Compaction trades verbatim detail for a smaller representation, so its preservation rules must be explicit and testable.",
        "contract": "Return a new list. Preserve short histories unchanged. For longer histories, create one system summary containing older user facts and tool outcomes, followed by the most recent messages.",
        "starter": '''def compact_history(messages, keep_recent=2):
    # TODO: avoid mutating messages
    # TODO: preserve short histories
    # TODO: summarize older user facts and tool outcomes
    raise NotImplementedError("Complete history compaction")''',
        "check": '''history = [
    {"role": "user", "content": "My preferred unit is millimetres."},
    {"role": "assistant", "content": "Noted."},
    {"role": "tool", "content": "calculation completed: 25 mm"},
    {"role": "user", "content": "Use that result in the report."},
]
compacted = compact_history(history, keep_recent=2)
assert len(history) == 4 and len(compacted) == 3
assert compacted[0]["role"] == "system" and "millimetres" in compacted[0]["content"]
assert compacted[-2:] == history[-2:]
print(compacted); print("PASS")''',
        "reflection": "Which details are unsafe to summarize away? Add a case with an unresolved approval request and decide whether it belongs in summary, state, or both.",
    },
    {
        "day": "day_03_memory_and_safety", "file": "11_exercise_action_policy.ipynb",
        "title": "Pivotal Exercise - Enforce Action Policy",
        "why": "A model proposal is not authorization. Policy evaluates a structured action against available capabilities and approval state before any side-effecting handler runs.",
        "contract": "Deny unknown tools. Permit read-only tools. Permit a side-effecting tool only when its exact `action_id` is approved. Return `(allowed, reason)`.",
        "starter": '''def evaluate_action(action, allowed_tools, approved_action_ids):
    # TODO: reject unknown tools before considering approval
    # TODO: allow read-only capabilities
    # TODO: require exact action-id approval for side effects
    raise NotImplementedError("Complete action policy")''',
        "check": '''allowed = {"search": {"side_effect": False}, "send_email": {"side_effect": True}}
assert evaluate_action({"action_id": "a1", "tool": "search"}, allowed, set())[0]
assert not evaluate_action({"action_id": "a2", "tool": "send_email"}, allowed, set())[0]
assert evaluate_action({"action_id": "a2", "tool": "send_email"}, allowed, {"a2"})[0]
assert not evaluate_action({"action_id": "a3", "tool": "delete_all"}, allowed, {"a3"})[0]
print("PASS")''',
        "reflection": "Why is approving the exact structured action safer than approving a sentence such as 'send it'? Add a test proving that approval for one action ID cannot authorize another.",
    },
    {
        "day": "day_04_multi_agent_systems", "file": "08_exercise_supervisor_merge.ipynb",
        "title": "Pivotal Exercise - Merge Specialist Findings",
        "why": "Specialists may overlap, disagree, or fail. Deterministic aggregation makes the supervisor boundary inspectable and avoids spending another model call on rules ordinary code can enforce.",
        "contract": "Ignore failed specialist results, keep the first copy of each finding ID, and sort successful findings by descending severity then ascending ID.",
        "starter": '''def merge_findings(results):
    # TODO: tolerate status == "error"
    # TODO: deduplicate by stable ID
    # TODO: sort by (-severity, id)
    raise NotImplementedError("Complete supervisor merge")''',
        "check": '''results = [
    {"status": "ok", "findings": [{"id": "F2", "severity": 2}, {"id": "F1", "severity": 3}]},
    {"status": "error", "error": "timeout"},
    {"status": "ok", "findings": [{"id": "F1", "severity": 3}, {"id": "F3", "severity": 1}]},
]
merged = merge_findings(results)
assert [item["id"] for item in merged] == ["F1", "F2", "F3"]
print(merged); print("PASS")''',
        "reflection": "Why can ID-based deduplication still miss semantic duplicates? Add a second deterministic key using category and line number, then describe its possible false merges.",
    },
    {
        "day": "day_05_ai_harness", "file": "08_exercise_tool_registry.ipynb",
        "title": "Pivotal Exercise - Build a Capability-Aware Tool Registry",
        "why": "A harness needs one controlled place for tool discovery and dispatch. The registry connects model-visible schemas to host-owned handlers while policy limits which capabilities a configuration receives.",
        "contract": "Reject duplicate registrations. Show schemas only for granted capabilities. Reject unknown or ungranted dispatches before calling the handler.",
        "starter": '''class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name, schema, handler, capability):
        raise NotImplementedError("Complete registration")

    def schemas_for(self, granted_capabilities):
        raise NotImplementedError("Complete filtered discovery")

    def dispatch(self, name, arguments, granted_capabilities):
        raise NotImplementedError("Complete protected dispatch")''',
        "check": '''registry = ToolRegistry()
registry.register("add", {"name": "add", "parameters": {"a": "number", "b": "number"}},
                  lambda a, b: a + b, "math.read")
assert len(registry.schemas_for({"math.read"})) == 1
assert registry.schemas_for(set()) == []
assert registry.dispatch("add", {"a": 4, "b": 5}, {"math.read"}) == 9
try:
    registry.dispatch("add", {"a": 1, "b": 1}, set())
except PermissionError:
    pass
else:
    raise AssertionError("An ungranted tool must not run")
print("PASS")''',
        "reflection": "Why must filtered schemas and protected dispatch both exist? Add tests for duplicate registration and an unknown tool name.",
    },
]


def build_exercises() -> int:
    for item in EXERCISES:
        cells = [
            md(f"# {item['title']}\n\nThis is an individual implementation lab. It uses no API key."),
            md(f"## Why this mechanism matters\n\n{item['why']}"),
            md(f"## Contract\n\n{item['contract']}\n\nBefore coding, write one sentence predicting the easiest failure to make."),
            code(item["starter"]),
            md("## Behavioural check\n\nRun this only after completing the starter cell. A passing check proves the listed contract examples, not every possible input."),
            code(item["check"]),
            md(f"## Explain and extend\n\n{item['reflection']}"),
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
