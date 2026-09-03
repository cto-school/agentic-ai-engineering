from __future__ import annotations

from uuid import uuid4

from .events import EventRecorder
from .schemas import ActionRequest, ActionResult
from .tools import POLICY, SimulatedWorkspace, tool_registry
from .proposal import ActionProposer


class SafeTaskAgent:
    def __init__(self, workspace: SimulatedWorkspace | None = None,
                 recorder: EventRecorder | None = None):
        self.workspace = workspace or SimulatedWorkspace()
        self.recorder = recorder or EventRecorder()
        self.tools = tool_registry(self.workspace)
        self.pending: dict[str, ActionRequest] = {}

    def handle_prompt(self, prompt: str, proposer: ActionProposer) -> ActionResult:
        visible=[{"name":name,"decision":decision} for name,decision in POLICY.items()]
        self.recorder.record("model_requested",prompt=prompt,visible_tools=[x["name"] for x in visible])
        try: proposal=proposer.propose(prompt,visible)
        except Exception as exc:
            self.recorder.record("model_error",error=str(exc))
            return ActionResult("error",str(exc))
        self.recorder.record("model_completed",kind=proposal.kind,usage=proposal.usage)
        if proposal.kind=="final" or not proposal.action:
            return ActionResult("completed",proposal.message)
        return self.request(proposal.action)

    def request(self, action: ActionRequest) -> ActionResult:
        self.recorder.record("action_requested", tool=action.tool, arguments=action.arguments)
        decision = POLICY.get(action.tool, "deny")
        self.recorder.record("policy_decision", tool=action.tool, decision=decision)
        if decision == "deny":
            return ActionResult("denied", f"Policy denied {action.tool}.")
        if decision == "approval":
            action_id = str(uuid4())
            self.pending[action_id] = action
            self.recorder.record("approval_requested", action_id=action_id, tool=action.tool)
            return ActionResult("pending_approval", "No action was executed. Approval is required.", action_id)
        return self._execute(action)

    def resume(self, action_id: str, approved: bool) -> ActionResult:
        action = self.pending.pop(action_id, None)
        if not action:
            return ActionResult("error", "Unknown or already resolved action.", action_id)
        self.recorder.record("approval_resolved", action_id=action_id, approved=approved)
        if not approved:
            return ActionResult("rejected", "User rejected the action; nothing was executed.", action_id)
        # Re-check policy on resume: policy may have changed while paused.
        if POLICY.get(action.tool, "deny") == "deny":
            return ActionResult("denied", "Current policy denies this action.", action_id)
        return self._execute(action, action_id)

    def _execute(self, action: ActionRequest, action_id: str | None = None) -> ActionResult:
        try:
            output = self.tools[action.tool](**action.arguments)
            self.recorder.record("tool_completed", tool=action.tool, action_id=action_id)
            return ActionResult("completed", f"Completed {action.tool}.", action_id, output)
        except (KeyError, TypeError) as exc:
            self.recorder.record("tool_error", tool=action.tool, error=str(exc))
            return ActionResult("error", str(exc), action_id)
