from pathlib import Path

from vela.cli import main


def _write_inputs(root: Path) -> None:
    (root / "portfolio.csv").write_text(
        "asset_type,ticker,name,quantity,currency,cost_basis,market_value,role,notes\n"
        "ETF,VWCE,Vanguard,1,EUR,100,110,core,main\n",
        encoding="utf-8",
    )
    (root / "watchlist.csv").write_text(
        "ticker,name,asset_type,benchmark,reason,max_portfolio_weight,default_label\n"
        "NVDA,NVIDIA,Stock,VWCE,AI study,0.05,Study more\n",
        encoding="utf-8",
    )


def test_cli_doctor(tmp_path, monkeypatch, capsys):
    _write_inputs(tmp_path)
    monkeypatch.chdir(tmp_path)

    exit_code = main(["doctor"])

    assert exit_code == 0
    assert "live trading: disabled" in capsys.readouterr().out


def test_cli_generates_ticker_and_weekly_reports(tmp_path, monkeypatch):
    _write_inputs(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert main(["ticker", "NVDA", "--output-dir", "reports/ticker"]) == 0
    assert main(["weekly", "--output-dir", "reports/weekly"]) == 0

    assert list((tmp_path / "reports" / "ticker").glob("NVDA_*.md"))
    assert list((tmp_path / "reports" / "weekly").glob("*_weekly_review.md"))
