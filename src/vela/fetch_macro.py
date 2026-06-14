"""FRED macro data helpers."""

from __future__ import annotations

import json
import os
from urllib.parse import urlencode
from urllib.request import urlopen

FRED_BASE_URL = "https://api.stlouisfed.org/fred"


def fred_api_key(api_key: str | None = None) -> str:
    value = api_key or os.environ.get("FRED_API_KEY", "")
    if not value.strip():
        raise ValueError("FRED_API_KEY is required for FRED network requests")
    return value.strip()


def fred_observations_url(series_id: str, *, api_key: str, file_type: str = "json") -> str:
    if not series_id.strip():
        raise ValueError("series_id is required")
    query = urlencode(
        {
            "series_id": series_id.strip().upper(),
            "api_key": fred_api_key(api_key),
            "file_type": file_type,
        }
    )
    return f"{FRED_BASE_URL}/series/observations?{query}"


def fetch_fred_observations(series_id: str, *, api_key: str, timeout: float = 20.0) -> dict:
    url = fred_observations_url(series_id, api_key=api_key)
    with urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))
