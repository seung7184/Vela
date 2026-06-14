"""Watchlist CSV loader."""

from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from vela.constants import ALLOWED_LABELS
from vela.models import WatchlistItem

REQUIRED_COLUMNS = {
    "ticker",
    "name",
    "asset_type",
    "benchmark",
    "reason",
    "max_portfolio_weight",
    "default_label",
}


def _weight(value: str, *, row_number: int) -> Decimal:
    try:
        weight = Decimal(value or "0")
    except InvalidOperation as exc:
        raise ValueError(f"Invalid max_portfolio_weight in row {row_number}: {value!r}") from exc
    if weight < 0 or weight > 1:
        raise ValueError(f"max_portfolio_weight must be between 0 and 1 in row {row_number}")
    return weight


def load_watchlist(path: str | Path = "watchlist.csv") -> list[WatchlistItem]:
    """Load watchlist items from a CSV file."""

    file_path = Path(path)
    with file_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Watchlist CSV is empty")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Watchlist CSV is missing columns: {sorted(missing)}")

        items: list[WatchlistItem] = []
        for row_number, row in enumerate(reader, start=2):
            label = (row["default_label"] or "").strip()
            if label not in ALLOWED_LABELS:
                raise ValueError(f"Invalid default_label in row {row_number}: {label!r}")
            items.append(
                WatchlistItem(
                    ticker=(row["ticker"] or "").strip().upper(),
                    name=(row["name"] or "").strip(),
                    asset_type=(row["asset_type"] or "").strip(),
                    benchmark=(row["benchmark"] or "").strip().upper(),
                    reason=(row["reason"] or "").strip(),
                    max_portfolio_weight=_weight(row["max_portfolio_weight"], row_number=row_number),
                    default_label=label,
                )
            )
    return items


def find_watchlist_item(items: list[WatchlistItem], ticker: str) -> WatchlistItem | None:
    """Find a watchlist item by ticker."""

    normalized = ticker.upper()
    return next((item for item in items if item.ticker == normalized), None)
