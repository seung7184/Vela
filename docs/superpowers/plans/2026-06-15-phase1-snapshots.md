# Phase 1 Snapshots Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a no-network-by-default cached JSON snapshot layer for repeatable weekly research.

**Architecture:** Snapshot files live under `data/processed/snapshots/` and are loaded through `src/vela/snapshots.py`, which validates required fields and blocks path traversal. The CLI adds a read-only `snapshot-summary` command that renders committed snapshots without touching network helpers.

**Tech Stack:** Python standard library JSON/path APIs, argparse, pytest.

---

### Task 1: Snapshot Module Tests

**Files:**
- Create: `tests/test_snapshots.py`

- [ ] **Step 1: Write failing tests for loading, validation, missing files, invalid JSON, unsafe paths, writing, and summary rendering**

Run: `pytest tests/test_snapshots.py -q`
Expected: FAIL because `vela.snapshots` does not exist.

### Task 2: Snapshot Module

**Files:**
- Create: `src/vela/snapshots.py`

- [ ] **Step 1: Implement `SnapshotValidationError`, `DEFAULT_SNAPSHOT_DIR`, path resolution, `validate_snapshot()`, `load_snapshot()`, `load_snapshots()`, `write_snapshot()`, and `render_snapshot_summary()`**

Run: `pytest tests/test_snapshots.py -q`
Expected: PASS.

### Task 3: Sample Snapshot Data

**Files:**
- Create: `data/processed/snapshots/2026-06-14-weekly.json`
- Create: `data/processed/snapshots/NVDA-2026-06-14.json`

- [ ] **Step 1: Add safe sample JSON snapshots with blank/no-secret metadata, manual price data, and education-only notes**

Run: `python -m vela.cli snapshot-summary`
Expected: The command still fails until Task 4 wires the CLI.

### Task 4: CLI Summary

**Files:**
- Modify: `src/vela/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write a failing CLI test for `snapshot-summary`**

Run: `pytest tests/test_cli.py::test_cli_snapshot_summary -q`
Expected: FAIL because the CLI command is unknown.

- [ ] **Step 2: Add the read-only CLI command**

Run: `pytest tests/test_cli.py::test_cli_snapshot_summary -q`
Expected: PASS.

### Task 5: Data Sources Documentation

**Files:**
- Create: `docs/data_sources.md`
- Modify: `README.md`

- [ ] **Step 1: Document SEC, FRED, manual prices, cached snapshots, refresh cadence, limitations, and safety boundaries**

Run: `pytest -q`
Expected: PASS.

### Task 6: Full Validation and PR

**Files:**
- All changed files

- [ ] **Step 1: Run full validation**

Run:

```bash
python -m pip install -e .[dev]
pytest -q
python -m vela.cli doctor
python -m vela.cli snapshot-summary
python -m vela.cli ticker NVDA --output-dir /tmp/vela_reports/ticker
python -m vela.cli weekly --output-dir /tmp/vela_reports/weekly
python -m compileall -q src tests
```

Expected: all commands exit 0.

- [ ] **Step 2: Push `phase1-snapshots` and open PR against `main` titled `Phase 1: add cached data snapshots`**
