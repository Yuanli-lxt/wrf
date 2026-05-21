from __future__ import annotations

import os
import shutil
import warnings
from pathlib import Path

import xarray as xr

from a_weather.apsim_met import ApsimMet, write_met_file
from a_weather.config import load_site_config
from a_weather.wrf_daily import aggregate_wrf_dataset


def main() -> None:
    warnings.filterwarnings("ignore")
    domain_size = int(os.environ.get("DOMAIN_SIZE", "80"))
    window_hours = int(os.environ.get("WINDOW_HOURS", "24"))
    source_dir = Path(f"data/wrfout/domain_{domain_size}_{window_hours}h_validation_20241001_00")
    ascii_dir = Path(f"data/generated/wrfout_domain_{domain_size}_{window_hours}h_ascii")
    output_path = Path(f"data/generated/apsim/domain_{domain_size}_{window_hours}h_validation_wrf_20241001.met")

    cfg = load_site_config("config/site.yaml")
    safe_files = _ascii_wrfout_files(source_dir, ascii_dir)
    parts = []
    for path in safe_files:
        with xr.open_dataset(path, engine="netcdf4") as ds:
            parts.append(ds[["Times", "T2", "SWDOWN", "RAINNC", "RAINC", "XLAT", "XLONG"]].load())
    combined = xr.concat(parts, dim="Time")
    records = aggregate_wrf_dataset(combined, latitude=cfg.site.latitude, longitude=cfg.site.longitude)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_met_file(
        ApsimMet(
            latitude=cfg.site.latitude,
            longitude=cfg.site.longitude,
            tav=cfg.apsim.tav,
            amp=cfg.apsim.amp,
            records=records,
        ),
        output_path,
    )
    print(f"Wrote {len(records)} APSIM records to {output_path}")


def _ascii_wrfout_files(source_dir: Path, ascii_dir: Path) -> list[Path]:
    source_files = sorted(source_dir.glob("wrfout_d01_*"))
    if not source_files:
        raise FileNotFoundError(f"No wrfout files found in {source_dir}")
    ascii_dir.mkdir(parents=True, exist_ok=True)
    ascii_files: list[Path] = []
    for index, source in enumerate(source_files):
        target = ascii_dir / f"wrfout_{index:03d}.nc"
        if not target.exists() or target.stat().st_size != source.stat().st_size:
            shutil.copy2(source, target)
        ascii_files.append(target)
    return ascii_files


if __name__ == "__main__":
    main()
