"""Cached JSON snapshot helpers.

Snapshots are local research inputs. Loading and summarizing them never makes
network calls.
"""

from __future__ import annotations

import json
from datetime import date
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


class SnapshotNotFoundError(SnapshotValidationError):
    """Raised when a requested cached snapshot ID is not present locally."""


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


def find_snapshot_by_id(snapshot_id: str, snapshot_dir: str | Path = DEFAULT_SNAPSHOT_DIR) -> dict[str, Any]:
    """Load local snapshots and return the unique snapshot with ``snapshot_id``."""

    found = None
    seen: set[str] = set()
    for snapshot in load_snapshots(snapshot_dir):
        current_id = snapshot["snapshot_id"]
        if current_id in seen:
            raise SnapshotValidationError(f"Duplicate snapshot_id found in cached snapshots: {current_id}")
        seen.add(current_id)
        if current_id == snapshot_id:
            found = snapshot
    if found is None:
        raise SnapshotNotFoundError(f"Snapshot not found: {snapshot_id}")
    return found


def snapshot_age_days(snapshot: dict[str, Any], today: date | None = None) -> int:
    """Return the age of a snapshot in days based on its ISO ``snapshot_date``."""

    payload = validate_snapshot(snapshot)
    try:
        snapshot_date = date.fromisoformat(payload["snapshot_date"])
    except ValueError as exc:
        raise SnapshotValidationError("Snapshot field 'snapshot_date' must be an ISO date in YYYY-MM-DD format") from exc
    return ((today or date.today()) - snapshot_date).days


def snapshot_staleness_warning(
    snapshot: dict[str, Any],
    today: date | None = None,
    stale_after_days: int = 30,
) -> str:
    """Return a warning when a cached snapshot is older than the allowed threshold."""

    if snapshot_age_days(snapshot, today=today) > stale_after_days:
        return (
            f"Warning: this cached snapshot is older than {stale_after_days} days. "
            "Refresh before using it for current research."
        )
    return ""


def snapshot_context_markdown(snapshot: dict[str, Any], today: date | None = None) -> str:
    """Render deterministic report context for a cached local snapshot."""

    payload = validate_snapshot(snapshot)
    age_days = snapshot_age_days(payload, today=today)
    warning = snapshot_staleness_warning(payload, today=today)
    lines = [
        "## Snapshot context",
        "",
        f"- snapshot_id: {payload['snapshot_id']}",
        f"- snapshot_date: {payload['snapshot_date']}",
        f"- source: {payload['source']}",
        f"- created_at: {payload['created_at']}",
        f"- description: {payload['description']}",
        f"- age_days: {age_days}",
    ]
    if warning:
        lines.append(f"- staleness_warning: {warning}")
    lines.append("- notes:")
    lines.extend(f"  - {note}" for note in payload["notes"])
    lines.extend(["", "This is cached local context only. No network calls were made."])
    return "\n".join(lines)


def _safe_scalar_pairs(values: dict[str, Any]) -> str:
    safe_items = [(key, value) for key, value in values.items() if isinstance(value, (str, int, float, bool))]
    return ", ".join(f"{key}={value}" for key, value in safe_items)


def snapshot_data_highlights_markdown(snapshot: dict[str, Any]) -> str:
    """Render conservative highlights from known safe snapshot data fields."""

    payload = validate_snapshot(snapshot)
    data = payload["data"]
    lines = ["## Snapshot data highlights", ""]

    ticker = data.get("ticker")
    if isinstance(ticker, str) and ticker.strip():
        lines.append(f"- Ticker: {ticker}")

    benchmark = data.get("benchmark")
    if isinstance(benchmark, str) and benchmark.strip():
        lines.append(f"- Benchmark: {benchmark}")

    manual_price = data.get("manual_price")
    if isinstance(manual_price, dict):
        price_ticker = manual_price.get("ticker") if isinstance(manual_price.get("ticker"), str) else ticker
        price = manual_price.get("price")
        currency = manual_price.get("currency")
        provider = manual_price.get("provider")
        if price is None:
            lines.append(f"- Price context: {price_ticker} price is a manual placeholder, not live market data.")
        elif isinstance(price, (int, float)):
            suffix = f" {currency}" if isinstance(currency, str) and currency else ""
            source = f" provider: {provider};" if isinstance(provider, str) and provider else ""
            lines.append(f"- Price context: {price_ticker} cached price field is {price}{suffix} ({source} not live market data).")

    prices = data.get("prices")
    if isinstance(prices, list):
        for price_item in prices[:5]:
            if not isinstance(price_item, dict):
                continue
            price_ticker = price_item.get("ticker")
            if not isinstance(price_ticker, str) or not price_ticker.strip():
                continue
            price = price_item.get("price")
            currency = price_item.get("currency")
            provider = price_item.get("provider")
            if price is None:
                lines.append(f"- Price context: {price_ticker} price is a manual placeholder, not live market data.")
            elif isinstance(price, (int, float)):
                suffix = f" {currency}" if isinstance(currency, str) and currency else ""
                source = f" provider: {provider};" if isinstance(provider, str) and provider else ""
                lines.append(
                    f"- Price context: {price_ticker} cached price field is {price}{suffix} ({source} not live market data)."
                )

    macro = data.get("macro")
    if isinstance(macro, list):
        for item in macro[:5]:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            observation = item.get("observation")
            source = item.get("source")
            if isinstance(name, str) and isinstance(observation, str):
                source_text = f" (source: {source})" if isinstance(source, str) and source else ""
                lines.append(f"- Macro: {name} - {observation}{source_text}")

    portfolio = data.get("portfolio")
    if isinstance(portfolio, dict):
        summary = _safe_scalar_pairs(portfolio)
        if summary:
            lines.append(f"- Portfolio context: {summary}")

    research_questions = data.get("research_questions")
    if isinstance(research_questions, list):
        for question in research_questions[:5]:
            if isinstance(question, str) and question.strip():
                lines.append(f"- Research question: {question}")

    vwce_test = data.get("vwce_alternative_test")
    if isinstance(vwce_test, dict):
        status = vwce_test.get("status")
        default_answer = vwce_test.get("default_answer")
        parts = []
        if isinstance(status, str) and status:
            parts.append(f"status={status}")
        if isinstance(default_answer, str) and default_answer:
            parts.append(f"default_answer={default_answer}")
        if parts:
            lines.append(f"- VWCE alternative test context: {', '.join(parts)}")

    if len(lines) == 2:
        lines.append("- No known safe highlight fields were found in this snapshot.")

    return "\n".join(lines)


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
