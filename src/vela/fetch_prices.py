"""Price data helpers for Phase 0.

The default provider is manual. Phase 0 does not require network access.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class PriceSnapshot:
    ticker: str
    price: float | None
    currency: str | None
    as_of: str
    provider: str
    note: str = ""


def manual_price_snapshot(ticker: str, note: str = "Manual placeholder; no network call made.") -> PriceSnapshot:
    """Return a placeholder snapshot for report scaffolding."""

    return PriceSnapshot(
        ticker=ticker.upper(),
        price=None,
        currency=None,
        as_of=datetime.now(UTC).isoformat(),
        provider="manual",
        note=note,
    )
