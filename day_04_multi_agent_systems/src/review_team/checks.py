from __future__ import annotations
import ast
from .schemas import Finding


def deterministic_checks(source: str) -> list[Finding]:
    """Objective AST checks run before model-like judgment."""
    tree = ast.parse(source)
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "eval":
            findings.append(Finding("DEF-SEC-03", "security", node.lineno, "Use of eval",
                ast.get_source_segment(source, node) or "eval", "critical", "Use an allow-listed parser.", "ast_check"))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(isinstance(d, (ast.List, ast.Dict, ast.Set)) for d in node.args.defaults):
                findings.append(Finding("DEF-MNT-01", "maintainability", node.lineno,
                    "Mutable default argument", node.name, "medium", "Default to None.", "ast_check"))
        if isinstance(node, ast.ExceptHandler) and isinstance(node.type, ast.Name) and node.type.id == "Exception":
            findings.append(Finding("DEF-MNT-02", "maintainability", node.lineno,
                "Broad exception handler", "except Exception", "medium", "Catch expected exceptions.", "ast_check"))
    return findings
