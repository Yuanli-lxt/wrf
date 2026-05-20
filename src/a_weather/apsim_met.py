from __future__ import annotations

import re
from dataclasses import dataclass
import calendar
from datetime import date, datetime, timedelta
from pathlib import Path


@dataclass(frozen=True)
class DailyWeather:
    date: date
    radn: float
    maxt: float
    mint: float
    rain: float


@dataclass(frozen=True)
class ApsimMet:
    latitude: float
    longitude: float
    tav: float
    amp: float
    records: list[DailyWeather]


def parse_met_file(path: str | Path) -> ApsimMet:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    latitude = _header_float(lines, "latitude")
    longitude = _header_float(lines, "longitude")
    tav = _header_float(lines, "tav")
    amp = _header_float(lines, "amp")

    field_index = next(
        (idx for idx, line in enumerate(lines) if line.split() == ["year", "day", "radn", "maxt", "mint", "rain"]),
        None,
    )
    if field_index is None:
        raise ValueError("missing APSIM field header")
    if field_index + 1 >= len(lines) or lines[field_index + 1].split() != ["()", "()", "(MJ/m2)", "(oC)", "(oC)", "(mm)"]:
        raise ValueError("missing APSIM units row")

    records: list[DailyWeather] = []
    for line in lines[field_index + 2 :]:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 6:
            raise ValueError(f"malformed APSIM data row: {line}")
        year, doy = int(parts[0]), int(parts[1])
        record_date = _date_from_year_day(year, doy)
        records.append(
            DailyWeather(
                date=record_date,
                radn=float(parts[2]),
                maxt=float(parts[3]),
                mint=float(parts[4]),
                rain=max(0.0, float(parts[5])),
            )
        )

    return ApsimMet(latitude=latitude, longitude=longitude, tav=tav, amp=amp, records=records)


def write_met_file(met: ApsimMet, path: str | Path) -> None:
    lines = [
        "[weather.met.weather]",
        f"latitude = {met.latitude:.2f} (dec deg)",
        f"longitude = {met.longitude:.2f} (dec deg)",
        f"tav = {met.tav:.2f} (oC) ! annual average ambient temperature",
        f"amp = {met.amp:.2f} (oC) ! annual amplitude in mean monthly temperature",
        "year   day   radn   maxt   mint   rain",
        " ()    ()   (MJ/m2) (oC)   (oC)   (mm)",
    ]
    for record in met.records:
        doy = record.date.timetuple().tm_yday
        lines.append(
            f"{record.date.year:<6d} {doy:<5d} "
            f"{record.radn:<7.2f} {record.maxt:<6.2f} {record.mint:<6.2f} {record.rain:<6.2f}"
        )
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _header_float(lines: list[str], key: str) -> float:
    pattern = re.compile(rf"^{re.escape(key)}\s*=\s*([-+]?\d+(?:\.\d+)?)")
    for line in lines:
        match = pattern.search(line)
        if match:
            return float(match.group(1))
    raise ValueError(f"missing APSIM header value: {key}")


def _date_from_year_day(year: int, doy: int) -> date:
    max_doy = 366 if calendar.isleap(year) else 365
    if doy < 1 or doy > max_doy:
        raise ValueError(f"invalid day-of-year {doy} for {year}")
    return date(year, 1, 1) + timedelta(days=doy - 1)
