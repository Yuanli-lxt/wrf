from __future__ import annotations

import shutil
import warnings
from pathlib import Path

import xarray as xr

from a_weather.apsim_met import ApsimMet, write_met_file
from a_weather.config import load_site_config
from a_weather.wrf_daily import aggregate_wrf_dataset


SOURCE_DIR = Path("data/wrfout/validation_20241001_00_72h")
ASCII_DIR = Path("data/generated/wrfout_validation_72h_ascii")
OUTPUT_PATH = Path("data/generated/apsim/validation_wrf_20241001_72h.met")


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
