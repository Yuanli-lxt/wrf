from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Site:
    name: str
    latitude: float
    longitude: float
    timezone: str


@dataclass(frozen=True)
class TimeWindow:
    start: datetime
    end: datetime


@dataclass(frozen=True)
class Domain:
    center_latitude: float
    center_longitude: float
    dx_m: int
    dy_m: int
    e_we: int
    e_sn: int
    time_step_seconds: int
    output_interval_minutes: int


@dataclass(frozen=True)
class ApsimExport:
    tav: float
    amp: float
    fields: list[str]


@dataclass(frozen=True)
class SiteConfig:
    site: Site
    validation_window: TimeWindow
    full_window: TimeWindow
    domain: Domain
    apsim: ApsimExport


def load_site_config(path: str | Path) -> SiteConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("configuration must be a mapping")

    required_sections = ["site", "validation_window", "full_window", "domain", "apsim"]
    missing = [section for section in required_sections if section not in raw]
    if missing:
        raise ValueError(f"missing required section: {', '.join(missing)}")

    return SiteConfig(
        site=_site(raw["site"]),
        validation_window=_window(raw["validation_window"]),
        full_window=_window(raw["full_window"]),
        domain=_domain(raw["domain"]),
        apsim=_apsim(raw["apsim"]),
    )


def _window(raw: dict[str, Any]) -> TimeWindow:
    start = datetime.fromisoformat(raw["start"])
    end = datetime.fromisoformat(raw["end"])
    if end <= start:
        raise ValueError("time window end must be after start")
    return TimeWindow(start=start, end=end)


def _site(raw: dict[str, Any]) -> Site:
    return Site(
        name=str(raw["name"]),
        latitude=float(raw["latitude"]),
        longitude=float(raw["longitude"]),
        timezone=str(raw["timezone"]),
    )


def _domain(raw: dict[str, Any]) -> Domain:
    return Domain(
        center_latitude=float(raw["center_latitude"]),
        center_longitude=float(raw["center_longitude"]),
        dx_m=int(raw["dx_m"]),
        dy_m=int(raw["dy_m"]),
        e_we=int(raw["e_we"]),
        e_sn=int(raw["e_sn"]),
        time_step_seconds=int(raw["time_step_seconds"]),
        output_interval_minutes=int(raw["output_interval_minutes"]),
    )


def _apsim(raw: dict[str, Any]) -> ApsimExport:
    fields = [str(field) for field in raw["fields"]]
    expected = ["year", "day", "radn", "maxt", "mint", "rain"]
    if fields != expected:
        raise ValueError(f"unsupported APSIM fields: {fields}")
    return ApsimExport(tav=float(raw["tav"]), amp=float(raw["amp"]), fields=fields)
