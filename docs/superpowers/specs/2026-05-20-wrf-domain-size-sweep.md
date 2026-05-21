# WRF Domain Size Sweep Design

## Goal

Find the smallest practical WRF domain for the APSIM point at 37.94N, 118.53E without abandoning WRF regional simulation. Compare 80x80, 60x60, and 50x50 domains for runtime, stability, and point-scale APSIM `.met` differences.

## Experiment Matrix

Domain sizes:

- 80x80
- 60x60
- 50x50

Windows:

- 24h: 2024-10-01 00:00 to 2024-10-02 00:00
- 72h: 2024-10-01 00:00 to 2024-10-04 00:00

The WRF grid spacing remains 9 km. Only `e_we` and `e_sn` change. Each domain size must have matching WPS `met_em` files because WRF cannot use `met_em` files from a different grid size.

## Architecture

Add reusable domain-size scripts:

- `scripts/run_wps_domain_size.sh`: runs WPS for one `DOMAIN_SIZE`.
- `scripts/run_wrf_domain_size.sh`: runs WRF for one `DOMAIN_SIZE` and one `WINDOW_HOURS`.
- `scripts/export_domain_size_met.py`: exports APSIM `.met` for one domain/window.
- `scripts/benchmark_domain_size_sweep.sh`: orchestrates WPS, WRF, export, and timing.
- `scripts/summarize_domain_size_sweep.py`: compares generated `.met` outputs against the 80x80 reference.

Outputs are isolated:

- WPS: `data/wps/domain_{size}_validation_20241001_00`
- WRF: `data/wrfout/domain_{size}_{window}h_validation_20241001_00`
- APSIM: `data/generated/apsim/domain_{size}_{window}h_validation_wrf_20241001.met`
- Timings: `data/generated/benchmarks/domain_size_sweep.csv`
- Summary: `data/generated/benchmarks/domain_size_sweep_summary.csv`

## Stability Criteria

A case is considered stable if:

- WPS exits with code 0.
- WRF exits with code 0.
- WRF writes the expected final `wrfout` boundary timestamp.
- APSIM export exits with code 0.
- The exported `.met` contains complete days only: one day for 24h and three days for 72h.

## Comparison Metrics

For each non-80 domain, compare against the matching 80x80 `.met` output:

- Mean absolute difference for `radn`, `maxt`, `mint`, `rain`.
- Maximum absolute difference for `radn`, `maxt`, `mint`, `rain`.
- Runtime for WPS, WRF, and export.

## Verification

Automated tests inspect scripts and output contracts without running WRF. Heavy verification runs the sweep explicitly.
