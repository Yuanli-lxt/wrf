from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from a_weather.apsim_met import ApsimMet, parse_met_file


REFERENCE_DOMAIN_SIZE = 80
RESULTS_PATH = Path("data/generated/benchmarks/domain_size_sweep.csv")
SUMMARY_PATH = Path("data/generated/benchmarks/domain_size_sweep_summary.csv")


def main() -> None:
    rows = _read_results(RESULTS_PATH)
    summary_rows: list[dict[str, str]] = []
    by_window: dict[int, dict[int, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        if row.get("exit_code") == "0":
            by_window[int(row["window_hours"])][int(row["domain_size"])] = row

    for window_hours, domain_rows in sorted(by_window.items()):
        reference_row = domain_rows.get(REFERENCE_DOMAIN_SIZE)
        if reference_row is None:
            continue
        reference = parse_met_file(reference_row["met_path"])
        for domain_size, row in sorted(domain_rows.items()):
            candidate = parse_met_file(row["met_path"])
            metrics = _difference_metrics(reference, candidate)
            summary_rows.append(
                {
                    "domain_size": str(domain_size),
                    "window_hours": str(window_hours),
                    "records": str(len(candidate.records)),
                    "wps_seconds": row["wps_seconds"],
                    "wrf_seconds": row["wrf_seconds"],
                    "export_seconds": row["export_seconds"],
                    **{key: f"{value:.4f}" for key, value in metrics.items()},
                    "met_path": row["met_path"],
                }
            )

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "domain_size",
        "window_hours",
        "records",
        "wps_seconds",
        "wrf_seconds",
        "export_seconds",
        "mean_abs_radn",
        "max_abs_radn",
        "mean_abs_maxt",
        "max_abs_maxt",
        "mean_abs_mint",
        "max_abs_mint",
        "mean_abs_rain",
        "max_abs_rain",
        "met_path",
    ]
    with SUMMARY_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"Wrote {len(summary_rows)} summary rows to {SUMMARY_PATH}")


def _read_results(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _difference_metrics(reference: ApsimMet, candidate: ApsimMet) -> dict[str, float]:
    reference_by_date = {record.date: record for record in reference.records}
    candidate_by_date = {record.date: record for record in candidate.records}
    dates = sorted(set(reference_by_date).intersection(candidate_by_date))
    if not dates:
        raise ValueError("No overlapping APSIM dates to compare")

    metrics: dict[str, float] = {}
    for field in ["radn", "maxt", "mint", "rain"]:
        diffs = [abs(getattr(candidate_by_date[day], field) - getattr(reference_by_date[day], field)) for day in dates]
        metrics[f"mean_abs_{field}"] = sum(diffs) / len(diffs)
        metrics[f"max_abs_{field}"] = max(diffs)
    return metrics


if __name__ == "__main__":
    main()
