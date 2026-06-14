"""Ticker scorecard logic."""

from __future__ import annotations

from vela.constants import ALLOWED_LABELS
from vela.models import Scorecard


def _validate_score(value: int, field: str) -> int:
    if not isinstance(value, int):
        raise TypeError(f"{field} must be an integer")
    if value < 0 or value > 10:
        raise ValueError(f"{field} must be between 0 and 10")
    return value


def suggest_label(total: int, *, vwce_alternative_test: bool) -> str:
    """Suggest a conservative label from score and ETF benchmark pass/fail."""

    if not vwce_alternative_test:
        return "ETF-only is better"
    if total >= 48:
        return "Small position candidate"
    if total >= 38:
        return "Watchlist"
    if total >= 28:
        return "Study more"
    return "Avoid"


def build_scorecard(
    *,
    business_quality: int,
    financial_strength: int,
    valuation_attractiveness: int,
    growth_durability: int,
    downside_risk: int,
    portfolio_fit: int,
    vwce_alternative_test: bool,
    final_label: str | None = None,
) -> Scorecard:
    """Build and validate a ticker scorecard."""

    values = {
        "business_quality": _validate_score(business_quality, "business_quality"),
        "financial_strength": _validate_score(financial_strength, "financial_strength"),
        "valuation_attractiveness": _validate_score(valuation_attractiveness, "valuation_attractiveness"),
        "growth_durability": _validate_score(growth_durability, "growth_durability"),
        "downside_risk": _validate_score(downside_risk, "downside_risk"),
        "portfolio_fit": _validate_score(portfolio_fit, "portfolio_fit"),
    }
    total = sum(values.values())
    label = final_label or suggest_label(total, vwce_alternative_test=vwce_alternative_test)
    if label not in ALLOWED_LABELS:
        raise ValueError(f"Invalid final label: {label!r}")
    if not vwce_alternative_test and label == "Small position candidate":
        raise ValueError("A failed VWCE alternative test cannot be a small position candidate")
    return Scorecard(**values, vwce_alternative_test=vwce_alternative_test, final_label=label)


def scorecard_to_markdown(scorecard: Scorecard) -> str:
    """Render a scorecard as Markdown."""

    rows = [
        ("Business quality", scorecard.business_quality),
        ("Financial strength", scorecard.financial_strength),
        ("Valuation attractiveness", scorecard.valuation_attractiveness),
        ("Growth durability", scorecard.growth_durability),
        ("Downside risk", scorecard.downside_risk),
        ("Portfolio fit", scorecard.portfolio_fit),
    ]
    lines = ["| Factor | Score |", "|---|---:|"]
    lines.extend(f"| {name} | {value}/10 |" for name, value in rows)
    lines.append(f"| **Total** | **{scorecard.total}/{scorecard.max_total}** |")
    lines.append("")
    lines.append(f"VWCE alternative test: {'pass' if scorecard.vwce_alternative_test else 'fail'}")
    lines.append(f"Final label: **{scorecard.final_label}**")
    return "\n".join(lines)
