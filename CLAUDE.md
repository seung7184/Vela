# CLAUDE.md — Vela operating rules

You are working on Vela, an ETF-first AI investment research OS.

## Non-negotiable rules

- Do not add live trading in Phase 0 or Phase 1.
- Do not add brokerage execution code.
- Do not create order placement helpers.
- Do not commit secrets, API keys, account numbers, or brokerage credentials.
- Every report must include: bull case, bear case, VWCE alternative test, downside risk, and what would change my mind.
- Every report must include: "Educational use only. Not financial advice."
- Prefer boring, testable Python over clever automation.

## Investor context

The default investor is based in the Netherlands, invests mostly via broad ETFs such as VWCE/CSPX, and uses Vela to study individual stocks without losing discipline.

## Default decision policy

The default answer is **ETF-only is better** unless the single-stock thesis is clearly stronger on a risk-adjusted basis and fits portfolio rules.

Allowed labels:

- Avoid
- Study more
- Watchlist
- Small position candidate
- ETF-only is better

## Build style

- Keep modules small.
- Use pure functions where possible.
- Avoid network calls in tests.
- Keep data-source functions injectable/mocked.
- Preserve Markdown files as the memory layer.
