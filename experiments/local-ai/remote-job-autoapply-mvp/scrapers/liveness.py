import re
import requests
from ai.schemas import LivenessResult

_EXPIRED_PATTERNS = [
    re.compile(r"job (is )?no longer available", re.I),
    re.compile(r"position has been filled", re.I),
    re.compile(r"this job has expired", re.I),
    re.compile(r"no longer accepting applications", re.I),
    re.compile(r"this (position|role|job) (is )?no longer", re.I),
    re.compile(r"job (listing )?is closed", re.I),
    re.compile(r"applications?\s+(?:(?:have|are|is)\s+)?closed", re.I),
    re.compile(r"job listing not found", re.I),
    re.compile(r"the page you.re looking for doesn.t exist", re.I),
]

_LISTING_PAGE_PATTERNS = [
    re.compile(r"\d+\s+jobs?\s+found", re.I),
    re.compile(r"search results", re.I),
]

_APPLY_PATTERNS = [
    re.compile(r"\bapply\b", re.I),
    re.compile(r"submit application", re.I),
    re.compile(r"easy apply", re.I),
    re.compile(r"start application", re.I),
]

_MIN_CONTENT_CHARS = 300


def check_liveness(url: str, timeout: int = 10) -> LivenessResult:
    try:
        resp = requests.get(url, timeout=timeout, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
    except requests.RequestException as exc:
        return LivenessResult(status="uncertain", reason=f"request failed: {exc}")

    if resp.status_code in (404, 410):
        return LivenessResult(status="expired", reason=f"HTTP {resp.status_code}")

    body = resp.text

    for pattern in _EXPIRED_PATTERNS:
        if pattern.search(body):
            return LivenessResult(status="expired", reason=f"matched: {pattern.pattern}")

    for pattern in _LISTING_PAGE_PATTERNS:
        if pattern.search(body):
            return LivenessResult(status="expired", reason="redirected to listing page")

    if len(body.strip()) < _MIN_CONTENT_CHARS:
        return LivenessResult(status="expired", reason="insufficient page content")

    for pattern in _APPLY_PATTERNS:
        if pattern.search(body):
            return LivenessResult(status="active", reason="apply control detected")

    return LivenessResult(status="uncertain", reason="content present but no apply control found")
