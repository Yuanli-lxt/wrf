# WRF 72h Validation And APSIM Export Implementation Plan

**Goal:** Add a separate 72-hour WRF validation path and APSIM `.met` export while preserving the existing 24-hour baseline.

**Architecture:** Copy the proven 24-hour path into separate 72-hour artifacts: one namelist, one WRF runner, and one export script. Keep outputs in `_72h` directories/files so baseline artifacts are not overwritten except for shared WRF run scratch inside the container.

**Tech Stack:** Bash, Python, Docker Compose, WRF/WPS namelists, pytest contract tests.

## Task 1: Contract Tests

**Files:**
- Modify: `tests/test_deployment_files.py`
- Modify: `tests/test_export_script.py`

- [x] Add tests for `namelist.input.72h.template`.
- [x] Assert the 72-hour namelist starts on 2024-10-01 and ends on 2024-10-04.
- [x] Assert the 72-hour namelist keeps hourly history output and 24 frames per file.
- [x] Add tests for `run_wrf_validation_72h.sh`.
- [x] Assert it uses `namelist.input.72h.template`.
- [x] Assert it reads `data/wps/validation_20241001_00`.
- [x] Assert it writes `data/wrfout/validation_20241001_00_72h`.
- [x] Assert it checks for 25 `met_em` files and final `wrfout_d01_2024-10-04_00-00-00`.
- [x] Add tests for `export_validation_72h_met.py`.
- [x] Assert it reads the 72-hour WRF output directory and writes `validation_wrf_20241001_72h.met`.

## Task 2: 72h Namelist

**Files:**
- Create: `wrf/namelists/namelist.input.72h.template`

- [x] Base the file on the current 24-hour namelist.
- [x] Set `run_days = 3`.
- [x] Set end date to 2024-10-04 00:00:00.
- [x] Preserve existing physics, grid, time step, and hourly output settings.

## Task 3: 72h WRF Runner

**Files:**
- Create: `scripts/run_wrf_validation_72h.sh`

- [x] Base the file on `scripts/run_wrf_validation.sh`.
- [x] Use `namelist.input.72h.template`.
- [x] Require 25 WPS `met_em` inputs.
- [x] Write outputs to `data/wrfout/validation_20241001_00_72h`.
- [x] Preserve Windows-safe filename conversion.
- [x] Check for the final 2024-10-04 output file.

## Task 4: 72h APSIM Export

**Files:**
- Create: `scripts/export_validation_72h_met.py`

- [x] Base the file on `scripts/export_validation_met.py`.
- [x] Read `data/wrfout/validation_20241001_00_72h`.
- [x] Use a separate ASCII-safe staging directory.
- [x] Write `data/generated/apsim/validation_wrf_20241001_72h.met`.
- [x] Reuse `aggregate_wrf_dataset` and `write_met_file`.

## Task 5: Verification

- [x] Run targeted pytest for deployment/export contracts.
- [x] Run full pytest.
- [x] Run `bash -n scripts/run_wrf_validation_72h.sh`.
- [x] Run `python -m py_compile scripts/export_validation_72h_met.py`.
- [x] Run Docker Compose config validation.
- [x] Run 72-hour WRF with `NPROC=4`.
- [x] Export 72-hour APSIM `.met`.
- [x] Confirm the `.met` contains three records.

## Task 6: Review

- [x] Review the diff against the spec.
- [x] Confirm no existing 24-hour baseline files were changed unnecessarily.
- [x] Confirm no tests run heavy WRF or download data.
- [x] Fix any Critical or Important finding before final status.
