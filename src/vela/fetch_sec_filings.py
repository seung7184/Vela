"""SEC EDGAR data helpers."""

from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen

SEC_SUBMISSIONS_BASE_URL = "https://data.sec.gov/submissions"
SEC_COMPANY_FACTS_BASE_URL = "https://data.sec.gov/api/xbrl/companyfacts"


def normalize_cik(cik: str | int) -> str:
    """Return a SEC CIK as a zero-padded 10-character string."""

    digits = str(cik).strip().lstrip("0") or "0"
    if not digits.isdigit():
        raise ValueError(f"CIK must contain only digits: {cik!r}")
    if len(digits) > 10:
        raise ValueError(f"CIK is too long: {cik!r}")
    return digits.zfill(10)


def submissions_url(cik: str | int) -> str:
    return f"{SEC_SUBMISSIONS_BASE_URL}/CIK{normalize_cik(cik)}.json"


def company_facts_url(cik: str | int) -> str:
    return f"{SEC_COMPANY_FACTS_BASE_URL}/CIK{normalize_cik(cik)}.json"


def sec_user_agent(user_agent: str | None = None) -> str:
    """Return an explicit SEC user agent for network requests."""

    value = user_agent or os.environ.get("SEC_USER_AGENT", "")
    if not value.strip():
        raise ValueError("SEC_USER_AGENT is required for SEC network requests")
    return value.strip()


def fetch_json(url: str, *, user_agent: str, timeout: float = 20.0) -> dict:
    """Fetch JSON from SEC with an explicit user agent."""

    request = Request(url, headers={"User-Agent": sec_user_agent(user_agent)})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_submissions(cik: str | int, *, user_agent: str, timeout: float = 20.0) -> dict:
    return fetch_json(submissions_url(cik), user_agent=user_agent, timeout=timeout)


def fetch_company_facts(cik: str | int, *, user_agent: str, timeout: float = 20.0) -> dict:
    return fetch_json(company_facts_url(cik), user_agent=user_agent, timeout=timeout)
