"""Cached JSON snapshot helpers.

Snapshots are local research inputs. Loading and summarizing them never makes
network calls.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_SNAPSHOT_DIR = Path("data/processed/snapshots")
REQUIRED_FIELDS = {
    "snapshot_id",
    "snapshot_date",
    "source",
    "created_at",
    "description",
    "data",
    "notes",
}


class SnapshotValidationError(ValueError):
    """Raised when a snapshot file does not match Vela's minimal schema."""


def _resolve_snapshot_path(path: str | Path, *, snapshot_dir: str | Path | None = None) -> Path:
    candidate = Path(path)
    if ".." in candidate.parts:
        raise ValueError(f"Snapshot path contains parent path segments: {path}")
    if snapshot_dir is None:
        return candidate

    root = Path(snapshot_dir).resolve()
    resolved = (root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"Snapshot path is outside snapshot directory: {path}")
    return resolved


def validate_snapshot(snapshot: Any) -> dict[str, Any]:
    """Validate and return a snapshot dictionary."""

    if not isinstance(snapshot, dict):
        raise SnapshotValidationError("Snapshot must be a JSON object")

    missing = REQUIRED_FIELDS - set(snapshot)
    if missing:
        raise SnapshotValidationError(f"Snapshot is missing required fields: {sorted(missing)}")

    for field in ("snapshot_id", "snapshot_date", "source", "created_at", "description"):
        if not isinstance(snapshot[field], str) or not snapshot[field].strip():
            raise SnapshotValidationError(f"Snapshot field {field!r} must be a non-empty string")
    if not isinstance(snapshot["data"], dict):
        raise SnapshotValidationError("Snapshot field 'data' must be an object")
    if not isinstance(snapshot["notes"], list) or not all(isinstance(note, str) for note in snapshot["notes"]):
        raise SnapshotValidationError("Snapshot field 'notes' must be a list of strings")
    return snapshot


def load_snapshot(path: str | Path, *, snapshot_dir: str | Path | None = None) -> dict[str, Any]:
    """Load and validate one snapshot JSON file."""

    snapshot_path = _resolve_snapshot_path(path, snapshot_dir=snapshot_dir)
    try:
        raw = snapshot_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SnapshotValidationError(f"Invalid JSON in snapshot {snapshot_path}: {exc.msg}") from exc
    return validate_snapshot(payload)


def load_snapshots(snapshot_dir: str | Path = DEFAULT_SNAPSHOT_DIR) -> list[dict[str, Any]]:
    """Load all JSON snapshots from a directory in deterministic order."""

    root = Path(snapshot_dir)
    if not root.exists():
        raise FileNotFoundError(f"Snapshot directory does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Snapshot path is not a directory: {root}")

    return [load_snapshot(path.name, snapshot_dir=root) for path in sorted(root.glob("*.json"))]


def write_snapshot(snapshot: dict[str, Any], path: str | Path, *, snapshot_dir: str | Path | None = None) -> Path:
    """Validate and write one snapshot JSON file."""

    payload = validate_snapshot(snapshot)
    snapshot_path = _resolve_snapshot_path(path, snapshot_dir=snapshot_dir)
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return snapshot_path


def render_snapshot_summary(snapshots: list[dict[str, Any]]) -> str:
    """Render a concise CLI summary for cached snapshots."""

    lines = [
        "Snapshot summary",
        "No network calls are made. Cached snapshots are local research inputs.",
        f"Snapshots loaded: {len(snapshots)}",
    ]
    for snapshot in snapshots:
        lines.append(
            "- "
            f"{snapshot['snapshot_id']} | "
            f"date: {snapshot['snapshot_date']} | "
            f"source: {snapshot['source']} | "
            f"{snapshot['description']}"
        )
    return "\n".join(lines)
