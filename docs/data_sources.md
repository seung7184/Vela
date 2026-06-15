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
```

The summary command reads local JSON files only. It does not fetch prices, call SEC, call FRED, place orders, or contact a broker.

## SEC EDGAR

SEC helpers can build and fetch EDGAR URLs when explicitly called by future workflows. Scripted SEC requests require a user-supplied `SEC_USER_AGENT`.

Phase 1 does not call SEC by default. Any SEC data used in weekly research should be saved into a reviewed cached snapshot before it is used for repeatable reports.

## FRED

FRED helpers can build and fetch macro data URLs when explicitly called by future workflows. FRED requests require a user-supplied `FRED_API_KEY`.

Phase 1 does not call FRED by default. Macro observations should be copied into cached snapshots with dates and source notes before weekly review.

## Manual prices

Manual prices are the Phase 1 default. Snapshot price fields may be `null` when no reviewed price has been entered.

`VELA_PRICE_PROVIDER=manual` remains the safe default. Vela does not include live trading, broker execution, or order placement.

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
