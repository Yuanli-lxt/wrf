# WRF 24h 4-Core Baseline Benchmark Design

## Goal

Create repeatable benchmark entry points for the already-validated 24-hour WRF run. The benchmark fixes the runtime to `NPROC=4`, uses the current `namelist.input.template` validation window, and records enough metadata to compare future changes against the baseline.

## Scope

This benchmark is only for the current short validation case:

- WPS inputs: `data/wps/validation_20241001_00`.
- WRF outputs: `data/wrfout/validation_20241001_00`.
- WRF command: `docker compose -f docker/docker-compose.yml run --rm wrf bash /work/scripts/run_wrf_validation.sh`.
- Parallelism: `NPROC=4`.
- Default repeats: 3 runs, so the user can compute a stable middle value.
- Primary Ubuntu entry point: `scripts/benchmark_wrf_24h_nproc4_baseline.sh`.
- Windows PowerShell companion: `scripts/benchmark_wrf_24h_nproc4_baseline.ps1`.

The benchmark does not run WPS, download data, edit namelists, or export APSIM `.met` files.

## Output Contract

The script writes a CSV under `data/generated/benchmarks/` with one row per repeat. Each row records:

- `run_label`: fixed validation case name.
- `run_index`: one-based repeat number.
- `nproc`: fixed at 4 by default.
- `seconds`: wall-clock duration rounded to two decimals.
- `exit_code`: process exit code.
- `git_commit`: short commit hash when available.
- `log`: per-repeat log file path.
- `command`: Docker command that was timed.

The script should preserve per-repeat logs and fail after writing the CSV if any repeat failed.

## Testing

Automated tests should inspect the script contract without running WRF. Heavy WRF execution remains an explicit manual/deployment verification step.

## Verification

Lightweight verification:

- Run the relevant pytest tests.
- Parse Docker Compose configuration.
- Run the Bash script with `REPEAT_COUNT=0` to verify parameter handling without launching WRF.
- Run the PowerShell script with `-RepeatCount 0` if PowerShell is available.

Heavy verification:

- Run the script with the default repeat count when the user wants to collect the final baseline.
