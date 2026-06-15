# Vela

Vela is an **ETF-first AI investment research OS** for learning, thesis tracking, and portfolio review.

It is deliberately **not** a live trading bot. Vela gives you a local, testable Python + Markdown system that helps you:

- keep an investment policy in plain text;
- maintain a portfolio and watchlist;
- generate repeatable ticker research notes;
- generate deterministic context packs for manual AI-assisted study;
- compare every stock idea against the default ETF alternative;
- keep decision logs, mistake logs, and weekly reviews;
- add data providers later without exposing secrets or enabling live brokerage execution.

> Vela helps you verify stock ideas before they touch your portfolio.

## Current scope

Included now:

```text
data/processed/snapshots/ Cached JSON snapshots for no-network weekly research
docs/context_packs.md   Manual AI context pack workflow
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
python -m vela.cli ticker NVDA --snapshot-id ticker-nvda-2026-06-14
python -m vela.cli weekly
python -m vela.cli weekly --snapshot-id weekly-2026-06-14
python -m vela.cli context-pack ticker NVDA
python -m vela.cli context-pack ticker NVDA --snapshot-id ticker-nvda-2026-06-14
python -m vela.cli context-pack weekly
python -m vela.cli context-pack weekly --snapshot-id weekly-2026-06-14
```

Generated reports are written to `reports/ticker/` and `reports/weekly/`. Generated context packs are written to `reports/context/`.

Generated reports can be created with or without cached snapshot context. When you pass `--snapshot-id`, Vela reads the matching local JSON snapshot from `data/processed/snapshots/` and adds cached context plus conservative data highlights to the report. Report generation does not refresh data, call APIs, or treat snapshot contents as current market data.

Context packs prepare copy/paste Markdown for manual analysis in tools such as ChatGPT or Claude. Vela does not call any AI API, does not include OpenAI or Anthropic SDKs, and does not transmit context packs anywhere. See `docs/context_packs.md`.

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
