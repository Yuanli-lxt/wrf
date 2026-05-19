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
