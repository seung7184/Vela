from datetime import date

from vela.constants import DISCLAIMER
from vela.generate_report import (
    generate_ticker_report,
    generate_weekly_review,
    ticker_report_markdown,
    weekly_review_markdown,
)
from vela.snapshots import write_snapshot


def _write_inputs(tmp_path):
    portfolio = tmp_path / "portfolio.csv"
    portfolio.write_text(
        "asset_type,ticker,name,quantity,currency,cost_basis,market_value,role,notes\n"
        "ETF,VWCE,Vanguard,1,EUR,100,110,core,main\n",
        encoding="utf-8",
    )
    watchlist = tmp_path / "watchlist.csv"
    watchlist.write_text(
        "ticker,name,asset_type,benchmark,reason,max_portfolio_weight,default_label\n"
        "NVDA,NVIDIA,Stock,VWCE,AI study,0.05,Study more\n",
        encoding="utf-8",
    )
    return portfolio, watchlist


def _snapshot(snapshot_id: str = "ticker-nvda-2026-06-14", snapshot_date: str = "2026-06-14") -> dict:
    return {
        "snapshot_id": snapshot_id,
        "snapshot_date": snapshot_date,
        "source": "manual",
        "created_at": f"{snapshot_date}T20:00:00Z",
        "description": "Safe cached research snapshot.",
        "data": {
            "ticker": "NVDA",
            "benchmark": "VWCE",
            "manual_price": {"ticker": "NVDA", "price": None, "currency": None, "provider": "manual"},
            "research_questions": ["What would make NVDA better than VWCE?"],
            "vwce_alternative_test": {"status": "fail", "default_answer": "No - prove otherwise before acting."},
        },
        "notes": ["Educational use only. Not financial advice."],
    }


def test_ticker_report_contains_required_sections():
    report = ticker_report_markdown("NVDA", report_date=date(2026, 6, 14))

    assert DISCLAIMER in report
    assert "## Bull case" in report
    assert "## Bear case" in report
    assert "## VWCE alternative test" in report
    assert "## What would change my mind" in report


def test_ticker_report_omits_snapshot_context_without_snapshot():
    report = ticker_report_markdown("NVDA", report_date=date(2026, 6, 14))

    assert "## Snapshot context" not in report
    assert "## Snapshot data highlights" not in report


def test_ticker_report_includes_snapshot_context_when_snapshot_is_provided():
    report = ticker_report_markdown("NVDA", snapshot=_snapshot(), report_date=date(2026, 6, 14))

    assert DISCLAIMER in report
    assert "## Snapshot context" in report
    assert "## Snapshot data highlights" in report
    assert "This is cached local context only. No network calls were made." in report
    assert "manual placeholder, not live market data" in report
    assert "## Bull case" in report
    assert "## Bear case" in report
    assert "## Key risks" in report
    assert "## Downside scenario" in report
    assert "## What would change my mind" in report
    assert "## VWCE alternative test" in report
    assert "## Scorecard" in report


def test_generate_ticker_report_writes_file(tmp_path):
    _, watchlist = _write_inputs(tmp_path)
    output_dir = tmp_path / "reports" / "ticker"

    output = generate_ticker_report(
        "NVDA",
        watchlist_path=watchlist,
        output_dir=output_dir,
        report_date=date(2026, 6, 14),
    )

    assert output.exists()
    assert output.name == "NVDA_2026-06-14.md"
    assert "NVIDIA" in output.read_text(encoding="utf-8")


def test_generate_ticker_report_loads_snapshot_by_id(tmp_path):
    _, watchlist = _write_inputs(tmp_path)
    snapshot_dir = tmp_path / "snapshots"
    write_snapshot(_snapshot(), snapshot_dir / "nvda.json")
    output_dir = tmp_path / "reports" / "ticker"

    output = generate_ticker_report(
        "NVDA",
        watchlist_path=watchlist,
        output_dir=output_dir,
        report_date=date(2026, 6, 14),
        snapshot_id="ticker-nvda-2026-06-14",
        snapshot_dir=snapshot_dir,
    )

    text = output.read_text(encoding="utf-8")
    assert "## Snapshot context" in text
    assert "- snapshot_id: ticker-nvda-2026-06-14" in text


