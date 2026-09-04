"""Offline repository-wide course validation. No API keys or hosted calls required.

The day notebooks (day_0X_complete.ipynb) are the source of truth; the lesson notebooks
under each notebooks/ folder are derived from them by split_day_notebooks.py.
"""
from __future__ import annotations
import ast, importlib.util, json, py_compile, sys
from pathlib import Path

ROOT=Path(__file__).parent
DAYS=[ROOT/f"day_{n:02d}_{slug}" for n,slug in [
    (1,"model_tools_agent"),(2,"knowledge_and_state"),(3,"memory_and_safety"),
    (4,"multi_agent_systems"),(5,"ai_harness")]]


def _tags(cell): return set(cell.get("metadata",{}).get("tags",[]))


def _python(cell):
    """Code-cell source with IPython magics (%pip, !cmd) removed so ast can parse it."""
    return "".join(line for line in cell["source"] if not line.startswith(("%","!")))   # magics sit in column 0


def validate_day_notebooks():
    """Each day notebook exists, parses, lists its sections, and has one live observation."""
    sections=cells=live=0
    for index,day in enumerate(DAYS,start=1):
        path=day/f"day_{index:02d}_complete.ipynb"
        if not path.exists(): raise AssertionError(f"Missing day notebook: {path.name}")
        notebook=json.loads(path.read_text(encoding="utf-8"))
        if notebook.get("nbformat")!=4: raise AssertionError(f"Unexpected format: {path}")
        files=notebook.get("metadata",{}).get("course",{}).get("generated_from") or []
        starts=[c for c in notebook["cells"] if "master-section-start" in _tags(c)]
        if not files or len(starts)!=len(files):
            raise AssertionError(f"{path.name}: {len(starts)} section starts but {len(files)} section files listed")
        if not any(f.split("_",1)[1].startswith("exercise_") or "_exercise_" in f for f in files):
            raise AssertionError(f"{path.name}: no hands-on exercise section")
        day_live=0
        for cell in notebook["cells"]:
            if cell["cell_type"]=="code": ast.parse(_python(cell)); cells+=1
            if "required-live-observation" in _tags(cell): day_live+=1
        if day_live!=1: raise AssertionError(f"{path.name}: expected one live-observation cell, found {day_live}")
        live+=day_live; sections+=len(files)
    return sections,cells,live


def validate_lesson_notebooks():
    """Derived lesson notebooks match the section list of their day notebook and parse."""
    count=0
    for index,day in enumerate(DAYS,start=1):
        master=json.loads((day/f"day_{index:02d}_complete.ipynb").read_text(encoding="utf-8"))
        expected=sorted(master["metadata"]["course"]["generated_from"])
        actual=sorted(p.name for p in (day/"notebooks").glob("*.ipynb"))
        if expected!=actual:
            raise AssertionError(f"{day.name}: lesson notebooks differ from the day notebook's section list.\n  run: py split_day_notebooks.py\n  expected {expected}\n  found    {actual}")
        for path in (day/"notebooks").glob("*.ipynb"):
            notebook=json.loads(path.read_text(encoding="utf-8")); count+=1
            markdown="".join("".join(c["source"]) for c in notebook["cells"] if c["cell_type"]=="markdown")
            if not markdown.strip(): raise AssertionError(f"{path}: no student-facing explanation")
            for cell in notebook["cells"]:
                if cell["cell_type"]=="code": ast.parse(_python(cell))
    return count


def validate_python():
    files=[]
    for day in DAYS:
        files += list((day/"src").rglob("*.py"))
        files += list((day/"tests").glob("test_*.py"))
    files += list((ROOT/"exercises").rglob("*.py"))
    files.append(ROOT/"split_day_notebooks.py")
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
    sections,cells,live=validate_day_notebooks(); lessons=validate_lesson_notebooks(); python_files=validate_python(); (tests,skipped)=run_plain_tests(); docs=validate_course_files()
    print(f"PASS: 5 day notebooks with {sections} sections and {cells} code cells, {lessons} derived lesson notebooks, {live} live-observation cells, {python_files} Python files, {tests} executed tests, {docs} key documents")
    if skipped:
        print("WARN: install requirements.txt to execute skipped test modules:")
        for item in skipped: print(" -",item)
