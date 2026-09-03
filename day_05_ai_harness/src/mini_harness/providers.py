from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
from typing import Protocol
from .schemas import AgentConfig, ModelDecision, ToolSpec


class ModelProvider(Protocol):
    def decide(self, prompt: str, config: AgentConfig, tools: list[ToolSpec], history: list[dict]) -> ModelDecision: ...


class MockModel:
    """Deterministic orchestration test double; it never pretends to be intelligent."""
    def decide(self,prompt,config,tools,history):
        outputs=[h for h in history if h.get("role")=="tool"]
        if outputs: return ModelDecision("final",content=f"Completed with tool result: {outputs[-1]['content']}")
        names={t.name for t in tools}
        if config.name=="research_agent" and "lookup_notes" in names:
            return ModelDecision("tool",tool="lookup_notes",arguments={"query":prompt})
        if config.name=="task_agent" and "send_email" in names and "send" in prompt.lower():
            return ModelDecision("tool",tool="send_email",arguments={"to":"mentor@example.test","subject":"Course update","body":prompt})
        if config.name=="task_agent" and "create_draft" in names:
            return ModelDecision("tool",tool="create_draft",arguments={"subject":"Course update","body":prompt})
        return ModelDecision("final",content="No permitted tool is needed.")


def build_provider(config):
    if config.provider=="mock": return MockModel()
    if config.provider=="openrouter": return OpenAICompatibleProvider(
        model=config.model,base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),max_tokens=config.max_output_tokens,
        temperature=config.temperature,reasoning_effort=os.getenv("OPENROUTER_REASONING_EFFORT","low"))
    if config.provider=="ollama": return OpenAICompatibleProvider(
        model=config.model,base_url=os.getenv("OLLAMA_OPENAI_BASE_URL","http://localhost:11434/v1"),
        api_key="ollama",max_tokens=config.max_output_tokens,temperature=config.temperature)
    raise ValueError(f"Unsupported provider: {config.provider}")


class OpenAICompatibleProvider:
    """Small OpenRouter/Ollama adapter using the provider-neutral harness contracts."""

    def __init__(self,model: str,base_url: str,api_key: str|None,max_tokens: int=400,
                 temperature: float=0.0,reasoning_effort: str|None=None):
        if not api_key: raise ValueError("The selected provider API key is not configured")
        self.model=model; self.base_url=base_url.rstrip("/"); self.api_key=api_key
        self.max_tokens=max_tokens; self.temperature=temperature; self.reasoning_effort=reasoning_effort

    def decide(self,prompt,config,tools,history):
        normalized_history=[]
        for item in history:
            message={key:value for key,value in item.items() if key in {"role","content","tool_calls","tool_call_id","name","reasoning_details"}}
            normalized_history.append(message)
        messages=[{"role":"system","content":config.instructions},
                  {"role":"user","content":prompt},*normalized_history]
        payload={"model":self.model,"messages":messages,"temperature":self.temperature,
                 "max_tokens":self.max_tokens,"tools":[{"type":"function","function":{
                     "name":tool.name,"description":tool.description,"parameters":tool.input_schema}}
                     for tool in tools]}
        if self.reasoning_effort:
            payload["reasoning"]={"effort":self.reasoning_effort,"exclude":False}
        request=urllib.request.Request(f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),method="POST",
            headers={"Content-Type":"application/json","Authorization":f"Bearer {self.api_key}"})
        try:
            with urllib.request.urlopen(request,timeout=120) as response:
                data=json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError,TimeoutError,json.JSONDecodeError) as exc:
            raise RuntimeError(f"Model request failed: {exc}") from exc
        message=data["choices"][0]["message"]; usage=data.get("usage") or {}
        usage_record={"prompt_tokens":usage.get("prompt_tokens",0) or 0,
                      "completion_tokens":usage.get("completion_tokens",0) or 0,
                      "cost_usd":float(usage.get("cost",0) or 0)}
        calls=message.get("tool_calls") or []
        if calls:
            function=calls[0]["function"]; arguments=function.get("arguments",{})
            if isinstance(arguments,str): arguments=json.loads(arguments)
            return ModelDecision("tool",tool=function["name"],arguments=arguments,usage=usage_record,
                call_id=calls[0].get("id"),reasoning_details=message.get("reasoning_details") or [])
        return ModelDecision("final",content=message.get("content") or "",usage=usage_record,
            reasoning_details=message.get("reasoning_details") or [])
