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
