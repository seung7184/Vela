import json
from datetime import date

import pytest

from vela.snapshots import (
    SnapshotNotFoundError,
    SnapshotValidationError,
    find_snapshot_by_id,
    load_snapshot,
    load_snapshots,
    render_snapshot_summary,
    snapshot_age_days,
    snapshot_context_markdown,
    snapshot_data_highlights_markdown,
    snapshot_staleness_warning,
    write_snapshot,
)


def _snapshot(snapshot_id: str = "weekly-2026-06-14") -> dict:
    return {
        "snapshot_id": snapshot_id,
        "snapshot_date": "2026-06-14",
        "source": "manual",
        "created_at": "2026-06-14T20:00:00Z",
        "description": "Safe cached research snapshot.",
        "data": {"prices": [{"ticker": "VWCE", "price": None, "provider": "manual"}]},
        "notes": ["Educational use only. Not financial advice."],
    }


def test_load_snapshot_reads_valid_snapshot(tmp_path):
    snapshot_path = tmp_path / "weekly.json"
    snapshot_path.write_text(json.dumps(_snapshot()), encoding="utf-8")

    loaded = load_snapshot(snapshot_path)

    assert loaded["snapshot_id"] == "weekly-2026-06-14"
    assert loaded["data"]["prices"][0]["ticker"] == "VWCE"


def test_load_snapshot_raises_for_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_snapshot(tmp_path / "missing.json")


def test_load_snapshot_raises_for_invalid_json(tmp_path):
    snapshot_path = tmp_path / "broken.json"
    snapshot_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="Invalid JSON"):
        load_snapshot(snapshot_path)


def test_load_snapshot_raises_for_missing_required_field(tmp_path):
    snapshot = _snapshot()
    del snapshot["snapshot_date"]
    snapshot_path = tmp_path / "missing-field.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="snapshot_date"):
        load_snapshot(snapshot_path)


def test_load_snapshot_blocks_path_traversal(tmp_path):
    root = tmp_path / "snapshots"
    root.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps(_snapshot()), encoding="utf-8")

    with pytest.raises(ValueError, match="parent path segments"):
        load_snapshot("../outside.json", snapshot_dir=root)


def test_load_snapshot_blocks_parent_segments_without_snapshot_dir():
    with pytest.raises(ValueError, match="parent path segments"):
        load_snapshot("../outside.json")


def test_write_snapshot_validates_and_writes_json(tmp_path):
    output = write_snapshot(_snapshot("ticker-nvda-2026-06-14"), tmp_path / "nvda.json")

    loaded = load_snapshot(output)

    assert loaded["snapshot_id"] == "ticker-nvda-2026-06-14"
    assert output.read_text(encoding="utf-8").endswith("\n")


def test_load_snapshots_reads_json_files_in_order(tmp_path):
    write_snapshot(_snapshot("b-weekly"), tmp_path / "b.json")
    write_snapshot(_snapshot("a-weekly"), tmp_path / "a.json")
    (tmp_path / "README.md").write_text("ignored", encoding="utf-8")

    loaded = load_snapshots(tmp_path)

    assert [item["snapshot_id"] for item in loaded] == ["a-weekly", "b-weekly"]


def test_find_snapshot_by_id_returns_matching_snapshot(tmp_path):
    write_snapshot(_snapshot("weekly-2026-06-14"), tmp_path / "weekly.json")
    write_snapshot(_snapshot("ticker-nvda-2026-06-14"), tmp_path / "ticker.json")

    found = find_snapshot_by_id("ticker-nvda-2026-06-14", snapshot_dir=tmp_path)

    assert found["snapshot_id"] == "ticker-nvda-2026-06-14"


def test_find_snapshot_by_id_raises_when_missing(tmp_path):
    write_snapshot(_snapshot("weekly-2026-06-14"), tmp_path / "weekly.json")

    with pytest.raises(SnapshotNotFoundError, match="missing-snapshot"):
        find_snapshot_by_id("missing-snapshot", snapshot_dir=tmp_path)


