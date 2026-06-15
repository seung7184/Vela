# Data Sources

Vela is no-network-by-default. Cached snapshots under `data/processed/snapshots/` are the default research input for repeatable weekly review.

Every report remains:

> Educational use only. Not financial advice.

## Cached snapshots

Snapshots are local JSON files that capture research inputs at a point in time. They are intended for repeatable review, testing, and study without calling live APIs.

Required fields:

- `snapshot_id`
- `snapshot_date`
- `source`
- `created_at`
- `description`
- `data`
- `notes`

Use:

```bash
python -m vela.cli snapshot-summary
python -m vela.cli ticker NVDA --snapshot-id ticker-nvda-2026-06-14
python -m vela.cli weekly --snapshot-id weekly-2026-06-14
python -m vela.cli context-pack ticker NVDA --snapshot-id ticker-nvda-2026-06-14
python -m vela.cli context-pack weekly --snapshot-id weekly-2026-06-14
```

The summary command, snapshot-aware report commands, and context-pack commands read local JSON files only. They do not fetch prices, call SEC, call FRED, call an AI API, place orders, or contact a broker.

Snapshot-aware reports use cached snapshots as report context. They add a `Snapshot context` section and conservative `Snapshot data highlights` section while keeping the normal research discipline sections such as bull case, bear case, downside scenario, VWCE alternative test, and scorecard.

Context packs can also include cached snapshots. They combine memory files, portfolio/watchlist CSVs, and optional snapshot sections into deterministic local Markdown that a human can copy into an AI assistant. Vela does not send context packs to ChatGPT, Claude, OpenAI, Anthropic, SEC, FRED, brokers, or any network service.

Snapshots can become stale. A cached snapshot should not be treated as current market data or complete market data, even when it contains price, macro, or portfolio fields. Stale snapshots should be refreshed intentionally before they are used for current research. Context packs preserve that warning and remain education-only, not financial advice.

## SEC EDGAR

SEC helpers can build and fetch EDGAR URLs when explicitly called by future workflows. Scripted SEC requests require a user-supplied `SEC_USER_AGENT`.

Vela does not call SEC by default, and report generation does not call SEC. Any SEC data used in weekly research should be saved into a reviewed cached snapshot before it is used for repeatable reports.

## FRED

FRED helpers can build and fetch macro data URLs when explicitly called by future workflows. FRED requests require a user-supplied `FRED_API_KEY`.

Vela does not call FRED by default, and report generation does not call FRED. Macro observations should be copied into cached snapshots with dates and source notes before weekly review.

## Manual prices

Manual prices are the Phase 1 default. Snapshot price fields may be `null` when no reviewed price has been entered.

`VELA_PRICE_PROVIDER=manual` remains the safe default. Vela does not include live trading, broker execution, or order placement.

Snapshot report and context-pack generation never adds live trading, broker execution, order placement, AI API calls, or financial advice. Every generated report and context pack remains education-only and not financial advice.

## Refresh cadence

Suggested cadence:

- Weekly: refresh portfolio, watchlist, benchmark, macro notes, and manual price placeholders before the weekly review.
- Monthly: review whether cached SEC/FRED-derived facts are stale.
- Before any thesis update: record the snapshot date and source notes used for the decision.

## Limitations

- Cached snapshots can become stale.
- Manual placeholders are not market data.
- Snapshot validation checks structure, not investment correctness.
- Network helpers are opt-in and require explicit user configuration.
- Vela is a local research OS, not financial advice and not a trading bot.
