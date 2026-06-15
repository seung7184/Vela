# Context Packs

Context packs are deterministic local Markdown artifacts for manual AI-assisted research. They collect Vela memory files, `portfolio.csv`, `watchlist.csv`, and optional cached snapshots into one auditable file.

Every generated context pack includes:

> Educational use only. Not financial advice.

## Generate a context pack

```bash
python -m vela.cli context-pack ticker NVDA
python -m vela.cli context-pack ticker NVDA --snapshot-id ticker-nvda-2026-06-14
python -m vela.cli context-pack weekly
python -m vela.cli context-pack weekly --snapshot-id weekly-2026-06-14
```

Files are written to `reports/context/`.

## Manual AI workflow

1. Generate a context pack locally.
2. Open the Markdown file in `reports/context/`.
3. Review it before sharing.
4. Copy the content into ChatGPT, Claude, or another assistant manually.
5. Ask the assistant to use only the context pack and to avoid live market data unless you provide separate approved inputs.

Vela does not call OpenAI, Anthropic, SEC, FRED, brokers, or any network service when generating context packs. It does not include an AI SDK and does not transmit files.

## Snapshot context

When `--snapshot-id` is provided, Vela loads the matching local JSON snapshot from `data/processed/snapshots/` and adds:

- `Snapshot context`
- `Snapshot data highlights`
- stale snapshot warnings when applicable

Cached snapshots are point-in-time research inputs. They are not current market data, complete market data, or a trading signal.

When no snapshot is selected, the context pack includes a clear `No snapshot selected` note.

## Private data caution

If you later add private account data, do not paste these items into an external AI assistant unless you have deliberately reviewed and redacted them:

- account numbers;
- tax IDs or national IDs;
- private addresses or phone numbers;
- exact cash balances you do not want to disclose;
- broker names tied to private accounts;
- API keys, tokens, passwords, or `.env` values.

Prefer replacing sensitive values with ranges or labels such as `small cash buffer`, `core ETF account`, or `private broker account`.

## Safety boundaries

Context packs are for education and research journaling only. They do not add live trading, broker execution, order placement helpers, automatic data refreshes, AI API calls, or financial advice.
