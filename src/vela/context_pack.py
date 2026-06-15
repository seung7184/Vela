"""AI-ready local context pack generation for Vela.

Context packs are deterministic Markdown artifacts. They collect local memory
files, CSV inputs, and optional cached snapshots without making network calls
or invoking any AI API.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from vela.constants import DISCLAIMER
from vela.snapshots import (
    DEFAULT_SNAPSHOT_DIR,
    find_snapshot_by_id,
    snapshot_context_markdown,
    snapshot_data_highlights_markdown,
)

MEMORY_DIR = Path("memory")
INVESTMENT_POLICY_PATH = MEMORY_DIR / "investment_policy.md"
PORTFOLIO_RULES_PATH = MEMORY_DIR / "portfolio_rules.md"
THESIS_LOG_PATH = MEMORY_DIR / "thesis_log.md"
WATCHLIST_REASONING_PATH = MEMORY_DIR / "watchlist_reasoning.md"
PORTFOLIO_CSV_PATH = Path("portfolio.csv")
WATCHLIST_CSV_PATH = Path("watchlist.csv")


def read_text_file(path: str | Path) -> str:
    """Read a UTF-8 text file from the local workspace."""

    return Path(path).read_text(encoding="utf-8").strip()


def _markdown_cell(value: str | None) -> str:
    text = "" if value is None else str(value)
    return text.replace("\n", " ").replace("|", "\\|")


def read_csv_as_markdown(path: str | Path, max_rows: int = 20) -> str:
    """Render a local CSV file as a deterministic Markdown table."""

    if max_rows < 0:
        raise ValueError("max_rows must be non-negative")

    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))

    if not rows:
        return "_No CSV rows found._"

    header = rows[0]
    data_rows = rows[1:]
    selected_rows = data_rows[:max_rows]
    table = [
        "| " + " | ".join(_markdown_cell(cell) for cell in header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    table.extend("| " + " | ".join(_markdown_cell(cell) for cell in row) + " |" for row in selected_rows)
    if len(data_rows) > max_rows:
        table.extend(["", f"_Showing {len(selected_rows)} of {len(data_rows)} rows._"])
    return "\n".join(table)


def _generation_metadata(*, today: date, ticker: str | None = None) -> str:
    lines = [
        "## Generation metadata",
        f"- generated_at: {today.isoformat()}",
    ]
    if ticker is not None:
        lines.append(f"- ticker: {ticker.upper()}")
    lines.extend(
        [
            "- no_network: true",
            "- live_trading: disabled",
            "- broker_execution: disabled",
            "- ai_api_calls: disabled",
        ]
    )
    return "\n".join(lines)


def _safety_boundaries() -> str:
    return """Vela context packs are local research inputs only.

- No network calls are made.
- No AI API calls are made.
- No live trading is enabled.
- No broker execution is enabled.
- No order placement helpers are included.
- Cached snapshots are not current market data."""


def _snapshot_sections(snapshot_id: str | None, snapshot_dir: str | Path, today: date) -> str:
    if not snapshot_id:
        return """## Snapshot context

No snapshot selected.

## Snapshot data highlights

No snapshot selected."""

    snapshot = find_snapshot_by_id(snapshot_id, snapshot_dir=snapshot_dir)
    return f"""{snapshot_context_markdown(snapshot, today=today)}

{snapshot_data_highlights_markdown(snapshot)}"""


def _local_memory_sections() -> str:
    return f"""## Safety boundaries

{_safety_boundaries()}

## Investment policy

{read_text_file(INVESTMENT_POLICY_PATH)}

## Portfolio rules

{read_text_file(PORTFOLIO_RULES_PATH)}

## Thesis log

{read_text_file(THESIS_LOG_PATH)}

## Watchlist reasoning

{read_text_file(WATCHLIST_REASONING_PATH)}

## Portfolio CSV

{read_csv_as_markdown(PORTFOLIO_CSV_PATH)}

## Watchlist CSV

{read_csv_as_markdown(WATCHLIST_CSV_PATH)}"""


def _ticker_prompt(ticker: str) -> str:
    normalized = ticker.upper()
    return f"""Analyze {normalized} using only this context pack. Do not use live market data, external browsing, broker tools, or unstated assumptions.

Include:

- business model
- bull case
- bear case
- valuation risk
- downside scenario
- VWCE alternative test
- what would change my mind
- final label"""


def _weekly_prompt() -> str:
    return """Analyze the week using only this context pack. Do not use live market data, external browsing, broker tools, or unstated assumptions.

Include:

- weekly market review
- ETF core assessment
- individual stock ideas worth studying
- ideas rejected and why
- emotional mistakes to avoid
- next week's study plan"""


def build_ticker_context_pack(
    ticker: str,
    snapshot_id: str | None = None,
    snapshot_dir: str | Path = DEFAULT_SNAPSHOT_DIR,
    today: date | None = None,
) -> str:
    """Build a ticker-specific AI-ready Markdown context pack."""

    normalized = ticker.upper()
    generated_at = today or date.today()
    return f"""# Vela Ticker Context Pack - {normalized}

{DISCLAIMER}

{_generation_metadata(today=generated_at, ticker=normalized)}

{_local_memory_sections()}

{_snapshot_sections(snapshot_id, snapshot_dir, generated_at)}

## Manual AI prompt scaffold

{_ticker_prompt(normalized)}
"""


def build_weekly_context_pack(
    snapshot_id: str | None = None,
    snapshot_dir: str | Path = DEFAULT_SNAPSHOT_DIR,
    today: date | None = None,
) -> str:
    """Build a weekly AI-ready Markdown context pack."""

    generated_at = today or date.today()
    return f"""# Vela Weekly Context Pack - {generated_at.isoformat()}

{DISCLAIMER}

{_generation_metadata(today=generated_at)}

{_local_memory_sections()}

{_snapshot_sections(snapshot_id, snapshot_dir, generated_at)}

## Manual AI prompt scaffold

{_weekly_prompt()}
"""


def write_context_pack(content: str, output_path: str | Path) -> Path:
    """Write a context pack Markdown file and return its path."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
