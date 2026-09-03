from pathlib import Path
import sys

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from safe_task_agent import ActionRequest, SafeTaskAgent, SQLiteMemoryStore, make_plan


def main() -> None:
    memories = SQLiteMemoryStore()
    memories.add("fictional_asha", "Prefer concise email drafts", "explicit_demo_input")
    print("MEMORY:", memories.search("fictional_asha", "email preference"))
    print("PLAN:", make_plan("send a project update"))

    agent = SafeTaskAgent()
    draft = agent.request(ActionRequest("create_draft", {
        "to": "mentor@example.test", "subject": "Project update", "body": "Synthetic progress update."}))
    print("DRAFT:", draft)
    pending = agent.request(ActionRequest("send_email", draft.output))
    print("PAUSED:", pending)
    print("RESUMED:", agent.resume(pending.action_id, approved=True))
    print("EVENTS:", [event.as_dict() for event in agent.recorder.events])


if __name__ == "__main__":
    main()
