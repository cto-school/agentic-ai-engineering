from __future__ import annotations
import json
from uuid import uuid4
from .events import CheckpointStore,EventStore
from .policy import decide
from .providers import ModelProvider
from .registry import ToolRegistry
from .schemas import AgentConfig,RunResult


class HarnessRuntime:
    def __init__(self,registry: ToolRegistry,provider: ModelProvider,events=None,checkpoints=None):
        self.registry=registry; self.provider=provider
        self.events=events or EventStore(); self.checkpoints=checkpoints or CheckpointStore()

    def run(self,config: AgentConfig,prompt: str,run_id: str|None=None) -> RunResult:
        run_id=run_id or str(uuid4()); history=[]
        self.events.add(run_id,"run_started",agent=config.name,model=config.model.model)
        for step in range(1,min(config.max_steps,10)+1):
            tools=self.registry.discover(config.allowed_tools)
            self.events.add(run_id,"model_requested",step=step,visible_tools=[t.name for t in tools])
            try:
                choice=self.provider.decide(prompt,config,tools,history)
            except Exception as exc:
                return self._failed(run_id,f"Model error: {exc}")
            self.events.add(run_id,"model_completed",step=step,usage=choice.usage)
            if choice.kind=="final":
                self.events.add(run_id,"run_completed",step=step)
                return RunResult(run_id,"completed",choice.content,events=self.events.get(run_id))
            try: registered=self.registry.get(choice.tool or "")
            except KeyError as exc: return self._failed(run_id,str(exc))
            try: self.registry.validate(registered.spec.name,choice.arguments)
            except (ValueError,TypeError) as exc: return self._failed(run_id,str(exc))
            policy=decide(config,registered.spec)
            self.events.add(run_id,"policy_decision",tool=registered.spec.name,decision=policy)
            call_id=choice.call_id or f"local-call-{step}"
            history.append({"role":"assistant","content":"","tool_calls":[{"id":call_id,"type":"function",
                "function":{"name":registered.spec.name,"arguments":json.dumps(choice.arguments)}}],
                "reasoning_details":choice.reasoning_details})
            if policy=="deny": return self._failed(run_id,f"Denied tool: {registered.spec.name}")
            if policy=="approval":
                pending={"tool":registered.spec.name,"arguments":choice.arguments,"history":history,"prompt":prompt,
                         "agent":config.name,"steps_used":step}
                self.checkpoints.save(run_id,pending); self.events.add(run_id,"approval_requested",**pending)
                return RunResult(run_id,"pending_approval",pending_action=pending,events=self.events.get(run_id))
            output=self.registry.call(registered.spec.name,choice.arguments)
            history.append({"role":"tool","name":registered.spec.name,"tool_call_id":call_id,"content":str(output)})
            self.events.add(run_id,"tool_completed",tool=registered.spec.name)
        self.events.add(run_id,"step_limit_reached",limit=config.max_steps)
        return RunResult(run_id,"step_limit","Maximum steps reached.",events=self.events.get(run_id))

    def resume(self,run_id: str,config: AgentConfig,approved: bool) -> RunResult:
        state=self.checkpoints.load(run_id)
        if not state: return self._failed(run_id,"Checkpoint not found")
        self.events.add(run_id,"approval_resolved",approved=approved)
        self.checkpoints.delete(run_id)
        if not approved:
            self.events.add(run_id,"run_cancelled",reason="User rejected action")
            return RunResult(run_id,"cancelled","User rejected action",events=self.events.get(run_id))
        tool=self.registry.get(state["tool"])
        if decide(config,tool.spec)!="approval": return self._failed(run_id,"Policy changed while paused")
        output=self.registry.call(tool.spec.name,state["arguments"])
        self.events.add(run_id,"tool_completed",tool=tool.spec.name)
        self.events.add(run_id,"run_completed",resumed=True)
        return RunResult(run_id,"completed",str(output),events=self.events.get(run_id))

    def _failed(self,run_id,message):
        self.events.add(run_id,"run_failed",error=message)
        return RunResult(run_id,"failed",message,events=self.events.get(run_id))
