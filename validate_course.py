"""Offline repository-wide course validation. No API keys or hosted calls required."""
from __future__ import annotations
import ast, importlib.util, json, py_compile, sys
from pathlib import Path

ROOT=Path(__file__).parent
DAYS=[ROOT/f"day_{n:02d}_{slug}" for n,slug in [
    (1,"model_tools_agent"),(2,"knowledge_and_state"),(3,"memory_and_safety"),
    (4,"multi_agent_systems"),(5,"ai_harness")]]


def validate_notebooks():
    count=cells=theory_cells=live_cells=0
    for day in DAYS:
        files=sorted((day/"notebooks").glob("*.ipynb"))
        if not files: raise AssertionError(f"No notebooks: {day.name}")
        for path in files:
            notebook=json.loads(path.read_text(encoding="utf-8")); count+=1
            if notebook.get("nbformat")!=4: raise AssertionError(f"Unexpected format: {path}")
            for cell in notebook["cells"]:
                if cell["cell_type"]=="code": ast.parse("".join(cell["source"])); cells+=1
                if "embedded-course-theory" in cell.get("metadata",{}).get("tags",[]): theory_cells+=1
                if "required-live-observation" in cell.get("metadata",{}).get("tags",[]): live_cells+=1
    if count != 45: raise AssertionError(f"Expected 45 notebooks including exercises and operational capstone, found {count}")
    if theory_cells < 31: raise AssertionError(f"Embedded theory missing: found {theory_cells} tagged cells")
    if live_cells != 5: raise AssertionError(f"Expected five required live-observation cells, found {live_cells}")
    required_exercises={
        "08_exercise_manual_agent_loop.ipynb", "09_exercise_rag_context.ipynb",
        "10_exercise_history_compaction.ipynb", "11_exercise_action_policy.ipynb",
        "08_exercise_supervisor_merge.ipynb", "08_exercise_tool_registry.ipynb",
    }
    actual={p.name for day in DAYS for p in (day/"notebooks").glob("*_exercise_*.ipynb")}
    if actual != required_exercises: raise AssertionError(f"Exercise notebook mismatch: {actual}")
    return count,cells,theory_cells,live_cells


def validate_python():
    files=[]
    for day in DAYS:
        files += list((day/"src").rglob("*.py"))
        files += list((day/"tests").glob("test_*.py"))
    files += list((ROOT/"exercises").rglob("*.py"))
    for path in files: py_compile.compile(str(path),doraise=True)
    return len(files)


def run_plain_tests():
    total=0; skipped=[]
    for day in DAYS:
        for path in (day/"tests").glob("test_*.py"):
            sys.path.insert(0,str(day/"src")); sys.path.insert(0,str(path.parent))
            name=f"qa_{day.name}_{path.stem}"
            spec=importlib.util.spec_from_file_location(name,path); module=importlib.util.module_from_spec(spec)
            try:
                assert spec.loader; spec.loader.exec_module(module)
            except ModuleNotFoundError as exc:
                skipped.append(f"{day.name}: missing {exc.name}")
                sys.path=[p for p in sys.path if p not in {str(day/"src"),str(path.parent)}]
                continue
            for attr in dir(module):
                if attr.startswith("test_") and callable(getattr(module,attr)):
                    getattr(module,attr)(); total+=1
            sys.path=[p for p in sys.path if p not in {str(day/"src"),str(path.parent)}]
    return total,skipped


def validate_course_files():
    required=[ROOT/"README.md",ROOT/"reference"/"glossary.md",ROOT/"instructor"/"delivery_guide.md",
              ROOT/"instructor"/"five_day_timetable.md",ROOT/"reference"/"conceptual_answer_key.md",
              ROOT/"instructor"/"live_observation_contract.md",
              ROOT/"reference"/"rag_failure_diagnosis.md",ROOT/"exercises"/"README.md",
              ROOT/"diagrams"/"source"/"day_01.md",ROOT/"diagrams"/"source"/"day_02.md",
              ROOT/"diagrams"/"source"/"day_03.md",ROOT/"diagrams"/"source"/"day_04.md",
              ROOT/"diagrams"/"source"/"day_05.md"]
    required += [day/"theory.md" for day in DAYS]
    missing=[str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing: raise AssertionError(f"Missing course files: {missing}")
    return len(required)


if __name__=="__main__":
    notebooks,cells,theory_cells,live_cells=validate_notebooks(); python_files=validate_python(); (tests,skipped)=run_plain_tests(); docs=validate_course_files()
    print(f"PASS: {notebooks} notebooks, {cells} code cells, {theory_cells} embedded theory cells, {live_cells} live-observation cells, {python_files} Python files, {tests} executed tests, {docs} key documents")
    if skipped:
        print("WARN: install requirements.txt to execute skipped test modules:")
        for item in skipped: print(" -",item)
