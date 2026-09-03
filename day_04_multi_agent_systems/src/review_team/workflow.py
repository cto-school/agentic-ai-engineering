from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
from .checks import deterministic_checks
from .reviewers import single_reviewer, specialist_review
from .schemas import ReviewRun
from .supervisor import synthesize
from .model_reviewers import ReviewerProvider


def _tokens(source: str, calls: int) -> int: return ((len(source) + 3) // 4) * calls


def run_single(source: str) -> ReviewRun:
    start = perf_counter(); findings = single_reviewer(source)
    return ReviewRun("single", findings, 1, _tokens(source, 1), (perf_counter()-start)*1000,
                     [{"step":"general_reviewer","count":len(findings)}])


def run_augmented(source: str) -> ReviewRun:
    start = perf_counter(); checks = deterministic_checks(source); review = single_reviewer(source)
    findings = synthesize([checks, review])
    return ReviewRun("checks_plus_single", findings, 1, _tokens(source, 1), (perf_counter()-start)*1000,
        [{"step":"deterministic_checks","count":len(checks)}, {"step":"general_reviewer","count":len(review)},
         {"step":"synthesis","count":len(findings)}])


def run_multi(source: str) -> ReviewRun:
    start = perf_counter(); categories = ["correctness", "security", "maintainability"]
    with ThreadPoolExecutor(max_workers=3) as pool:
        groups = list(pool.map(lambda c: specialist_review(source, c), categories))
    checks = deterministic_checks(source)
    findings = synthesize([checks, *groups])
    trace = [{"step":f"{c}_specialist","count":len(g)} for c,g in zip(categories,groups)]
    trace += [{"step":"deterministic_checks","count":len(checks)}, {"step":"supervisor","count":len(findings)}]
    return ReviewRun("multi_specialist", findings, 3, _tokens(source, 3), (perf_counter()-start)*1000, trace)


def run_model_review(source: str,provider: ReviewerProvider,role: str="general") -> ReviewRun:
    start=perf_counter(); findings,usage=provider.review(source,role)
    tokens=int(usage.get("prompt_tokens",0))+int(usage.get("completion_tokens",0))
    return ReviewRun(f"model_{role}",findings,1,tokens,(perf_counter()-start)*1000,
        [{"step":f"{role}_model_reviewer","count":len(findings),"usage":usage}])


def run_model_multi(source: str,provider: ReviewerProvider) -> ReviewRun:
    start=perf_counter(); categories=["correctness","security","maintainability"]
    # Sequential by default for classroom readability and predictable rate limits.
    reviewed=[provider.review(source,category) for category in categories]
    groups=[item[0] for item in reviewed]; usage=[item[1] for item in reviewed]
    findings=synthesize(groups); tokens=sum(int(u.get("prompt_tokens",0))+int(u.get("completion_tokens",0)) for u in usage)
    trace=[{"step":f"{category}_model_reviewer","count":len(group),"usage":u}
           for category,group,u in zip(categories,groups,usage)]
    trace.append({"step":"supervisor","count":len(findings)})
    return ReviewRun("model_multi_specialist",findings,3,tokens,(perf_counter()-start)*1000,trace)
