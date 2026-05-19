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
