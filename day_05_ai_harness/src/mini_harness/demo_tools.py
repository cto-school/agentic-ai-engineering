from .registry import ToolRegistry
from .schemas import ToolSpec


def build_demo_registry() -> ToolRegistry:
    registry=ToolRegistry()
    registry.register(ToolSpec("lookup_notes","Search supplied synthetic notes",{
        "type":"object","properties":{"query":{"type":"string"}},"required":["query"],"additionalProperties":False},"read"),
        lambda query:{"query":query,"note":"The course harness centralizes policy and events."})
    registry.register(ToolSpec("create_draft","Create a reversible local draft",{
        "type":"object","properties":{"subject":{"type":"string"},"body":{"type":"string"}},
        "required":["subject","body"],"additionalProperties":False},"write"),
        lambda subject,body:{"draft":True,"subject":subject,"body":body})
    registry.register(ToolSpec("send_email","Send a simulated external email",{
        "type":"object","properties":{"to":{"type":"string"},"subject":{"type":"string"},"body":{"type":"string"}},
        "required":["to","subject","body"],"additionalProperties":False},"external"),
        lambda to,subject,body:{"sent":True,"to":to,"subject":subject,"body":body})
    registry.register(ToolSpec("erase_workspace","Delete all workspace data",{
        "type":"object","properties":{},"additionalProperties":False},"destructive"),lambda:{"erased":True})
    return registry
