from datetime import date

import pytest

from a_weather.apsim_met import ApsimMet, DailyWeather, parse_met_file, write_met_file


def test_parse_example_met_file_reads_header_and_dates():
    met = parse_met_file("tests/fixtures/p0-1-24-25.met")

    assert met.latitude == pytest.approx(37.94)
    assert met.longitude == pytest.approx(118.53)
    assert met.tav == pytest.approx(14.53)
    assert met.amp == pytest.approx(29.84)
    assert len(met.records) == 456
    assert met.records[0].date == date(2024, 10, 1)
    assert met.records[-1].date == date(2025, 12, 30)
    assert met.records[0].radn == pytest.approx(17.67)
    assert met.records[0].maxt == pytest.approx(20.68)
    assert met.records[0].mint == pytest.approx(7.58)
    assert met.records[0].rain == pytest.approx(0.0)


def test_write_met_file_preserves_apsim_header_and_day_of_year(tmp_path):
    met = ApsimMet(
        latitude=37.94,
        longitude=118.53,
        tav=14.53,
        amp=29.84,
        records=[
            DailyWeather(date=date(2024, 10, 1), radn=17.67, maxt=20.68, mint=7.58, rain=0.0),
            DailyWeather(date=date(2024, 10, 2), radn=19.41, maxt=19.12, mint=6.11, rain=0.0),
        ],
    )
    path = tmp_path / "out.met"

    write_met_file(met, path)

    text = path.read_text(encoding="utf-8")
    assert "[weather.met.weather]" in text
    assert "latitude = 37.94 (dec deg)" in text
    assert "year   day   radn   maxt   mint   rain" in text
    assert "(MJ/m2)" in text
    assert "2024   275" in text
    assert "2024   276" in text


def test_parse_met_file_rejects_missing_units_row(tmp_path):
    path = tmp_path / "missing-units.met"
    path.write_text(
        "\n".join(
            [
                "[weather.met.weather]",
                "latitude = 37.94 (dec deg)",
                "longitude = 118.53 (dec deg)",
                "tav = 14.53 (oC)",
                "amp = 29.84 (oC)",
                "year   day   radn   maxt   mint   rain",
                "2024   275   17.67   20.68  7.58   0.00",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing APSIM units row"):
        parse_met_file(path)


def test_parse_met_file_rejects_day_of_year_outside_year(tmp_path):
    path = tmp_path / "bad-doy.met"
    path.write_text(
        "\n".join(
            [
                "[weather.met.weather]",
                "latitude = 37.94 (dec deg)",
                "longitude = 118.53 (dec deg)",
                "tav = 14.53 (oC)",
                "amp = 29.84 (oC)",
                "year   day   radn   maxt   mint   rain",
                " ()    ()   (MJ/m2) (oC)   (oC)   (mm)",
                "2023   366   17.67   20.68  7.58   0.00",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid day-of-year"):
        parse_met_file(path)
