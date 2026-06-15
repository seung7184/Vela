import json

import pytest

from vela.snapshots import (
    SnapshotValidationError,
    load_snapshot,
    load_snapshots,
    render_snapshot_summary,
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


def test_render_snapshot_summary_lists_snapshots():
    summary = render_snapshot_summary([_snapshot("weekly-2026-06-14"), _snapshot("ticker-nvda-2026-06-14")])

    assert "Snapshot summary" in summary
    assert "weekly-2026-06-14" in summary
    assert "ticker-nvda-2026-06-14" in summary
    assert "No network calls are made" in summary
