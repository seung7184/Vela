import json
from datetime import date
from pathlib import Path

import pytest

from vela.constants import DISCLAIMER
from vela.context_pack import (
    build_ticker_context_pack,
    build_weekly_context_pack,
    read_csv_as_markdown,
    weekly_context_pack_filename,
    write_context_pack,
)


def _write_inputs(root: Path) -> None:
    (root / "memory").mkdir()
    (root / "memory" / "investment_policy.md").write_text(
        "# Investment Policy\n\nETF core first.\n\nEducational use only. Not financial advice.\n",
        encoding="utf-8",
    )
    (root / "memory" / "portfolio_rules.md").write_text(
        "# Portfolio Rules\n\nCompare every stock with VWCE.\n",
        encoding="utf-8",
    )
    (root / "memory" / "thesis_log.md").write_text(
        "# Thesis Log\n\nTicker ideas must define what would change my mind.\n",
        encoding="utf-8",
    )
    (root / "memory" / "watchlist_reasoning.md").write_text(
        "# Watchlist Reasoning\n\nNVDA is an AI growth study case.\n",
        encoding="utf-8",
    )
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


def _write_snapshot(root: Path, snapshot_id: str = "ticker-nvda-2026-06-14") -> Path:
    snapshot_dir = root / "data" / "processed" / "snapshots"
    snapshot_dir.mkdir(parents=True)
    (snapshot_dir / "snapshot.json").write_text(
        json.dumps(
            {
                "snapshot_id": snapshot_id,
                "snapshot_date": "2026-06-14",
                "source": "manual",
                "created_at": "2026-06-14T20:00:00Z",
                "description": "Safe cached research snapshot.",
                "data": {
                    "ticker": "NVDA",
                    "benchmark": "VWCE",
                    "manual_price": {"ticker": "NVDA", "price": None, "currency": None, "provider": "manual"},
                    "research_questions": ["What would make NVDA better than VWCE?"],
                },
                "notes": ["Educational use only. Not financial advice."],
            }
        ),
        encoding="utf-8",
    )
    return snapshot_dir


def test_read_csv_as_markdown_renders_limited_rows(tmp_path):
    csv_path = tmp_path / "items.csv"
    csv_path.write_text("ticker,name\nNVDA,NVIDIA\nVWCE,Vanguard\nTSLA,Tesla\n", encoding="utf-8")

    table = read_csv_as_markdown(csv_path, max_rows=2)

    assert table == (
        "| ticker | name |\n"
        "| --- | --- |\n"
        "| NVDA | NVIDIA |\n"
        "| VWCE | Vanguard |\n"
        "\n_Showing 2 of 3 rows._"
    )


def test_weekly_context_pack_filename_uses_date_explicitly():
    assert weekly_context_pack_filename(date(2026, 6, 15)) == "2026-06-15_weekly_context_pack.md"


def test_ticker_context_pack_contains_policy_csv_disclaimer_and_prompt(tmp_path, monkeypatch):
    _write_inputs(tmp_path)
    monkeypatch.chdir(tmp_path)

    pack = build_ticker_context_pack("NVDA", today=date(2026, 6, 15))

    assert "# Vela Ticker Context Pack - NVDA" in pack
    assert DISCLAIMER in pack
    assert "## Investment policy" in pack
    assert "ETF core first." in pack
    assert "| ticker | name |" in pack
    assert "## Manual AI prompt scaffold" in pack
    assert "Analyze NVDA using only this context pack" in pack
    assert "VWCE alternative test" in pack


def test_weekly_context_pack_contains_policy_csv_disclaimer_and_prompt(tmp_path, monkeypatch):
    _write_inputs(tmp_path)
    monkeypatch.chdir(tmp_path)

    pack = build_weekly_context_pack(today=date(2026, 6, 15))

    assert "# Vela Weekly Context Pack - 2026-06-15" in pack
    assert DISCLAIMER in pack
    assert "## Portfolio rules" in pack
    assert "Compare every stock with VWCE." in pack
    assert "| ticker | name | asset_type | benchmark | reason | max_portfolio_weight | default_label |" in pack
    assert "## Manual AI prompt scaffold" in pack
    assert "weekly market review" in pack
    assert "next week's study plan" in pack


def test_context_pack_with_snapshot_includes_context_and_highlights(tmp_path, monkeypatch):
    _write_inputs(tmp_path)
    snapshot_dir = _write_snapshot(tmp_path)
    monkeypatch.chdir(tmp_path)

    pack = build_ticker_context_pack(
        "NVDA",
        snapshot_id="ticker-nvda-2026-06-14",
        snapshot_dir=snapshot_dir,
        today=date(2026, 6, 15),
    )

    assert "## Snapshot context" in pack
    assert "- snapshot_id: ticker-nvda-2026-06-14" in pack
    assert "## Snapshot data highlights" in pack
    assert "manual placeholder, not live market data" in pack


def test_context_pack_without_snapshot_includes_no_snapshot_note(tmp_path, monkeypatch):
    _write_inputs(tmp_path)
    monkeypatch.chdir(tmp_path)

    pack = build_ticker_context_pack("NVDA", today=date(2026, 6, 15))

    assert "No snapshot selected" in pack


def test_missing_snapshot_id_fails_clearly(tmp_path, monkeypatch):
    _write_inputs(tmp_path)
    _write_snapshot(tmp_path)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="Snapshot not found: missing-snapshot"):
        build_ticker_context_pack("NVDA", snapshot_id="missing-snapshot", today=date(2026, 6, 15))


def test_write_context_pack_writes_markdown(tmp_path):
    output = write_context_pack("hello\n", tmp_path / "reports" / "context" / "pack.md")

    assert output == tmp_path / "reports" / "context" / "pack.md"
    assert output.read_text(encoding="utf-8") == "hello\n"