def test_generate_ticker_report_includes_stale_snapshot_warning(tmp_path):
    _, watchlist = _write_inputs(tmp_path)
    snapshot_dir = tmp_path / "snapshots"
    write_snapshot(_snapshot(snapshot_date="2026-04-01"), snapshot_dir / "old.json")
    output_dir = tmp_path / "reports" / "ticker"

    output = generate_ticker_report(
        "NVDA",
        watchlist_path=watchlist,
        output_dir=output_dir,
        report_date=date(2026, 6, 14),
        snapshot_id="ticker-nvda-2026-06-14",
        snapshot_dir=snapshot_dir,
    )

    assert "Warning: this cached snapshot is older than 30 days" in output.read_text(encoding="utf-8")


def test_weekly_review_omits_snapshot_context_without_snapshot(tmp_path):
    portfolio, watchlist = _write_inputs(tmp_path)

    report = weekly_review_markdown(portfolio_path=portfolio, watchlist_path=watchlist, report_date=date(2026, 6, 14))

    assert "## Snapshot context" not in report
    assert "## Snapshot data highlights" not in report


def test_weekly_review_includes_snapshot_context_when_snapshot_is_provided(tmp_path):
    portfolio, watchlist = _write_inputs(tmp_path)
    snapshot = _snapshot("weekly-2026-06-14")
    snapshot["data"] = {
        "macro": [{"name": "Rates and inflation", "observation": "Placeholder macro note.", "source": "manual"}],
        "portfolio": {"base_currency": "EUR", "core_benchmark": "VWCE", "review_mode": "education-only"},
        "prices": [{"ticker": "VWCE", "price": None, "currency": None, "provider": "manual"}],
    }

    report = weekly_review_markdown(
        portfolio_path=portfolio,
        watchlist_path=watchlist,
        snapshot=snapshot,
        report_date=date(2026, 6, 14),
    )

    assert DISCLAIMER in report
    assert "## Snapshot context" in report
    assert "## Snapshot data highlights" in report
    assert "Macro: Rates and inflation - Placeholder macro note. (source: manual)" in report
    assert "Portfolio context: base_currency=EUR, core_benchmark=VWCE, review_mode=education-only" in report
    assert "Price context: VWCE price is a manual placeholder, not live market data." in report
    assert "## ETF core assessment" in report


def test_generate_weekly_review_writes_file(tmp_path):
    portfolio, watchlist = _write_inputs(tmp_path)
    output_dir = tmp_path / "reports" / "weekly"

    output = generate_weekly_review(
        portfolio_path=portfolio,
        watchlist_path=watchlist,
        output_dir=output_dir,
        report_date=date(2026, 6, 14),
    )

    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert DISCLAIMER in text
    assert "ETF core assessment" in text


def test_generate_weekly_review_loads_snapshot_by_id(tmp_path):
    portfolio, watchlist = _write_inputs(tmp_path)
    snapshot_dir = tmp_path / "snapshots"
    write_snapshot(_snapshot("weekly-2026-06-14"), snapshot_dir / "weekly.json")
    output_dir = tmp_path / "reports" / "weekly"

    output = generate_weekly_review(
        portfolio_path=portfolio,
        watchlist_path=watchlist,
        output_dir=output_dir,
        report_date=date(2026, 6, 14),
        snapshot_id="weekly-2026-06-14",
        snapshot_dir=snapshot_dir,
    )

    text = output.read_text(encoding="utf-8")
    assert "## Snapshot context" in text
    assert "- snapshot_id: weekly-2026-06-14" in text
