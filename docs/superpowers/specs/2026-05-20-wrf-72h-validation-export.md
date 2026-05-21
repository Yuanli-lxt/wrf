# WRF 72h Validation And APSIM Export Design

## Goal

Add an isolated 72-hour WRF validation path that uses the already prepared 2024-10-01 00Z GFS/WPS inputs and exports a three-day APSIM `.met` file. The existing 24-hour validation path remains the baseline and must not be replaced.

## Scope

The 72-hour validation case covers:

- Start: `2024-10-01_00:00:00`.
- End: `2024-10-04_00:00:00`.
- WPS input directory: `data/wps/validation_20241001_00`.
- WRF output directory: `data/wrfout/validation_20241001_00_72h`.
- APSIM output: `data/generated/apsim/validation_wrf_20241001_72h.met`.

The task does not download new data and does not rerun WPS. It reuses the existing 25 `met_em` files generated from forecast hours 000 through 072.

## Architecture

Add a separate WRF namelist template:

- `wrf/namelists/namelist.input.72h.template`

Add a separate WRF execution script:

- `scripts/run_wrf_validation_72h.sh`

Add a separate APSIM export script:

- `scripts/export_validation_72h_met.py`

The 24-hour files remain unchanged:

- `wrf/namelists/namelist.input.template`
- `scripts/run_wrf_validation.sh`
- `scripts/export_validation_met.py`

## Output Contract

The 72-hour WRF run should produce Windows-safe output names under `data/wrfout/validation_20241001_00_72h`, including:

- `wrfout_d01_2024-10-01_00-00-00`
- `wrfout_d01_2024-10-02_00-00-00`
- `wrfout_d01_2024-10-03_00-00-00`
- `wrfout_d01_2024-10-04_00-00-00`

The APSIM export should aggregate complete days only, producing three records for:

- 2024-10-01
- 2024-10-02
- 2024-10-03

## Testing

Automated tests should validate script and template contracts without running WRF. Heavy WRF execution remains an explicit verification command.

## Verification

Lightweight verification:

- Run pytest.
- Run shell syntax checks.
- Validate Docker Compose config.

Heavy verification:

- Run `NPROC=4 docker compose -f docker/docker-compose.yml run --rm wrf bash /work/scripts/run_wrf_validation_72h.sh`.
- Run `python scripts/export_validation_72h_met.py`.
- Confirm the exported `.met` has three APSIM records.
