"""Typed domain models used by Vela."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PortfolioPosition:
    asset_type: str
    ticker: str
    name: str
    quantity: Decimal
    currency: str
    cost_basis: Decimal
    market_value: Decimal
    role: str
    notes: str = ""


@dataclass(frozen=True)
class WatchlistItem:
    ticker: str
    name: str
    asset_type: str
    benchmark: str
    reason: str
    max_portfolio_weight: Decimal
    default_label: str


@dataclass(frozen=True)
class Scorecard:
    business_quality: int
    financial_strength: int
    valuation_attractiveness: int
    growth_durability: int
    downside_risk: int
    portfolio_fit: int
    vwce_alternative_test: bool
    final_label: str

    @property
    def total(self) -> int:
        return (
            self.business_quality
            + self.financial_strength
            + self.valuation_attractiveness
            + self.growth_durability
            + self.downside_risk
            + self.portfolio_fit
        )

    @property
    def max_total(self) -> int:
        return 60
