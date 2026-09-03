from __future__ import annotations
import json,os,re,urllib.error,urllib.request
from typing import Protocol
from .schemas import Finding


class ReviewerProvider(Protocol):
    def review(self,source: str,role: str) -> tuple[list[Finding],dict]: ...


def _prompt(source: str,role: str) -> list[dict]:
    scope="all correctness, security, and maintainability concerns" if role=="general" else f"only {role} concerns"
    schema='{"findings":[{"category":"correctness|security|maintainability","line":1,"title":"...","evidence":"exact source excerpt","severity":"low|medium|high|critical","recommendation":"..."}]}'
    return [{"role":"system","content":f"You are a bounded engineering reviewer. Review {scope}. Return JSON only in this shape: {schema}. Report at most 10 evidenced findings. Do not invent code."},
            {"role":"user","content":"Review this synthetic Python artifact:\n\n"+source}]


def _parse_findings(content: str,role: str) -> list[Finding]:
    content=content.strip()
    if content.startswith("```"):
        content=re.sub(r"^```(?:json)?\s*|\s*```$","",content,flags=re.I)
    data=json.loads(content); raw=data.get("findings",[])
    if not isinstance(raw,list) or len(raw)>10: raise ValueError("findings must be a list of at most 10")
    allowed_categories={"correctness","security","maintainability"}; allowed_severity={"low","medium","high","critical"}
    findings=[]
    for index,item in enumerate(raw,1):
        category=item.get("category"); severity=item.get("severity"); line=item.get("line")
        if category not in allowed_categories or severity not in allowed_severity or not isinstance(line,int):
            raise ValueError(f"Invalid finding {index}")
        if role!="general" and category!=role: raise ValueError(f"{role} reviewer returned {category}")
        for field in ("title","evidence","recommendation"):
            if not isinstance(item.get(field),str) or not item[field].strip(): raise ValueError(f"Missing {field}")
        findings.append(Finding(f"MODEL-{role[:3].upper()}-{line}-{index}",category,line,item["title"],
            item["evidence"],severity,item["recommendation"],f"{role}_model_reviewer"))
    return findings


class OpenRouterReviewer:
    def __init__(self,api_key: str|None=None,model: str|None=None):
        self.api_key=api_key or os.getenv("OPENROUTER_API_KEY"); self.model=model or os.getenv("OPENROUTER_MODEL","openai/gpt-oss-120b")
        if not self.api_key: raise ValueError("OPENROUTER_API_KEY is required")

    def review(self,source,role):
        payload={"model":self.model,"messages":_prompt(source,role),"temperature":0,"max_tokens":1200,
                 "response_format":{"type":"json_object"},"reasoning":{"effort":"low","exclude":False},
                 "provider":{"sort":"price","require_parameters":True}}
        request=urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode(),method="POST",headers={"Content-Type":"application/json","Authorization":f"Bearer {self.api_key}"})
        try:
            with urllib.request.urlopen(request,timeout=120) as response: data=json.loads(response.read().decode())
        except (urllib.error.URLError,TimeoutError,json.JSONDecodeError) as exc: raise RuntimeError(f"Review request failed: {exc}") from exc
        message=data["choices"][0]["message"]; usage=data.get("usage") or {}
        findings=_parse_findings(message.get("content") or "",role)
        return findings,{"model":self.model,"prompt_tokens":usage.get("prompt_tokens",0) or 0,
            "completion_tokens":usage.get("completion_tokens",0) or 0,"cost_usd":float(usage.get("cost",0) or 0)}


class MockStructuredReviewer:
    """Deterministic stand-in that exercises the same role/provider contract offline."""
    def review(self,source,role):
        from .reviewers import single_reviewer,specialist_review
        findings=single_reviewer(source) if role=="general" else specialist_review(source,role)
        for finding in findings: finding.reviewer=f"{role}_mock_model"
        return findings,{"model":"mock-structured-reviewer","prompt_tokens":(len(source)+3)//4,
                         "completion_tokens":len(findings)*45,"cost_usd":0.0}
