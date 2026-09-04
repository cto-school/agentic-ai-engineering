"""Scripted stand-in reviewers.

IMPORTANT for students: these functions are NOT language models. They are scripted
reviewers whose blind spots we choose on purpose, so that a classroom A/B comparison
is reproducible on any laptop with no API key. Nothing here is a claim about how good
real LLMs are at code review.

Because the blind spots are a *parameter*, we can run the same architecture comparison
under two different worlds:

* "blind_spots"       - the single general reviewer misses a lot; specialists help.
* "strong_generalist" - the single general reviewer is nearly as good as the whole
                        team, so the team pays 3x the model calls for no extra recall.

Day 4's honest answer ("sometimes one agent is enough") only becomes visible because
both worlds exist.
"""
from __future__ import annotations

from .schemas import Finding

# Every seeded defect: id -> (category, source needle, title, severity, recommendation).
# The needle is how a scripted reviewer "locates" the defect in the artifact.
RULES = {
    "DEF-COR-01": ("correctness", "quantity", "Negative quantities are accepted", "high",
                   "Validate quantity is a positive integer."),
    "DEF-COR-02": ("correctness", "subtotal - 20", "Discount can make total negative", "medium",
                   "Use a percentage and clamp or reject invalid totals."),
    "DEF-COR-03": ("correctness", "/ len(items)", "Empty input causes division by zero", "medium",
                   "Define empty-list behavior before division."),
    "DEF-SEC-01": ("security", "ADMIN_TOKEN", "Credential-like token is hardcoded", "high",
                   "Load secrets from an injected secret store."),
    "DEF-SEC-02": ("security", "SELECT * FROM", "SQL query uses string concatenation", "critical",
                   "Use a parameterized query."),
    "DEF-SEC-03": ("security", "eval(", "Untrusted expression may reach eval", "critical",
                   "Replace eval with an allow-listed parser."),
    "DEF-SEC-04": ("security", 'user.get("token")', "Sensitive token is logged", "high",
                   "Never log tokens; redact sensitive fields."),
    "DEF-MNT-01": ("maintainability", "audit=[]", "Mutable default argument retains state", "medium",
                   "Default to None and create a list inside."),
    "DEF-MNT-02": ("maintainability", "except Exception", "Broad exception hides failures", "medium",
                   "Catch only expected exceptions and record context."),
}

ALL_IDS = sorted(RULES)

# Which defect ids each role is able to see, per scenario.
SCENARIOS: dict[str, dict[str, list[str]]] = {
    # World A: one generalist has real blind spots; narrow roles cover them.
    "blind_spots": {
        "general": ["DEF-COR-03", "DEF-SEC-01", "DEF-SEC-02", "DEF-SEC-03", "DEF-MNT-01"],
        "correctness": ["DEF-COR-01", "DEF-COR-02", "DEF-COR-03"],
        "security": ["DEF-SEC-01", "DEF-SEC-02", "DEF-SEC-03", "DEF-SEC-04"],
        "maintainability": ["DEF-MNT-01", "DEF-MNT-02"],
    },
    # World B: the generalist is strong. It misses only the subtle business rule
    # (DEF-COR-02) - and so does the correctness specialist, because narrowing the
    # prompt does not create knowledge the reviewer never had.
    "strong_generalist": {
        "general": [i for i in ALL_IDS if i != "DEF-COR-02"],
        "correctness": ["DEF-COR-01", "DEF-COR-03"],
        "security": ["DEF-SEC-01", "DEF-SEC-02", "DEF-SEC-03", "DEF-SEC-04"],
        "maintainability": ["DEF-MNT-01", "DEF-MNT-02"],
    },
}

DEFAULT_SCENARIO = "blind_spots"


def _visible(scenario: str, role: str) -> list[str]:
    """Look up which defect ids `role` can see in `scenario`, with a clear error."""
    if scenario not in SCENARIOS:
        raise KeyError(f"Unknown scenario {scenario!r}. Choose one of {sorted(SCENARIOS)}.")
    roles = SCENARIOS[scenario]
    if role not in roles:
        raise KeyError(f"Scenario {scenario!r} has no role {role!r}. Roles: {sorted(roles)}.")
    return roles[role]


def _finding(defect_id: str, lines: list[str], reviewer: str) -> Finding:
    """Build one Finding, locating the defect by searching the artifact for its needle."""
    category, needle, title, severity, fix = RULES[defect_id]
    line = next((i for i, text in enumerate(lines, 1) if needle in text), 1)
    return Finding(defect_id, category, line, title, lines[line - 1].strip(), severity, fix, reviewer)


def single_reviewer(source: str, scenario: str = DEFAULT_SCENARIO) -> list[Finding]:
    """One general reviewer looking at every category at once."""
    lines = source.splitlines()
    ids = [i for i in _visible(scenario, "general") if RULES[i][1] in source]
    findings = [_finding(i, lines, "general_reviewer") for i in sorted(ids)]
    return sorted(findings, key=lambda f: (f.line, f.id))   # top-to-bottom, like a human


def specialist_review(source: str, category: str, scenario: str = DEFAULT_SCENARIO) -> list[Finding]:
    """One narrow reviewer that may only report findings in its own category."""
    lines = source.splitlines()
    ids = [i for i in _visible(scenario, category) if RULES[i][1] in source]
    findings = [_finding(i, lines, f"{category}_specialist") for i in sorted(ids)]
    return sorted(findings, key=lambda f: (f.line, f.id))
