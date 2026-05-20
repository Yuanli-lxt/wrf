# WRF APSIM Weather Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local WRF deployment scaffold and APSIM `.met` postprocessing package for the 37.94N, 118.53E site.

**Architecture:** A small Python package validates project configuration, parses/writes APSIM weather files, and aggregates WRF-like hourly data to APSIM daily fields. Docker Compose and namelist templates provide the local WRF/WPS deployment path while keeping heavy WRF execution outside unit tests.

**Tech Stack:** Python 3.11, pytest, PyYAML, xarray, netCDF4, Docker Desktop with WSL2, WRF/WPS namelist templates.

---

## File Structure

- Create `pyproject.toml` to define package metadata and test dependencies.
- Create `config/site.yaml` for the APSIM site, validation window, full production window, and WRF domain settings.
- Create `src/a_weather/__init__.py` for package exports.
- Create `src/a_weather/config.py` for configuration loading and validation.
- Create `src/a_weather/apsim_met.py` for APSIM `.met` parsing and writing.
- Create `src/a_weather/wrf_daily.py` for hourly WRF-like dataset aggregation.
- Create `tests/test_config.py` for configuration behavior.
- Create `tests/test_apsim_met.py` for APSIM example parsing and writing behavior.
- Create `tests/test_wrf_daily.py` for synthetic hourly aggregation behavior.
- Create `docker/docker-compose.yml` for local WRF/WPS runtime mounting.
- Create `docker/README.md` for Docker Desktop startup and runtime commands.
- Create `wrf/namelists/namelist.wps.template` for the 9 km WPS domain.
- Create `wrf/namelists/namelist.input.template` for the WRF validation run.
- Create `scripts/verify_environment.ps1` for local environment checks.
- Create `.gitignore` for generated data, Python caches, and WRF runtime outputs.

## Task 1: Python Project And Config

**Files:**
- Create: `pyproject.toml`
- Create: `config/site.yaml`
- Create: `src/a_weather/__init__.py`
- Create: `src/a_weather/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write the failing config tests**

```python
from datetime import date, datetime

import pytest

from a_weather.config import load_site_config


def test_load_site_config_has_expected_site_and_windows():
    cfg = load_site_config("config/site.yaml")

    assert cfg.site.latitude == pytest.approx(37.94)
    assert cfg.site.longitude == pytest.approx(118.53)
    assert cfg.validation_window.start == datetime(2024, 10, 1, 0)
    assert cfg.validation_window.end == datetime(2024, 10, 4, 0)
    assert cfg.full_window.start.date() == date(2024, 10, 1)
    assert cfg.full_window.end.date() == date(2025, 12, 30)
    assert cfg.domain.dx_m == 9000
    assert cfg.domain.dy_m == 9000
    assert cfg.apsim.fields == ["year", "day", "radn", "maxt", "mint", "rain"]


