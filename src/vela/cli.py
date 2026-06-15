"""Command-line interface for Vela."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from vela.generate_report import generate_ticker_report, generate_weekly_review
from vela.load_portfolio import load_portfolio, portfolio_total_market_value
from vela.load_watchlist import load_watchlist
from vela.snapshots import DEFAULT_SNAPSHOT_DIR, SnapshotValidationError, load_snapshots, render_snapshot_summary


def doctor() -> int:
    positions = load_portfolio("portfolio.csv")
    watchlist = load_watchlist("watchlist.csv")
    print("Vela doctor")
    print(f"- portfolio positions: {len(positions)}")
    print(f"- watchlist items: {len(watchlist)}")
    print(f"- portfolio market value: {portfolio_total_market_value(positions)}")
    print("- live trading: disabled")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Vela investment research OS")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="Validate local Vela inputs")

    ticker_parser = subparsers.add_parser("ticker", help="Generate a ticker research report")
    ticker_parser.add_argument("ticker", help="Ticker symbol, e.g. NVDA")
    ticker_parser.add_argument("--output-dir", default="reports/ticker")
    ticker_parser.add_argument("--snapshot-id", help="Cached snapshot ID to include as local report context")
    ticker_parser.add_argument("--snapshot-dir", default=str(DEFAULT_SNAPSHOT_DIR))

    weekly_parser = subparsers.add_parser("weekly", help="Generate weekly portfolio review")
    weekly_parser.add_argument("--output-dir", default="reports/weekly")
    weekly_parser.add_argument("--snapshot-id", help="Cached snapshot ID to include as local report context")
    weekly_parser.add_argument("--snapshot-dir", default=str(DEFAULT_SNAPSHOT_DIR))

    snapshot_parser = subparsers.add_parser("snapshot-summary", help="Summarize cached research snapshots")
    snapshot_parser.add_argument("--snapshot-dir", default=str(DEFAULT_SNAPSHOT_DIR))

    args = parser.parse_args(argv)

    if args.command == "doctor":
        return doctor()
    if args.command == "ticker":
        try:
            path = generate_ticker_report(
                args.ticker,
                output_dir=Path(args.output_dir),
                snapshot_id=args.snapshot_id,
                snapshot_dir=Path(args.snapshot_dir),
            )
        except (SnapshotValidationError, FileNotFoundError, NotADirectoryError, ValueError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        print(path)
        return 0
    if args.command == "weekly":
        try:
            path = generate_weekly_review(
                output_dir=Path(args.output_dir),
                snapshot_id=args.snapshot_id,
                snapshot_dir=Path(args.snapshot_dir),
            )
        except (SnapshotValidationError, FileNotFoundError, NotADirectoryError, ValueError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        print(path)
        return 0
    if args.command == "snapshot-summary":
        print(render_snapshot_summary(load_snapshots(Path(args.snapshot_dir))))
        return 0
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
