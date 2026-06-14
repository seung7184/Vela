# AGENTS.md

## Mission

Build Vela as a calm, auditable investment research journal — not a trading robot.

## Agent roles

### Architect
Checks scope, safety boundaries, and folder conventions.

### Research Engineer
Adds data loaders and report generators with tests.

### Reviewer
Looks for accidental live-trading hooks, missing tests, secrets, and misleading financial advice language.

## Definition of done

- `pytest` passes locally.
- New code has tests.
- No live trading module exists.
- `.env` is ignored.
- Generated reports contain the education-only disclaimer.
