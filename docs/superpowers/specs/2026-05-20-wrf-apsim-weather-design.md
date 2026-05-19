# WRF to APSIM Weather Pipeline Design

## Goal

Build a local, reproducible WRF-based weather generation pipeline for the APSIM crop model at latitude 37.94 and longitude 118.53. The pipeline will run a small WRF validation case first, then support segmented runs for the full APSIM weather period from 2024-10-01 to 2025-12-30.

## Scope

The first implementation focuses on deployment readiness and the end-to-end data contract:

- Configure a local WRF/WPS runtime path using Docker Desktop with WSL2 support.
- Store site, domain, time, and APSIM export settings in a project configuration file.
- Provide WRF/WPS namelist templates for a single 9 km domain centered on 37.94N, 118.53E.
- Convert hourly WRF output into APSIM daily `.met` format.
- Validate the APSIM `.met` format against the provided example file `p0-1-24-25.met`.

The first implementation will not run the entire 456-day WRF simulation by default. It will define a short validation window from 2024-10-01 00:00 to 2024-10-04 00:00, then keep the full period available for monthly or half-month segmented production runs.

## Model Choice

The chosen path is WRF regional simulation rather than a pure stochastic weather generator. This matches the user's preference for WRF and preserves spatially coherent hourly meteorology before daily aggregation for APSIM.

The first domain uses about 9 km grid spacing. Smaller values are finer but more expensive. On this Windows 10 workstation with about 17 GB RAM, 9 km is a practical first domain for local validation. A later nested 3 km domain can be added after the single-domain pipeline works.

## Architecture

The project will use a small Python control layer around WRF/WPS assets:

- `config/site.yaml` stores the site, time windows, domain, and APSIM export fields.
- `docker/` stores the Docker Compose file and a WRF runtime README.
- `wrf/namelists/` stores WPS and WRF namelist templates.
- `src/a_weather/` stores Python package code for configuration loading, APSIM `.met` parsing/writing, and WRF-to-daily aggregation.
- `tests/` stores TDD tests for the APSIM format and configuration contract.
- `data/` is the runtime data area for boundary files, WPS intermediate files, WRF output, and generated APSIM files.

The first deployable artifact is a local project scaffold that can be used once Docker Desktop is running. It will not hide large external downloads behind tests.

## Data Flow

1. The user starts Docker Desktop.
2. The project configuration defines the site and WRF run windows.
3. Boundary data are placed under `data/raw_boundary/`.
4. WPS prepares geogrid, ungrib, and metgrid files.
5. WRF generates hourly `wrfout` NetCDF files.
6. Python reads hourly WRF variables and aggregates them to daily APSIM fields:
   - `radn`: daily incoming shortwave radiation, converted to MJ/m2.
   - `maxt`: daily maximum 2 m air temperature in degrees Celsius.
   - `mint`: daily minimum 2 m air temperature in degrees Celsius.
   - `rain`: daily accumulated precipitation in mm.
7. Python writes APSIM `.met` output with the same header structure as `p0-1-24-25.met`.

## Error Handling

Configuration loading must fail clearly when required fields are missing, dates are invalid, or the requested export fields are unsupported.

APSIM parsing must reject malformed headers, missing units, or data rows that do not contain `year day radn maxt mint rain`.

WRF postprocessing must reject input files missing required variables. It must also clamp tiny negative rainfall values caused by numerical or floating-point noise to zero.

## Testing

Tests will be written before implementation. The initial test set will cover:

- Parsing the provided APSIM `.met` example and confirming location, dates, fields, and record count.
- Writing APSIM `.met` data with the expected header, units, and day-of-year values.
- Loading `config/site.yaml` and validating required deployment settings.
- Aggregating a small synthetic hourly WRF-like dataset into daily APSIM values.

Heavy WRF execution is not part of the automated test suite. It will be verified by explicit deployment commands after Docker Desktop is available.

## Review And Verification

After implementation, the work must pass:

- Unit tests with `pytest`.
- A static import check for the local Python package.
- Docker configuration validation if Docker Desktop is running.
- A code review pass against the design and implementation plan.

## Future Extension

After the first single-domain pipeline works, the next practical extensions are:

- Add a nested 3 km WRF domain around the APSIM point.
- Add ERA5 download automation through CDS API credentials.
- Add monthly WRF run segmentation for 2024-10-01 to 2025-12-30.
- Add bias correction against the provided `.met` file or nearby station observations.
