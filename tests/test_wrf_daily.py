import numpy as np
import pandas as pd
import pytest
import xarray as xr

from a_weather.wrf_daily import aggregate_wrf_dataset


def test_aggregate_wrf_dataset_to_daily_apsim_records():
    times = pd.date_range("2024-10-01T00:00:00", periods=49, freq="h")
    ds = xr.Dataset(
        data_vars={
            "T2": ("Time", np.linspace(280.0, 300.0, 49)),
            "SWDOWN": ("Time", np.full(49, 200.0)),
            "RAINNC": ("Time", np.concatenate([np.linspace(0.0, 4.0, 25), np.linspace(4.0, 9.0, 24)])),
            "RAINC": ("Time", np.zeros(49)),
        },
        coords={"Time": times},
    )

    records = aggregate_wrf_dataset(ds)

    assert len(records) == 2
    assert records[0].date.isoformat() == "2024-10-01"
    assert records[0].mint == pytest.approx(6.85, abs=0.01)
    assert records[0].maxt == pytest.approx(16.43, abs=0.01)
    assert records[0].radn == pytest.approx(17.28, abs=0.01)
    assert records[0].rain == pytest.approx(4.0, abs=0.01)
    assert records[1].rain == pytest.approx(5.0, abs=0.01)


def test_aggregate_wrf_dataset_selects_nearest_grid_cell_for_real_wrf_shape():
    times = pd.date_range("2024-10-01T00:00:00", periods=25, freq="h")
    shape = (25, 2, 2)
    t2 = np.full(shape, 285.0)
    t2[:, 1, 1] = np.linspace(280.0, 300.0, 25)
    rainnc = np.zeros(shape)
    rainnc[:, 1, 1] = np.linspace(0.0, 6.0, 25)
    ds = xr.Dataset(
        data_vars={
            "T2": (("Time", "south_north", "west_east"), t2),
            "SWDOWN": (("Time", "south_north", "west_east"), np.full(shape, 100.0)),
            "RAINNC": (("Time", "south_north", "west_east"), rainnc),
            "RAINC": (("Time", "south_north", "west_east"), np.zeros(shape)),
            "XLAT": (("south_north", "west_east"), np.array([[37.0, 37.0], [38.0, 38.0]])),
            "XLONG": (("south_north", "west_east"), np.array([[118.0, 119.0], [118.0, 119.0]])),
        },
        coords={"Time": times},
    )

    records = aggregate_wrf_dataset(ds, latitude=37.94, longitude=118.53)

    assert len(records) == 1
    assert records[0].mint == pytest.approx(6.85, abs=0.01)
    assert records[0].maxt == pytest.approx(26.02, abs=0.01)
    assert records[0].rain == pytest.approx(6.0, abs=0.01)


def test_aggregate_wrf_dataset_decodes_raw_wrf_times_character_variable():
    time_strings = ["2024-10-01_00:00:00", "2024-10-01_01:00:00", "2024-10-02_00:00:00"]
    times_chars = np.array([list(value) for value in time_strings], dtype="S1")
    ds = xr.Dataset(
        data_vars={
            "Times": (("Time", "DateStrLen"), times_chars),
            "T2": ("Time", np.array([280.0, 282.0, 284.0])),
            "SWDOWN": ("Time", np.array([100.0, 100.0, 0.0])),
            "RAINNC": ("Time", np.array([0.0, 1.0, 3.0])),
            "RAINC": ("Time", np.zeros(3)),
        },
        coords={"Time": np.arange(3)},
    )

    records = aggregate_wrf_dataset(ds)

    assert len(records) == 1
    assert records[0].date.isoformat() == "2024-10-01"
    assert records[0].rain == pytest.approx(3.0, abs=0.01)


def test_aggregate_wrf_dataset_decodes_one_dimensional_wrf_times_strings():
    ds = xr.Dataset(
        data_vars={
            "Times": ("Time", np.array(["2024-10-01_00:00:00", "2024-10-01_01:00:00", "2024-10-02_00:00:00"])),
            "T2": ("Time", np.array([280.0, 282.0, 284.0])),
            "SWDOWN": ("Time", np.array([100.0, 100.0, 0.0])),
            "RAINNC": ("Time", np.array([0.0, 1.0, 3.0])),
            "RAINC": ("Time", np.zeros(3)),
        },
        coords={"Time": np.arange(3)},
    )

    records = aggregate_wrf_dataset(ds)

    assert len(records) == 1
    assert records[0].date.isoformat() == "2024-10-01"
    assert records[0].rain == pytest.approx(3.0, abs=0.01)
