# WRF 24h 4-Core Baseline Benchmark Implementation Plan

**Goal:** Add a repeatable script for benchmarking the current 24-hour WRF validation case at 4 cores.

**Architecture:** Keep the existing WRF validation script as the execution target. Add thin host benchmark wrappers that set `NPROC=4`, repeat the run, write one CSV row per repeat, store logs, and report failures after recording results. The Bash wrapper is primary for Ubuntu-WRF; the PowerShell wrapper mirrors the same contract for Windows.

**Tech Stack:** Bash, PowerShell, Docker Compose, pytest text-contract tests.

## Task 1: Contract Tests

**Files:**
- Modify: `tests/test_deployment_files.py`

- [x] Add a test that checks the new baseline benchmark script exists.
- [x] Assert the script defaults to `Nproc = 4`.
- [x] Assert the script defaults to `RepeatCount = 3`.
- [x] Assert the output path is `data/generated/benchmarks/wrf_validation_24h_nproc4_baseline.csv`.
- [x] Assert it times `/work/scripts/run_wrf_validation.sh`.
- [x] Assert it records `run_label`, `run_index`, `nproc`, `seconds`, `exit_code`, `git_commit`, `log`, and `command`.
- [x] Assert it fails after writing results if any repeat fails.

## Task 2: Ubuntu Benchmark Script

**Files:**
- Create: `scripts/benchmark_wrf_24h_nproc4_baseline.sh`

- [x] Add environment overrides for `REPEAT_COUNT`, `NPROC_VALUE`, and `OUTPUT_PATH`.
- [x] Default `REPEAT_COUNT` to 3 and `NPROC_VALUE` to 4.
- [x] Create `data/generated/benchmarks/` if needed.
- [x] Capture the current short git commit where available.
- [x] For each repeat, set `NPROC`, time the Docker WRF validation command, and redirect output to a per-repeat log.
- [x] Append a CSV row with the output contract fields.
- [x] Support `REPEAT_COUNT=0` as a header-only dry run that does not launch WRF.
- [x] Exit non-zero after writing results if any repeat has a non-zero exit code.

## Task 3: PowerShell Benchmark Script

**Files:**
- Create: `scripts/benchmark_wrf_24h_nproc4_baseline.ps1`

- [x] Add parameters for `RepeatCount`, `Nproc`, and `OutputPath`.
- [x] Default `RepeatCount` to 3 and `Nproc` to 4.
- [x] Create `data/generated/benchmarks/` if needed.
- [x] Capture the current short git commit where available.
- [x] For each repeat, set `$env:NPROC`, time the Docker WRF validation command with `Measure-Command`, and redirect output to a per-repeat log.
- [x] Append a structured row to the results array.
- [x] Remove `NPROC` from the environment at the end.
- [x] Export CSV and print a table.
- [x] Throw if any repeat has a non-zero exit code.

## Task 4: Verification

- [x] Run `pytest tests/test_deployment_files.py -v`.
- [x] Run `pytest -v`.
- [x] Run `docker compose -f docker/docker-compose.yml config --quiet`.
- [x] Run `REPEAT_COUNT=0 scripts/benchmark_wrf_24h_nproc4_baseline.sh`.
- [ ] Run `pwsh -NoProfile -File scripts/benchmark_wrf_24h_nproc4_baseline.ps1 -RepeatCount 0` if PowerShell is available. Not run because `pwsh` is not installed in this Ubuntu shell.

## Task 5: Review

- [x] Review the diff against the spec.
- [x] Review for operational risk: no accidental downloads, no WPS runs, no namelist edits, no hidden long-running behavior in tests.
- [x] Fix any Critical or Important finding before final status.
