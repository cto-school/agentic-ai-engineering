from __future__ import annotations
import re
from .schemas import Finding


RULES = {
 "DEF-COR-01": ("correctness", "quantity", "Negative quantities are accepted", "high", "Validate quantity is a positive integer."),
 "DEF-COR-02": ("correctness", "subtotal - 20", "Discount can make total negative", "medium", "Use a percentage and clamp or reject invalid totals."),
 "DEF-COR-03": ("correctness", "/ len(items)", "Empty input causes division by zero", "medium", "Define empty-list behavior before division."),
 "DEF-SEC-01": ("security", "ADMIN_TOKEN", "Credential-like token is hardcoded", "high", "Load secrets from an injected secret store."),
 "DEF-SEC-02": ("security", "SELECT * FROM", "SQL query uses string concatenation", "critical", "Use a parameterized query."),
 "DEF-SEC-03": ("security", "eval(", "Untrusted expression may reach eval", "critical", "Replace eval with an allow-listed parser."),
 "DEF-SEC-04": ("security", "user.get(\"token\")", "Sensitive token is logged", "high", "Never log tokens; redact sensitive fields."),
 "DEF-MNT-01": ("maintainability", "audit=[]", "Mutable default argument retains state", "medium", "Default to None and create a list inside."),
 "DEF-MNT-02": ("maintainability", "except Exception", "Broad exception hides failures", "medium", "Catch only expected exceptions and record context."),
}


def _finding(defect_id: str, lines: list[str], reviewer: str) -> Finding:
    category, needle, title, severity, fix = RULES[defect_id]
    line = next((i for i, text in enumerate(lines, 1) if needle in text), 1)
    return Finding(defect_id, category, line, title, lines[line-1].strip(), severity, fix, reviewer)


def specialist_review(source: str, category: str) -> list[Finding]:
    lines = source.splitlines()
    return [_finding(i, lines, f"{category}_specialist") for i, rule in RULES.items()
            if rule[0] == category and rule[1] in source]


def single_reviewer(source: str) -> list[Finding]:
    """A reproducible baseline with realistic blind spots, not a claim about all LLMs."""
    visible = {"DEF-COR-03", "DEF-SEC-01", "DEF-SEC-02", "DEF-SEC-03", "DEF-MNT-01"}
    lines = source.splitlines()
    return [_finding(i, lines, "general_reviewer") for i in visible if RULES[i][1] in source]