def test_load_site_config_rejects_missing_required_section(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("site:\n  latitude: 37.94\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required section"):
        load_site_config(path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'a_weather'`.

- [ ] **Step 3: Write minimal implementation**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "a-weather"
version = "0.1.0"
description = "WRF to APSIM weather generation pipeline"
requires-python = ">=3.11"
dependencies = [
  "PyYAML>=6.0.1",
  "xarray>=2024.1.0",
  "netCDF4>=1.6.5",
  "numpy>=1.26.0",
]

[project.optional-dependencies]
test = ["pytest>=8.0.0"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

Create `config/site.yaml`:

```yaml
site:
  name: dongying_yellow_river_delta
  latitude: 37.94
  longitude: 118.53
  timezone: Asia/Shanghai

validation_window:
  start: "2024-10-01T00:00:00"
  end: "2024-10-04T00:00:00"

full_window:
  start: "2024-10-01T00:00:00"
  end: "2025-12-30T23:00:00"

domain:
  center_latitude: 37.94
  center_longitude: 118.53
  dx_m: 9000
  dy_m: 9000
  e_we: 80
  e_sn: 80
  time_step_seconds: 54
  output_interval_minutes: 60

apsim:
  tav: 14.53
  amp: 29.84
  fields:
    - year
    - day
    - radn
    - maxt
    - mint
    - rain
```

Create `src/a_weather/__init__.py`:

```python
"""WRF to APSIM weather pipeline helpers."""
```

Create `src/a_weather/config.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Site:
    name: str
    latitude: float
    longitude: float
    timezone: str


@dataclass(frozen=True)
class TimeWindow:
    start: datetime
    end: datetime


@dataclass(frozen=True)
class Domain:
    center_latitude: float
    center_longitude: float
    dx_m: int
    dy_m: int
    e_we: int
    e_sn: int
    time_step_seconds: int
    output_interval_minutes: int


@dataclass(frozen=True)
class ApsimExport:
    tav: float
    amp: float
    fields: list[str]


@dataclass(frozen=True)
class SiteConfig:
    site: Site
    validation_window: TimeWindow
    full_window: TimeWindow
    domain: Domain
    apsim: ApsimExport


def load_site_config(path: str | Path) -> SiteConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("configuration must be a mapping")

    required_sections = ["site", "validation_window", "full_window", "domain", "apsim"]
    missing = [section for section in required_sections if section not in raw]
    if missing:
        raise ValueError(f"missing required section: {', '.join(missing)}")

    return SiteConfig(
        site=_site(raw["site"]),
        validation_window=_window(raw["validation_window"]),
        full_window=_window(raw["full_window"]),
        domain=_domain(raw["domain"]),
        apsim=_apsim(raw["apsim"]),
    )


def _window(raw: dict[str, Any]) -> TimeWindow:
    start = datetime.fromisoformat(raw["start"])
    end = datetime.fromisoformat(raw["end"])
    if end <= start:
        raise ValueError("time window end must be after start")
    return TimeWindow(start=start, end=end)


def _site(raw: dict[str, Any]) -> Site:
    return Site(
        name=str(raw["name"]),
        latitude=float(raw["latitude"]),
        longitude=float(raw["longitude"]),
        timezone=str(raw["timezone"]),
    )


def _domain(raw: dict[str, Any]) -> Domain:
    return Domain(
        center_latitude=float(raw["center_latitude"]),
        center_longitude=float(raw["center_longitude"]),
        dx_m=int(raw["dx_m"]),
        dy_m=int(raw["dy_m"]),
        e_we=int(raw["e_we"]),
        e_sn=int(raw["e_sn"]),
        time_step_seconds=int(raw["time_step_seconds"]),
        output_interval_minutes=int(raw["output_interval_minutes"]),
    )


def _apsim(raw: dict[str, Any]) -> ApsimExport:
    fields = [str(field) for field in raw["fields"]]
    expected = ["year", "day", "radn", "maxt", "mint", "rain"]
    if fields != expected:
        raise ValueError(f"unsupported APSIM fields: {fields}")
    return ApsimExport(tav=float(raw["tav"]), amp=float(raw["amp"]), fields=fields)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml config/site.yaml src/a_weather/__init__.py src/a_weather/config.py tests/test_config.py
git commit -m "feat: add site configuration contract"
```

## Task 2: APSIM MET Parser And Writer

**Files:**
- Create: `src/a_weather/apsim_met.py`
- Test: `tests/test_apsim_met.py`

- [ ] **Step 1: Write the failing APSIM tests**

```python
from datetime import date

import pytest

from a_weather.apsim_met import ApsimMet, DailyWeather, parse_met_file, write_met_file


def test_parse_example_met_file_reads_header_and_dates():
    met = parse_met_file("p0-1-24-25.met")

    assert met.latitude == pytest.approx(37.94)
    assert met.longitude == pytest.approx(118.53)
    assert met.tav == pytest.approx(14.53)
    assert met.amp == pytest.approx(29.84)
    assert len(met.records) == 456
    assert met.records[0].date == date(2024, 10, 1)
    assert met.records[-1].date == date(2025, 12, 30)
    assert met.records[0].radn == pytest.approx(17.67)
    assert met.records[0].maxt == pytest.approx(20.68)
    assert met.records[0].mint == pytest.approx(7.58)
    assert met.records[0].rain == pytest.approx(0.0)


def test_write_met_file_preserves_apsim_header_and_day_of_year(tmp_path):
    met = ApsimMet(
        latitude=37.94,
        longitude=118.53,
        tav=14.53,
        amp=29.84,
        records=[
            DailyWeather(date=date(2024, 10, 1), radn=17.67, maxt=20.68, mint=7.58, rain=0.0),
            DailyWeather(date=date(2024, 10, 2), radn=19.41, maxt=19.12, mint=6.11, rain=0.0),
        ],
    )
    path = tmp_path / "out.met"

    write_met_file(met, path)

    text = path.read_text(encoding="utf-8")
    assert "[weather.met.weather]" in text
    assert "latitude = 37.94 (dec deg)" in text
    assert "year   day   radn   maxt   mint   rain" in text
    assert "(MJ/m2)" in text
    assert "2024   275" in text
    assert "2024   276" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_apsim_met.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'a_weather.apsim_met'`.

- [ ] **Step 3: Write minimal implementation**

```python
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


@dataclass(frozen=True)
class DailyWeather:
    date: date
    radn: float
    maxt: float
    mint: float
    rain: float


@dataclass(frozen=True)
class ApsimMet:
    latitude: float
    longitude: float
    tav: float
    amp: float
    records: list[DailyWeather]


def parse_met_file(path: str | Path) -> ApsimMet:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    latitude = _header_float(lines, "latitude")
    longitude = _header_float(lines, "longitude")
    tav = _header_float(lines, "tav")
    amp = _header_float(lines, "amp")

    field_index = next(
        (idx for idx, line in enumerate(lines) if line.split() == ["year", "day", "radn", "maxt", "mint", "rain"]),
        None,
    )
    if field_index is None:
        raise ValueError("missing APSIM field header")

    records: list[DailyWeather] = []
    for line in lines[field_index + 2 :]:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 6:
            raise ValueError(f"malformed APSIM data row: {line}")
        year, doy = int(parts[0]), int(parts[1])
        records.append(
            DailyWeather(
                date=datetime.strptime(f"{year} {doy}", "%Y %j").date(),
                radn=float(parts[2]),
                maxt=float(parts[3]),
                mint=float(parts[4]),
                rain=max(0.0, float(parts[5])),
            )
        )

    return ApsimMet(latitude=latitude, longitude=longitude, tav=tav, amp=amp, records=records)


def write_met_file(met: ApsimMet, path: str | Path) -> None:
    lines = [
        "[weather.met.weather]",
        f"latitude = {met.latitude:.2f} (dec deg)",
        f"longitude = {met.longitude:.2f} (dec deg)",
        f"tav = {met.tav:.2f} (oC) ! annual average ambient temperature",
        f"amp = {met.amp:.2f} (oC) ! annual amplitude in mean monthly temperature",
        "year   day   radn   maxt   mint   rain",
        " ()    ()   (MJ/m2) (oC)   (oC)   (mm)",
    ]
    for record in met.records:
        doy = record.date.timetuple().tm_yday
        lines.append(
            f"{record.date.year:<6d} {doy:<5d} "
            f"{record.radn:<7.2f} {record.maxt:<6.2f} {record.mint:<6.2f} {record.rain:<6.2f}"
        )
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _header_float(lines: list[str], key: str) -> float:
    pattern = re.compile(rf"^{re.escape(key)}\s*=\s*([-+]?\d+(?:\.\d+)?)")
    for line in lines:
        match = pattern.search(line)
        if match:
            return float(match.group(1))
    raise ValueError(f"missing APSIM header value: {key}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_apsim_met.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/a_weather/apsim_met.py tests/test_apsim_met.py
git commit -m "feat: add apsim met parser and writer"
```

## Task 3: WRF Hourly To APSIM Daily Aggregation

**Files:**
- Create: `src/a_weather/wrf_daily.py`
- Test: `tests/test_wrf_daily.py`

- [ ] **Step 1: Write the failing aggregation test**

```python
import numpy as np
import pandas as pd
import pytest
import xarray as xr

from a_weather.wrf_daily import aggregate_wrf_dataset


def test_aggregate_wrf_dataset_to_daily_apsim_records():
    times = pd.date_range("2024-10-01T00:00:00", periods=48, freq="h")
    ds = xr.Dataset(
        data_vars={
            "T2": ("Time", np.linspace(280.0, 300.0, 48)),
            "SWDOWN": ("Time", np.full(48, 200.0)),
            "RAINNC": ("Time", np.concatenate([np.linspace(0.0, 4.0, 24), np.linspace(4.0, 9.0, 24)])),
            "RAINC": ("Time", np.zeros(48)),
        },
        coords={"Time": times},
    )

    records = aggregate_wrf_dataset(ds)

    assert len(records) == 2
    assert records[0].date.isoformat() == "2024-10-01"
    assert records[0].mint == pytest.approx(6.85, abs=0.01)
    assert records[0].maxt == pytest.approx(16.64, abs=0.01)
    assert records[0].radn == pytest.approx(17.28, abs=0.01)
    assert records[0].rain == pytest.approx(4.0, abs=0.01)
    assert records[1].rain == pytest.approx(5.0, abs=0.01)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_wrf_daily.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'a_weather.wrf_daily'`.

- [ ] **Step 3: Write minimal implementation**

```python
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import xarray as xr

from a_weather.apsim_met import DailyWeather


def aggregate_wrf_dataset(ds: xr.Dataset) -> list[DailyWeather]:
    required = {"T2", "SWDOWN", "RAINNC", "RAINC"}
    missing = sorted(required.difference(ds.data_vars))
    if missing:
        raise ValueError(f"WRF dataset missing required variables: {', '.join(missing)}")
    if "Time" not in ds.coords:
        raise ValueError("WRF dataset missing Time coordinate")

    frame = pd.DataFrame(
        {
            "time": pd.to_datetime(ds["Time"].values),
            "t2_c": np.asarray(ds["T2"].values, dtype=float) - 273.15,
            "swdown_w_m2": np.asarray(ds["SWDOWN"].values, dtype=float),
            "rain_total": np.asarray(ds["RAINNC"].values, dtype=float) + np.asarray(ds["RAINC"].values, dtype=float),
        }
    )
    frame["day"] = frame["time"].dt.date

    records: list[DailyWeather] = []
    for day, group in frame.groupby("day", sort=True):
        rain_delta = float(group["rain_total"].iloc[-1] - group["rain_total"].iloc[0])
        rain = 0.0 if abs(rain_delta) < 1e-9 else max(0.0, rain_delta)
        radn = float(group["swdown_w_m2"].sum() * 3600.0 / 1_000_000.0)
        records.append(
            DailyWeather(
                date=day if isinstance(day, date) else pd.Timestamp(day).date(),
                radn=radn,
                maxt=float(group["t2_c"].max()),
                mint=float(group["t2_c"].min()),
                rain=rain,
            )
        )
    return records
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_wrf_daily.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/a_weather/wrf_daily.py tests/test_wrf_daily.py
git commit -m "feat: aggregate wrf hourly output to apsim daily weather"
```

## Task 4: WRF Deployment Scaffold

**Files:**
- Create: `docker/docker-compose.yml`
- Create: `docker/README.md`
- Create: `wrf/namelists/namelist.wps.template`
- Create: `wrf/namelists/namelist.input.template`
- Create: `scripts/verify_environment.ps1`
- Create: `.gitignore`
- Test: `tests/test_deployment_files.py`

- [ ] **Step 1: Write the failing deployment file tests**

```python
from pathlib import Path


def test_docker_compose_declares_wrf_service_and_mounts_project_dirs():
    text = Path("docker/docker-compose.yml").read_text(encoding="utf-8")

    assert "wrf:" in text
    assert "NCAR/WRF" in text or "wrf" in text.lower()
    assert "../data:/work/data" in text
    assert "../wrf:/work/wrf" in text


def test_namelists_define_single_9km_domain_centered_on_site():
    wps = Path("wrf/namelists/namelist.wps.template").read_text(encoding="utf-8")
    wrf = Path("wrf/namelists/namelist.input.template").read_text(encoding="utf-8")

    assert "ref_lat" in wps
    assert "37.94" in wps
    assert "ref_lon" in wps
    assert "118.53" in wps
    assert "dx = 9000" in wps
    assert "dy = 9000" in wps
    assert "time_step = 54" in wrf
    assert "history_interval = 60" in wrf
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_deployment_files.py -v`
Expected: FAIL because deployment files do not exist.

- [ ] **Step 3: Write minimal deployment scaffold**

Create `docker/docker-compose.yml`:

```yaml
services:
  wrf:
    image: ghcr.io/wrf-model/wrf:latest
    container_name: a-weather-wrf
    working_dir: /work
    stdin_open: true
    tty: true
    volumes:
      - ../data:/work/data
      - ../wrf:/work/wrf
      - ../config:/work/config
      - ../scripts:/work/scripts
```

Create `docker/README.md`:

```markdown
# Local WRF Runtime

Start Docker Desktop before using this runtime.

Validate the Compose file:

```powershell
docker compose -f docker/docker-compose.yml config
```

Open a shell in the WRF container:

```powershell
docker compose -f docker/docker-compose.yml run --rm wrf bash
```

The first validation target is 2024-10-01 00:00 to 2024-10-04 00:00 for the site at 37.94N, 118.53E. Place boundary data under `data/raw_boundary/` before running WPS.
```

Create `wrf/namelists/namelist.wps.template`:

```text
&share
 wrf_core = 'ARW',
 max_dom = 1,
 start_date = '2024-10-01_00:00:00',
 end_date   = '2024-10-04_00:00:00',
 interval_seconds = 21600,
 io_form_geogrid = 2,
/

&geogrid
 parent_id         = 1,
 parent_grid_ratio = 1,
 i_parent_start    = 1,
 j_parent_start    = 1,
 e_we              = 80,
 e_sn              = 80,
 geog_data_res     = 'default',
 dx = 9000,
 dy = 9000,
 map_proj = 'lambert',
 ref_lat   = 37.94,
 ref_lon   = 118.53,
 truelat1  = 30.0,
 truelat2  = 60.0,
 stand_lon = 118.53,
 geog_data_path = '/work/data/geog'
/

&ungrib
 out_format = 'WPS',
 prefix = 'FILE',
/

&metgrid
 fg_name = 'FILE',
 io_form_metgrid = 2,
/
```

Create `wrf/namelists/namelist.input.template`:

```text
&time_control
 run_days                            = 3,
 run_hours                           = 0,
 start_year                          = 2024,
 start_month                         = 10,
 start_day                           = 01,
 start_hour                          = 00,
 end_year                            = 2024,
 end_month                           = 10,
 end_day                             = 04,
 end_hour                            = 00,
 interval_seconds                    = 21600,
 input_from_file                     = .true.,
 history_interval                    = 60,
 frames_per_outfile                  = 24,
 restart                             = .false.,
 io_form_history                     = 2,
 io_form_restart                     = 2,
 io_form_input                       = 2,
 io_form_boundary                    = 2,
/

&domains
 time_step                           = 54,
 max_dom                             = 1,
 e_we                                = 80,
 e_sn                                = 80,
 e_vert                              = 35,
 dx                                  = 9000,
 dy                                  = 9000,
 p_top_requested                     = 5000,
 num_metgrid_levels                  = 34,
 num_metgrid_soil_levels             = 4,
/
```

Create `scripts/verify_environment.ps1`:

```powershell
$ErrorActionPreference = "Stop"

Write-Host "Python:"
python --version

Write-Host "Docker:"
docker --version

Write-Host "Docker Compose config:"
docker compose -f docker/docker-compose.yml config | Out-Null
Write-Host "OK"
```

Create `.gitignore`:

```gitignore
__pycache__/
.pytest_cache/
*.pyc
.venv/
data/raw_boundary/
data/geog/
data/wps/
data/wrfout/
data/generated/
wrf/run/
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_deployment_files.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docker docker/README.md wrf/namelists scripts/verify_environment.ps1 .gitignore tests/test_deployment_files.py
git commit -m "feat: add wrf docker deployment scaffold"
```

## Task 5: Final Verification And Review

**Files:**
- Modify: none unless review finds a defect.

- [ ] **Step 1: Run the full test suite**

Run: `pytest -v`
Expected: all tests PASS.

- [ ] **Step 2: Run import verification**

Run: `python -c "from a_weather.config import load_site_config; from a_weather.apsim_met import parse_met_file; from a_weather.wrf_daily import aggregate_wrf_dataset; print('imports ok')"`
Expected: prints `imports ok`.

- [ ] **Step 3: Run Docker Compose validation**

Run: `docker compose -f docker/docker-compose.yml config`
Expected: exit code 0 if Docker Desktop is running. If Docker Desktop is not running, record the Docker daemon connection failure and leave the command for the user to rerun after starting Docker Desktop.

- [ ] **Step 4: Request code review**

Review description: "Built local WRF deployment scaffold and Python APSIM weather postprocessing package."

Review requirements: "Must satisfy the design in `docs/superpowers/specs/2026-05-20-wrf-apsim-weather-design.md` and this implementation plan. Check correctness of APSIM date/format handling, WRF daily aggregation assumptions, Docker scaffold clarity, and test coverage."

- [ ] **Step 5: Fix Critical or Important review findings**

If the review finds a defect, write a failing test reproducing it, verify the test fails, fix the implementation, rerun the relevant test, then rerun the full verification suite.

- [ ] **Step 6: Final status**

Report implemented files, verification evidence, Docker status, and the next command the user can run after starting Docker Desktop.

## Self-Review

- Spec coverage: Tasks cover config, APSIM `.met` parsing/writing, WRF hourly aggregation, Docker/WPS/WRF deployment scaffold, verification, and review.
- Placeholder scan: The plan contains no unresolved placeholders.
- Type consistency: `DailyWeather`, `ApsimMet`, `SiteConfig`, and `aggregate_wrf_dataset` names are consistent across tests and implementation.
