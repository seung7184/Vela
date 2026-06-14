from decimal import Decimal

import pytest

from vela.load_portfolio import load_portfolio, portfolio_total_market_value
from vela.load_watchlist import find_watchlist_item, load_watchlist


def test_load_portfolio_reads_positions(tmp_path):
    path = tmp_path / "portfolio.csv"
    path.write_text(
        "asset_type,ticker,name,quantity,currency,cost_basis,market_value,role,notes\n"
        "ETF,VWCE,Vanguard,2.5,EUR,250,300,core,main\n",
        encoding="utf-8",
    )

    positions = load_portfolio(path)

    assert len(positions) == 1
    assert positions[0].ticker == "VWCE"
    assert positions[0].quantity == Decimal("2.5")
    assert portfolio_total_market_value(positions) == Decimal("300")


def test_load_portfolio_fails_on_missing_columns(tmp_path):
    path = tmp_path / "portfolio.csv"
    path.write_text("ticker,name\nVWCE,Vanguard\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing columns"):
        load_portfolio(path)


def test_load_watchlist_validates_label_and_finds_item(tmp_path):
    path = tmp_path / "watchlist.csv"
    path.write_text(
        "ticker,name,asset_type,benchmark,reason,max_portfolio_weight,default_label\n"
        "NVDA,NVIDIA,Stock,VWCE,AI study,0.05,Study more\n",
        encoding="utf-8",
    )

    items = load_watchlist(path)

    assert len(items) == 1
    assert find_watchlist_item(items, "nvda") is items[0]
    assert items[0].max_portfolio_weight == Decimal("0.05")


def test_load_watchlist_rejects_invalid_weight(tmp_path):
    path = tmp_path / "watchlist.csv"
    path.write_text(
        "ticker,name,asset_type,benchmark,reason,max_portfolio_weight,default_label\n"
        "NVDA,NVIDIA,Stock,VWCE,AI study,2.00,Study more\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="between 0 and 1"):
        load_watchlist(path)
