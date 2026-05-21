# WRF Domain Size Sweep Implementation Plan

**Goal:** Compare 80x80, 60x60, and 50x50 WRF domains for 24h/72h stability, runtime, and APSIM `.met` differences at 37.94N, 118.53E.

**Architecture:** Add domain-size-specific WPS/WRF/export wrappers plus one benchmark orchestrator and one summary script. Generate namelists at runtime by substituting `e_we` and `e_sn` while preserving the existing validated templates.

**Tech Stack:** Bash, Python, Docker Compose, WPS, WRF, pytest text-contract tests.

## Task 1: Contract Tests

**Files:**
- Modify: `tests/test_deployment_files.py`
- Modify: `tests/test_export_script.py`

- [x] Add tests for the domain-size WPS runner.
- [x] Add tests for the domain-size WRF runner.
- [x] Add tests for the domain-size benchmark orchestrator.
- [x] Add tests for the domain-size APSIM export script.
- [x] Add tests for the summary script output contract.

## Task 2: Domain-Size WPS Runner

**Files:**
- Create: `scripts/run_wps_domain_size.sh`

- [x] Read `DOMAIN_SIZE`, defaulting to 80.
- [x] Validate that `DOMAIN_SIZE` is numeric.
- [x] Generate `namelist.wps` from the validated template with matching `e_we` and `e_sn`.
- [x] Reuse the existing GFS boundary directory.
- [x] Run `geogrid.exe`, `ungrib.exe`, and `metgrid.exe`.
- [x] Copy Windows-safe outputs to `data/wps/domain_{size}_validation_20241001_00`.

## Task 3: Domain-Size WRF Runner

**Files:**
- Create: `scripts/run_wrf_domain_size.sh`

- [x] Read `DOMAIN_SIZE` and `WINDOW_HOURS`.
- [x] Use 24h or 72h namelist template based on `WINDOW_HOURS`.
- [x] Generate `namelist.input` with matching `e_we` and `e_sn`.
- [x] Read WPS outputs from `data/wps/domain_{size}_validation_20241001_00`.
- [x] Write WRF outputs to `data/wrfout/domain_{size}_{window}h_validation_20241001_00`.
- [x] Check the expected final `wrfout` file.

## Task 4: Export And Summary

**Files:**
- Create: `scripts/export_domain_size_met.py`
- Create: `scripts/summarize_domain_size_sweep.py`

- [x] Export APSIM `.met` for `DOMAIN_SIZE` and `WINDOW_HOURS`.
- [x] Use separate ASCII-safe staging directories per case.
- [x] Summarize differences against the matching 80x80 reference.
- [x] Write `domain_size_sweep_summary.csv`.

## Task 5: Benchmark Orchestrator

**Files:**
- Create: `scripts/benchmark_domain_size_sweep.sh`

- [x] Loop over `DOMAIN_SIZES`, defaulting to `80 60 50`.
- [x] Loop over `WINDOW_HOURS_LIST`, defaulting to `24 72`.
- [x] Time WPS, WRF, and export stages.
- [x] Write `domain_size_sweep.csv`.
- [x] Run the summary script after all cases.

## Task 6: Verification

- [x] Run targeted pytest.
- [x] Run full pytest.
- [x] Run shell syntax checks.
- [x] Run Python compile checks.
- [x] Run Docker Compose config validation.
- [x] Run the sweep, or a narrowed sweep first if runtime is too high.
- [x] Confirm `.met` record counts and summary metrics.

## Task 7: Review

- [x] Review diff against the spec.
- [x] Confirm existing 24h/72h baseline scripts remain intact.
- [x] Confirm automated tests do not run WRF or download data.
- [x] Fix any Critical or Important issue before final status.
