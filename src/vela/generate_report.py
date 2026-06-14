"""Markdown report generation for Vela."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from vela.constants import DEFAULT_BENCHMARK, DISCLAIMER
from vela.load_portfolio import load_portfolio, portfolio_total_market_value
from vela.load_watchlist import find_watchlist_item, load_watchlist
from vela.models import Scorecard, WatchlistItem
from vela.score_ticker import build_scorecard, scorecard_to_markdown


def ticker_report_markdown(
    ticker: str,
    *,
    item: WatchlistItem | None = None,
    scorecard: Scorecard | None = None,
    report_date: date | None = None,
) -> str:
    """Create a repeatable ticker research template."""

    normalized = ticker.upper()
    today = report_date or date.today()
    item_name = item.name if item else normalized
    benchmark = item.benchmark if item else DEFAULT_BENCHMARK
    reason = item.reason if item else "Manual research idea."
    label = item.default_label if item else "Study more"
    scorecard = scorecard or build_scorecard(
        business_quality=5,
        financial_strength=5,
        valuation_attractiveness=5,
        growth_durability=5,
        downside_risk=5,
        portfolio_fit=5,
        vwce_alternative_test=False,
        final_label="ETF-only is better" if label != "Avoid" else "Avoid",
    )

    return f"""# {normalized} Research Report — {today.isoformat()}

{DISCLAIMER}

## Summary

- Name: {item_name}
- Asset type: {item.asset_type if item else "Unknown"}
- Benchmark: {benchmark}
- Watchlist reason: {reason}
- Starting label: {label}

## Business model

TODO: Explain how the company or fund creates value.

## Revenue drivers

TODO: Identify the main revenue or return drivers.

## Recent financial trend

TODO: Summarize revenue, margin, cash flow, leverage, and capital allocation trends.

## Valuation snapshot

TODO: Compare valuation against history, peers, and growth expectations.

## Bull case

TODO: Write the strongest reasonable positive case.

## Bear case

TODO: Write the strongest reasonable negative case.

## Key risks

- Valuation risk
- Concentration risk
- Macro or rates risk
- Thesis drift risk

## Downside scenario

TODO: Describe what could go wrong and what portfolio loss would be acceptable.

## What would change my mind

TODO: Define measurable evidence that would upgrade, downgrade, or invalidate the thesis.

## VWCE alternative test

Would buying {normalized} improve the portfolio more than simply adding to {benchmark}?

Current default answer: **No — prove otherwise before acting.**

## Scorecard

{scorecard_to_markdown(scorecard)}

## Next study questions

1. What data would make the bull case stronger?
2. What data would make the bear case stronger?
3. Is this idea already mostly captured by the ETF core?
"""


def generate_ticker_report(
    ticker: str,
    *,
    watchlist_path: str | Path = "watchlist.csv",
    output_dir: str | Path = "reports/ticker",
    report_date: date | None = None,
) -> Path:
    items = load_watchlist(watchlist_path)
    item = find_watchlist_item(items, ticker)
    today = report_date or date.today()
    output_path = Path(output_dir) / f"{ticker.upper()}_{today.isoformat()}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(ticker_report_markdown(ticker, item=item, report_date=today), encoding="utf-8")
    return output_path


def weekly_review_markdown(
    *,
    portfolio_path: str | Path = "portfolio.csv",
    watchlist_path: str | Path = "watchlist.csv",
    report_date: date | None = None,
) -> str:
    today = report_date or date.today()
    positions = load_portfolio(portfolio_path)
    watchlist = load_watchlist(watchlist_path)
    total_value = portfolio_total_market_value(positions)
    tickers = ", ".join(item.ticker for item in watchlist)

    return f"""# Weekly Portfolio Review — {today.isoformat()}

{DISCLAIMER}

## Portfolio snapshot

- Positions loaded: {len(positions)}
- Total market value from CSV: {total_value}
- Watchlist tickers: {tickers}

## What changed this week

TODO: Summarize material market, macro, and watchlist changes.

## ETF core assessment

TODO: Check whether the ETF core still matches the investment policy.

## Individual stock ideas worth studying

TODO: List ideas that deserve more research, not immediate action.

## Ideas rejected and why

TODO: Record ideas that failed the VWCE alternative test.

## Mistakes or emotional decisions to avoid

TODO: Update `memory/mistakes_log.md` if needed.

## Next week's study plan

1. Review one ETF core assumption.
2. Deep-dive one watchlist idea.
3. Learn one investing concept.
"""


def generate_weekly_review(
    *,
    portfolio_path: str | Path = "portfolio.csv",
    watchlist_path: str | Path = "watchlist.csv",
    output_dir: str | Path = "reports/weekly",
    report_date: date | None = None,
) -> Path:
    today = report_date or date.today()
    output_path = Path(output_dir) / f"{today.isoformat()}_weekly_review.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        weekly_review_markdown(portfolio_path=portfolio_path, watchlist_path=watchlist_path, report_date=today),
        encoding="utf-8",
    )
    return output_path
