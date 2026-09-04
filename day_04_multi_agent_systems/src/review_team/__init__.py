"""Day 4 review team package.

Import the names you need explicitly, for example:

    from review_team import MockStructuredReviewer, run_specialist_team, evaluate
"""
from .checks import deterministic_checks
from .evaluation import evaluate, match_to_golden
from .model_reviewers import (FallbackReviewer, MockStructuredReviewer,
                              OpenRouterReviewer, ReviewerProvider)
from .reviewers import DEFAULT_SCENARIO, RULES, SCENARIOS, single_reviewer, specialist_review
from .schemas import Finding, ReviewRun, SynthesisReport
from .supervisor import synthesize, synthesize_with_report
from .workflow import (SPECIALIST_ROLES, run_checks_plus_reviewer, run_single_reviewer,
                       run_specialist_team)

__all__ = [
    # contracts
    "Finding", "ReviewRun", "SynthesisReport",
    # reviewers
    "single_reviewer", "specialist_review", "SCENARIOS", "DEFAULT_SCENARIO", "RULES",
    "MockStructuredReviewer", "OpenRouterReviewer", "FallbackReviewer", "ReviewerProvider",
    # tools and fan-in
    "deterministic_checks", "synthesize", "synthesize_with_report",
    # the three systems we compare
    "run_single_reviewer", "run_checks_plus_reviewer", "run_specialist_team",
    "SPECIALIST_ROLES",
    # measurement
    "evaluate", "match_to_golden",
]
