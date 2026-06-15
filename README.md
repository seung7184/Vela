# Vela

Vela is an **ETF-first AI investment research OS** for learning, thesis tracking, and portfolio review.

It is deliberately **not** a live trading bot. Vela gives you a local, testable Python + Markdown system that helps you:

- keep an investment policy in plain text;
- maintain a portfolio and watchlist;
- generate repeatable ticker research notes;
- compare every stock idea against the default ETF alternative;
- keep decision logs, mistake logs, and weekly reviews;
- add data providers later without exposing secrets or enabling live brokerage execution.

> Vela helps you verify stock ideas before they touch your portfolio.

## Current scope

Included now:

```text
data/processed/snapshots/ Cached JSON snapshots for no-network weekly research
memory/                 Investment policy and long-term rules
routines/               Daily and weekly review prompts
reports/                Generated report output folders
src/vela/               Small Python package
portfolio.csv           Sample ETF-first portfolio template
watchlist.csv           Sample ETF/stock watchlist template
tests/                  Unit tests for loaders, scoring, reports, and URLs
.github/workflows/ci.yml GitHub Actions test workflow
```

Not included in Phase 0:

- live trading;
- broker API execution;
- automated order placement;
- secrets committed to git;
- financial advice.

## Safety model

Vela is built around a few hard rules:

1. **No live trading in v1.**
2. **VWCE/core ETF is the default benchmark.**
3. **Every stock thesis needs a bear case.**
4. **Every idea must define what would change your mind.**
5. **Every report is education-only and not financial advice.**
6. **API keys live only in environment variables.**

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .[dev]
pytest
python -m vela.cli doctor
python -m vela.cli snapshot-summary
python -m vela.cli ticker NVDA
python -m vela.cli weekly
```

Generated reports are written to `reports/ticker/` and `reports/weekly/`.

Cached research snapshots live under `data/processed/snapshots/`. See `docs/data_sources.md` for the no-network default workflow and source limitations.

## Environment variables

Copy `.env.example` to `.env` for local use. Do not commit `.env`.

```bash
cp .env.example .env
```

Optional variables:

- `SEC_USER_AGENT`: required by SEC-friendly scripted access when fetching SEC data.
- `FRED_API_KEY`: required for FRED API calls.
- `VELA_PRICE_PROVIDER`: future hook for price providers.

## Repository status

This repository is built through small, reviewable pull requests:

- Phase 1: cached snapshots for no-network weekly research;
- Phase 2: AI-assisted report drafting using saved Markdown context;
- Phase 3: paper-trading sandbox only, disabled by default;
- Phase 4: dashboard or notebook layer.
