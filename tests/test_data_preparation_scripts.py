from pathlib import Path


def test_prepare_geog_script_uses_official_wps_low_res_package():
    text = Path("scripts/prepare_geog.ps1").read_text(encoding="utf-8")

    assert "https://www2.mmm.ucar.edu/wrf/src/wps_files/geog_low_res_mandatory.tar.gz" in text
    assert "data/geog" in text
    assert "tar -xzf" in text


def test_prepare_gfs_boundary_script_downloads_validation_window_files():
    text = Path("scripts/prepare_gfs_boundary.ps1").read_text(encoding="utf-8")

    assert "noaa-gfs-bdp-pds.s3.amazonaws.com" in text
    assert "$ForecastHours = 0..72" in text
    assert "Where-Object { $_ % 3 -eq 0 }" in text
    assert "gfs.t${Cycle}z.pgrb2.${Resolution}.f" in text
    assert "data/raw_boundary" in text
