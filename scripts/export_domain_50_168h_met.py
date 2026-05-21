from __future__ import annotations

from datetime import date
import shutil
import warnings
from pathlib import Path

import xarray as xr

from a_weather.apsim_met import ApsimMet, write_met_file
from a_weather.config import load_site_config
from a_weather.wrf_daily import aggregate_wrf_dataset


SOURCE_DIR = Path("data/wrfout/domain_50_168h_validation_20241001_00")
ASCII_DIR = Path("data/generated/wrfout_domain_50_168h_ascii")
OUTPUT_PATH = Path("data/generated/apsim/domain_50_168h_validation_wrf_20241001.met")


def main() -> None:
    warnings.filterwarnings("ignore")
    cfg = load_site_config("config/site.yaml")
    safe_files = _ascii_wrfout_files()
    parts = []
    for path in safe_files:
        with xr.open_dataset(path, engine="netcdf4") as ds:
            parts.append(ds[["Times", "T2", "SWDOWN", "RAINNC", "RAINC", "XLAT", "XLONG"]].load())
    combined = xr.concat(parts, dim="Time")
    records = aggregate_wrf_dataset(combined, latitude=cfg.site.latitude, longitude=cfg.site.longitude)

    expected_records = 7
    if len(records) != expected_records:
        raise ValueError(f"expected {expected_records} APSIM records, got {len(records)}")
    if records[0].date != date.fromisoformat("2024-10-01") or records[-1].date != date.fromisoformat("2024-10-07"):
        raise ValueError("expected APSIM dates from 2024-10-01 to 2024-10-07")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_met_file(
        ApsimMet(
            latitude=cfg.site.latitude,
            longitude=cfg.site.longitude,
            tav=cfg.apsim.tav,
            amp=cfg.apsim.amp,
            records=records,
        ),
        OUTPUT_PATH,
    )
    print(f"Wrote {len(records)} APSIM records to {OUTPUT_PATH}")


def _ascii_wrfout_files() -> list[Path]:
    source_files = sorted(SOURCE_DIR.glob("wrfout_d01_*"))
    if not source_files:
        raise FileNotFoundError(f"No wrfout files found in {SOURCE_DIR}")
    ASCII_DIR.mkdir(parents=True, exist_ok=True)
    ascii_files: list[Path] = []
    for index, source in enumerate(source_files):
        target = ASCII_DIR / f"wrfout_{index:03d}.nc"
        if not target.exists() or target.stat().st_size != source.stat().st_size:
            shutil.copy2(source, target)
        ascii_files.append(target)
    return ascii_files


if __name__ == "__main__":
    main()
