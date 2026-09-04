"""Deterministic (non-model) checks.

A Python parser can *prove* some of these defects. Proving is cheaper, faster and more
repeatable than asking a model. Note the ids: this checker emits its own `AST-...` ids
because a real static analyser has never heard of our golden defect list. The evaluator
therefore has to match findings to defects by location, exactly as it would for a model.
"""
from __future__ import annotations

import ast

from .schemas import Finding


def deterministic_checks(source: str) -> list[Finding]:
    """Walk the syntax tree and report the patterns a parser can establish as facts."""
    tree = ast.parse(source)                    # parse once; raises SyntaxError on bad input
    lines = source.splitlines()
    findings: list[Finding] = []

    def excerpt(lineno: int) -> str:
        """The source line the finding points at, so every claim carries evidence."""
        return lines[lineno - 1].strip() if 0 < lineno <= len(lines) else ""

    for node in ast.walk(tree):                 # visit every node in the file
        # 1) A direct call to eval() is a fact, not an opinion.
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "eval":
            findings.append(Finding(
                f"AST-EVAL-{node.lineno}", "security", node.lineno,
                "Call to eval()", excerpt(node.lineno), "critical",
                "Use an allow-listed parser instead of eval.", "ast_checker"))

        # 2) A mutable default argument is visible in the function signature.
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(isinstance(d, (ast.List, ast.Dict, ast.Set)) for d in node.args.defaults):
                findings.append(Finding(
                    f"AST-MUTABLE-DEFAULT-{node.lineno}", "maintainability", node.lineno,
                    "Mutable default argument", excerpt(node.lineno), "medium",
                    "Default to None and build the container inside the function.", "ast_checker"))

        # 3) `except Exception:` swallows unrelated failures.
        if isinstance(node, ast.ExceptHandler) and isinstance(node.type, ast.Name) and node.type.id == "Exception":
            findings.append(Finding(
                f"AST-BROAD-EXCEPT-{node.lineno}", "maintainability", node.lineno,
                "Broad exception handler", excerpt(node.lineno), "medium",
                "Catch only the exceptions you expect.", "ast_checker"))

    return sorted(findings, key=lambda f: (f.line, f.id))