def test_find_snapshot_by_id_fails_fast_for_duplicate_ids(tmp_path):
    write_snapshot(_snapshot("duplicate-id"), tmp_path / "a.json")
    write_snapshot(_snapshot("duplicate-id"), tmp_path / "b.json")

    with pytest.raises(SnapshotValidationError, match="Duplicate snapshot_id"):
        find_snapshot_by_id("duplicate-id", snapshot_dir=tmp_path)


def test_snapshot_staleness_warning_for_old_snapshot():
    snapshot = _snapshot()
    snapshot["snapshot_date"] = "2026-05-01"

    warning = snapshot_staleness_warning(snapshot, today=date(2026, 6, 14), stale_after_days=30)

    assert warning == "Warning: this cached snapshot is older than 30 days. Refresh before using it for current research."


def test_snapshot_staleness_warning_empty_for_fresh_snapshot():
    snapshot = _snapshot()

    assert snapshot_staleness_warning(snapshot, today=date(2026, 6, 14), stale_after_days=30) == ""


def test_snapshot_age_days_raises_for_malformed_snapshot_date():
    snapshot = _snapshot()
    snapshot["snapshot_date"] = "June 14, 2026"

    with pytest.raises(SnapshotValidationError, match="snapshot_date"):
        snapshot_age_days(snapshot, today=date(2026, 6, 14))


def test_snapshot_context_markdown_contains_no_network_language():
    context = snapshot_context_markdown(_snapshot(), today=date(2026, 6, 14))

    assert "## Snapshot context" in context
    assert "- snapshot_id: weekly-2026-06-14" in context
    assert "- age_days: 0" in context
    assert "This is cached local context only. No network calls were made." in context
    assert "Educational use only. Not financial advice." in context


def test_snapshot_data_highlights_markdown_is_conservative_and_avoids_raw_dump():
    snapshot = _snapshot("ticker-nvda-2026-06-14")
    snapshot["data"] = {
        "ticker": "NVDA",
        "benchmark": "VWCE",
        "manual_price": {"ticker": "NVDA", "price": None, "currency": None, "provider": "manual"},
        "research_questions": ["What would make NVDA better than VWCE?"],
        "vwce_alternative_test": {"status": "fail", "default_answer": "No - prove otherwise before acting."},
        "large_unsafe_blob": {"nested": ["raw"] * 200},
    }

    highlights = snapshot_data_highlights_markdown(snapshot)

    assert "## Snapshot data highlights" in highlights
    assert "Ticker: NVDA" in highlights
    assert "Benchmark: VWCE" in highlights
    assert "manual placeholder, not live market data" in highlights
    assert "What would make NVDA better than VWCE?" in highlights
    assert "large_unsafe_blob" not in highlights
    assert "{'nested'" not in highlights


def test_snapshot_data_highlights_formats_cached_price_provider_cleanly():
    snapshot = _snapshot("ticker-nvda-2026-06-14")
    snapshot["data"] = {
        "manual_price": {"ticker": "NVDA", "price": 100.5, "currency": "USD", "provider": "manual"},
        "prices": [{"ticker": "VWCE", "price": 120.25, "currency": "EUR", "provider": "manual"}],
    }

    highlights = snapshot_data_highlights_markdown(snapshot)

    assert "NVDA cached price field is 100.5 USD (provider: manual; not live market data)." not in highlights
    assert "VWCE cached price field is 120.25 EUR (provider: manual; not live market data)." not in highlights
    assert "NVDA cached price field is 100.5 USD (provider: manual, not live market data)." in highlights
    assert "VWCE cached price field is 120.25 EUR (provider: manual, not live market data)." in highlights


def test_render_snapshot_summary_lists_snapshots():
    summary = render_snapshot_summary([_snapshot("weekly-2026-06-14"), _snapshot("ticker-nvda-2026-06-14")])

    assert "Snapshot summary" in summary
    assert "weekly-2026-06-14" in summary
    assert "ticker-nvda-2026-06-14" in summary
    assert "No network calls are made" in summary
