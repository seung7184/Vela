from datetime import date

from vela.constants import DISCLAIMER
from vela.generate_report import generate_ticker_report, generate_weekly_review, ticker_report_markdown


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


def test_ticker_report_contains_required_sections():
    report = ticker_report_markdown("NVDA", report_date=date(2026, 6, 14))

    assert DISCLAIMER in report
    assert "## Bull case" in report
    assert "## Bear case" in report
    assert "## VWCE alternative test" in report
    assert "## What would change my mind" in report


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
