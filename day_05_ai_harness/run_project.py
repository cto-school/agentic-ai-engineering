from pathlib import Path
import json,sys
ROOT=Path(__file__).parent; sys.path.insert(0,str(ROOT/"src"))
from mini_harness import *

def load(name):
    raw=json.loads((ROOT/"configs"/f"{name}.json").read_text(encoding="utf-8")); raw["model"]=ModelConfig(**raw["model"])
    return AgentConfig(**raw)

runtime=HarnessRuntime(build_demo_registry(),MockModel())
for name,prompt in [("research_agent","What is a harness?"),("task_agent","Prepare a project update")]:
    result=runtime.run(load(name),prompt); print(name,result.status,result.output); print(*result.events,sep="\n")
task=load("task_agent"); pending=runtime.run(task,"Send a synthetic course update")
print("PAUSED",pending.pending_action); print("RESUMED",runtime.resume(pending.run_id,task,approved=True))
