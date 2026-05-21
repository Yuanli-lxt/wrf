#!/usr/bin/env bash
set -euo pipefail

DOMAIN_SIZES=${DOMAIN_SIZES:-"80 60 50"}
WINDOW_HOURS_LIST=${WINDOW_HOURS_LIST:-"24 72"}
NPROC_VALUE=${NPROC_VALUE:-4}
OUTPUT_PATH=${OUTPUT_PATH:-data/generated/benchmarks/domain_size_sweep.csv}

mkdir -p "$(dirname "$OUTPUT_PATH")" data/generated/benchmarks
printf 'domain_size,window_hours,wps_seconds,wrf_seconds,export_seconds,exit_code,wps_log,wrf_log,export_log,met_path\n' > "$OUTPUT_PATH"

time_command() {
  local log_path=$1
  shift
  local start_seconds end_seconds seconds exit_code
  start_seconds=$(date +%s.%N)
  set +e
  "$@" > "$log_path" 2>&1
  exit_code=$?
  set -e
  end_seconds=$(date +%s.%N)
  seconds=$(awk -v start="$start_seconds" -v end="$end_seconds" 'BEGIN { printf "%.2f", end - start }')
  printf '%s,%s\n' "$seconds" "$exit_code"
}

for domain_size in $DOMAIN_SIZES; do
  echo "Running WPS for DOMAIN_SIZE=$domain_size"
  wps_log="data/generated/benchmarks/domain_${domain_size}_wps.log"
  IFS=, read -r wps_seconds wps_exit < <(
    time_command "$wps_log" docker compose -f docker/docker-compose.yml run --rm -e DOMAIN_SIZE="$domain_size" wrf bash /work/scripts/run_wps_domain_size.sh
  )

  for window_hours in $WINDOW_HOURS_LIST; do
    wrf_log="data/generated/benchmarks/domain_${domain_size}_${window_hours}h_wrf.log"
    export_log="data/generated/benchmarks/domain_${domain_size}_${window_hours}h_export.log"
    met_path="data/generated/apsim/domain_${domain_size}_${window_hours}h_validation_wrf_20241001.met"
    wrf_seconds=0.00
    wrf_exit=1
    export_seconds=0.00
    export_exit=1

    if [[ "$wps_exit" -eq 0 ]]; then
      echo "Running WRF for DOMAIN_SIZE=$domain_size WINDOW_HOURS=$window_hours"
      IFS=, read -r wrf_seconds wrf_exit < <(
        time_command "$wrf_log" docker compose -f docker/docker-compose.yml run --rm -e DOMAIN_SIZE="$domain_size" -e WINDOW_HOURS="$window_hours" -e NPROC="$NPROC_VALUE" wrf bash /work/scripts/run_wrf_domain_size.sh
      )
    fi

    if [[ "$wps_exit" -eq 0 && "$wrf_exit" -eq 0 ]]; then
      echo "Exporting APSIM met for DOMAIN_SIZE=$domain_size WINDOW_HOURS=$window_hours"
      IFS=, read -r export_seconds export_exit < <(
        time_command "$export_log" env DOMAIN_SIZE="$domain_size" WINDOW_HOURS="$window_hours" uv run python scripts/export_domain_size_met.py
      )
    fi

    case_exit=0
    if [[ "$wps_exit" -ne 0 || "$wrf_exit" -ne 0 || "$export_exit" -ne 0 ]]; then
      case_exit=1
    fi

    printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
      "$domain_size" \
      "$window_hours" \
      "$wps_seconds" \
      "$wrf_seconds" \
      "$export_seconds" \
      "$case_exit" \
      "$wps_log" \
      "$wrf_log" \
      "$export_log" \
      "$met_path" >> "$OUTPUT_PATH"
  done
done

uv run python scripts/summarize_domain_size_sweep.py
echo "Domain-size sweep written to $OUTPUT_PATH"
