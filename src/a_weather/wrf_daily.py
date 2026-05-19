from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import xarray as xr

from a_weather.apsim_met import DailyWeather


def aggregate_wrf_dataset(ds: xr.Dataset, latitude: float | None = None, longitude: float | None = None) -> list[DailyWeather]:
    required = {"T2", "SWDOWN", "RAINNC", "RAINC"}
    missing = sorted(required.difference(ds.data_vars))
    if missing:
        raise ValueError(f"WRF dataset missing required variables: {', '.join(missing)}")
    if "Time" not in ds.coords:
        raise ValueError("WRF dataset missing Time coordinate")

    point = _select_point(ds, latitude=latitude, longitude=longitude)
    frame = pd.DataFrame(
        {
            "time": pd.to_datetime(point["Time"].values),
            "t2_c": np.asarray(point["T2"].values, dtype=float) - 273.15,
            "swdown_w_m2": np.asarray(point["SWDOWN"].values, dtype=float),
            "rain_total": np.asarray(point["RAINNC"].values, dtype=float) + np.asarray(point["RAINC"].values, dtype=float),
        }
    )
    frame["day"] = frame["time"].dt.date

    records: list[DailyWeather] = []
    days = sorted(frame["day"].unique())
    for day in days:
        start = pd.Timestamp(day)
        end = start + pd.Timedelta(days=1)
        group = frame[(frame["time"] >= start) & (frame["time"] < end)]
        next_boundary = frame[frame["time"] == end]
        if group.empty or next_boundary.empty:
            continue
        start_boundary = group[group["time"] == start]
        if start_boundary.empty:
            continue
        rain_delta = float(next_boundary["rain_total"].iloc[0] - start_boundary["rain_total"].iloc[0])
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


def _select_point(ds: xr.Dataset, latitude: float | None, longitude: float | None) -> xr.Dataset:
    sample = ds["T2"]
    spatial_dims = [dim for dim in sample.dims if dim != "Time"]
    if not spatial_dims:
        return ds
    if latitude is None or longitude is None:
        raise ValueError("latitude and longitude are required for gridded WRF datasets")
    if "XLAT" not in ds or "XLONG" not in ds:
        raise ValueError("gridded WRF dataset missing XLAT or XLONG")

    lat = ds["XLAT"]
    lon = ds["XLONG"]
    if "Time" in lat.dims:
        lat = lat.isel(Time=0)
    if "Time" in lon.dims:
        lon = lon.isel(Time=0)
    distance = (lat - latitude) ** 2 + (lon - longitude) ** 2
    flat_index = int(np.nanargmin(distance.values))
    y_index, x_index = np.unravel_index(flat_index, distance.shape)
    indexers = {distance.dims[0]: y_index, distance.dims[1]: x_index}
    return ds.isel(indexers)
