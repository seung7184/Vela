"""Portfolio CSV loader."""

from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

from vela.models import PortfolioPosition

REQUIRED_COLUMNS = {
    "asset_type",
    "ticker",
    "name",
    "quantity",
    "currency",
    "cost_basis",
    "market_value",
    "role",
}


def _decimal(value: str, *, field: str, row_number: int) -> Decimal:
    try:
        return Decimal(value or "0")
    except InvalidOperation as exc:
        raise ValueError(f"Invalid decimal in row {row_number}, field '{field}': {value!r}") from exc


def load_portfolio(path: str | Path = "portfolio.csv") -> list[PortfolioPosition]:
    """Load portfolio positions from a CSV file."""

    file_path = Path(path)
    with file_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Portfolio CSV is empty")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Portfolio CSV is missing columns: {sorted(missing)}")

        positions: list[PortfolioPosition] = []
        for row_number, row in enumerate(reader, start=2):
            positions.append(
                PortfolioPosition(
                    asset_type=(row["asset_type"] or "").strip(),
                    ticker=(row["ticker"] or "").strip().upper(),
                    name=(row["name"] or "").strip(),
                    quantity=_decimal(row["quantity"], field="quantity", row_number=row_number),
                    currency=(row["currency"] or "").strip().upper(),
                    cost_basis=_decimal(row["cost_basis"], field="cost_basis", row_number=row_number),
                    market_value=_decimal(row["market_value"], field="market_value", row_number=row_number),
                    role=(row["role"] or "").strip(),
                    notes=(row.get("notes") or "").strip(),
                )
            )
    return positions


def portfolio_total_market_value(positions: list[PortfolioPosition]) -> Decimal:
    """Return total market value across loaded positions."""

    return sum((position.market_value for position in positions), Decimal("0"))
