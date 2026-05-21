from pathlib import Path


def test_prepare_geog_script_uses_official_wps_low_res_package():
    text = Path("scripts/prepare_geog.ps1").read_text(encoding="utf-8")

    assert "https://www2.mmm.ucar.edu/wrf/src/wps_files/geog_low_res_mandatory.tar.gz" in text
    assert "data/geog" in text
    assert "tar -xzf" in text
    assert "Assert-ArchiveSize" in text
    assert "Test-GeogReady" in text
    assert "WPS_GEOG_LOW_RES" in text
    assert "topo_gmted2010_5m" in text
    assert "modis_landuse_20class_5m_with_lakes" in text


def test_prepare_gfs_boundary_script_downloads_validation_window_files():
    text = Path("scripts/prepare_gfs_boundary.ps1").read_text(encoding="utf-8")

    assert "noaa-gfs-bdp-pds.s3.amazonaws.com" in text
    assert "$MaxForecastHour = 72" in text
    assert "$ForecastHours = 0..$MaxForecastHour" in text
    assert "Where-Object { $_ % 3 -eq 0 }" in text
    assert "gfs.t${Cycle}z.pgrb2.${Resolution}.f" in text
    assert "data/raw_boundary" in text


def test_prepare_gfs_boundary_bash_script_supports_168h_download_window():
    text = Path("scripts/prepare_gfs_boundary.sh").read_text(encoding="utf-8")

    assert "MAX_FORECAST_HOUR=${MAX_FORECAST_HOUR:-72}" in text
    assert "noaa-gfs-bdp-pds.s3.amazonaws.com" in text
    assert "seq 0 3 \"$MAX_FORECAST_HOUR\"" in text
    assert "gfs.t${CYCLE}z.pgrb2.${RESOLUTION}.f" in text
    assert "curl -fsSLI" in text
    assert "curl -fL" in text
    assert "data/raw_boundary" in text
