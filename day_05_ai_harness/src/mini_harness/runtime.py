"""The runtime: one loop that every agent configuration shares."""
from __future__ import annotations
import json
import time
from uuid import uuid4
from .events import CheckpointStore, EventStore
from .policy import decide
from .providers import ModelProvider
from .registry import ToolRegistry
from .schemas import AgentConfig, RunResult

# --- Execution limits ---------------------------------------------------------
# A configuration may ask for any number of steps, but the harness owns the last
# word. This constant is the hard ceiling; the effective limit is the smaller of
# the two and is what every event and message reports.
MAX_STEPS_HARD_CAP = 10

# --- Retry budget -------------------------------------------------------------
# Network calls fail. We retry a *bounded* number of times with exponential
# backoff, and we record every attempt. The delays are deliberately tiny so a
# classroom demonstration stays fast.
MAX_PROVIDER_RETRIES = 2
RETRY_BASE_DELAY_SECONDS = 0.05

# Errors that will not improve on repetition: bad arguments, missing keys,
# misconfiguration. Retrying these only wastes time and credit.
NON_RETRYABLE_ERRORS = (ValueError, TypeError, KeyError)


def effective_step_limit(config: AgentConfig) -> int:
    """The number of steps this run may actually take."""
    return min(config.max_steps, MAX_STEPS_HARD_CAP)


class HarnessRuntime:
    def __init__(self, registry: ToolRegistry, provider: ModelProvider, events=None, checkpoints=None):
        self.registry = registry
        self.provider = provider
        self.events = events or EventStore()
        self.checkpoints = checkpoints or CheckpointStore()

    # -- provider call with a bounded retry budget -----------------------------
    def _decide_with_retries(self, run_id, step, prompt, config, tools, history):
        """Call the provider, retrying transient failures with exponential backoff."""
        attempt = 0
        while True:
            attempt += 1
            try:
                return self.provider.decide(prompt, config, tools, history)
            except NON_RETRYABLE_ERRORS as exc:
                # Fail immediately: a schema or configuration error is not transient.
                self.events.add(run_id, "provider_error_not_retried", step=step,
                                error=f"{type(exc).__name__}: {exc}")
                raise
            except Exception as exc:
                if attempt > MAX_PROVIDER_RETRIES:
                    self.events.add(run_id, "provider_retry_budget_exhausted", step=step,
                                    attempts=attempt, error=str(exc))
                    raise
                delay = RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1))  # 0.05s, 0.10s, ...
                self.events.add(run_id, "provider_retry", step=step, attempt=attempt,
                                error=str(exc), retry_in_seconds=round(delay, 3),
                                retries_left=MAX_PROVIDER_RETRIES - attempt + 1)
                time.sleep(delay)

    def run(self, config: AgentConfig, prompt: str, run_id: str | None = None) -> RunResult:
        run_id = run_id or str(uuid4())
        history: list[dict] = []
        limit = effective_step_limit(config)
        self.events.add(run_id, "run_started", agent=config.name, model=config.model.model,
                        requested_max_steps=config.max_steps, hard_cap=MAX_STEPS_HARD_CAP,
                        effective_step_limit=limit)
        for step in range(1, limit + 1):
            tools = self.registry.discover(config.allowed_tools)
            self.events.add(run_id, "model_requested", step=step, visible_tools=[t.name for t in tools])
            try:
                choice = self._decide_with_retries(run_id, step, prompt, config, tools, history)
            except Exception as exc:
                return self._failed(run_id, f"Model error: {exc}")
            self.events.add(run_id, "model_completed", step=step, usage=choice.usage)
            if choice.kind == "final":
                self.events.add(run_id, "run_completed", step=step)
                return RunResult(run_id, "completed", choice.content, events=self.events.get(run_id))
            try:
                registered = self.registry.get(choice.tool or "")
            except KeyError as exc:
                return self._failed(run_id, str(exc))
            try:
                self.registry.validate(registered.spec.name, choice.arguments)
            except (ValueError, TypeError) as exc:
                return self._failed(run_id, str(exc))
            policy = decide(config, registered.spec)
            self.events.add(run_id, "policy_decision", tool=registered.spec.name,
                            risk=registered.spec.risk, decision=policy)
            call_id = choice.call_id or f"local-call-{step}"
            history.append({"role": "assistant", "content": "",
                            "tool_calls": [{"id": call_id, "type": "function",
                                            "function": {"name": registered.spec.name,
                                                         "arguments": json.dumps(choice.arguments)}}],
                            "reasoning_details": choice.reasoning_details})
            if policy == "deny":
                return self._failed(run_id, f"Denied tool: {registered.spec.name}")
            if policy == "approval":
                pending = {"tool": registered.spec.name, "arguments": choice.arguments,
                           "history": history, "prompt": prompt, "agent": config.name,
                           "steps_used": step}
                self.checkpoints.save(run_id, pending)
                self.events.add(run_id, "approval_requested", **pending)
                return RunResult(run_id, "pending_approval", pending_action=pending,
                                 events=self.events.get(run_id))
            try:
                output = self.registry.call(registered.spec.name, choice.arguments)
            except Exception as exc:
                # A tool raising (for example a domain guardrail refusing) ends the
                # run with a recorded reason rather than an uncaught traceback.
                self.events.add(run_id, "tool_failed", tool=registered.spec.name, error=str(exc))
                return self._failed(run_id, f"Tool {registered.spec.name} refused: {exc}")
            history.append({"role": "tool", "name": registered.spec.name,
                            "tool_call_id": call_id, "content": str(output)})
            self.events.add(run_id, "tool_completed", tool=registered.spec.name)
        self.events.add(run_id, "step_limit_reached", limit=limit,
                        requested_max_steps=config.max_steps, hard_cap=MAX_STEPS_HARD_CAP)
        return RunResult(run_id, "step_limit", f"Maximum steps reached (effective limit {limit}).",
                         events=self.events.get(run_id))

    def resume(self, run_id: str, config: AgentConfig, approved: bool) -> RunResult:
        state = self.checkpoints.load(run_id)
        if not state:
            return self._failed(run_id, "Checkpoint not found")
        self.events.add(run_id, "approval_resolved", approved=approved)
        self.checkpoints.delete(run_id)
        if not approved:
            self.events.add(run_id, "run_cancelled", reason="User rejected action")
            return RunResult(run_id, "cancelled", "User rejected action", events=self.events.get(run_id))
        tool = self.registry.get(state["tool"])
        if decide(config, tool.spec) != "approval":
            return self._failed(run_id, "Policy changed while paused")
        try:
            output = self.registry.call(tool.spec.name, state["arguments"])
        except Exception as exc:
            self.events.add(run_id, "tool_failed", tool=tool.spec.name, error=str(exc))
            return self._failed(run_id, f"Tool {tool.spec.name} refused: {exc}")
        self.events.add(run_id, "tool_completed", tool=tool.spec.name)
        self.events.add(run_id, "run_completed", resumed=True)
        return RunResult(run_id, "completed", str(output), events=self.events.get(run_id))

    def _failed(self, run_id, message):
        self.events.add(run_id, "run_failed", error=message)
        return RunResult(run_id, "failed", message, events=self.events.get(run_id))
