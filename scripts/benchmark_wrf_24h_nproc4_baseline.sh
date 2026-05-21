#!/usr/bin/env bash
set -euo pipefail

REPEAT_COUNT=${REPEAT_COUNT:-3}
NPROC_VALUE=${NPROC_VALUE:-4}
OUTPUT_PATH=${OUTPUT_PATH:-data/generated/benchmarks/wrf_validation_24h_nproc4_baseline.csv}
RUN_LABEL=validation_20241001_00
COMMAND_TEXT="docker compose -f docker/docker-compose.yml run --rm wrf bash /work/scripts/run_wrf_validation.sh"
COMMAND=(docker compose -f docker/docker-compose.yml run --rm wrf bash /work/scripts/run_wrf_validation.sh)

if (( REPEAT_COUNT < 0 )); then
  echo "REPEAT_COUNT must be non-negative." >&2
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT_PATH")"
git_commit=$(git rev-parse --short HEAD 2>/dev/null || true)
failed_count=0

printf 'run_label,run_index,nproc,seconds,exit_code,git_commit,log,command\n' > "$OUTPUT_PATH"

for ((run_index = 1; run_index <= REPEAT_COUNT; run_index++)); do
  echo "Running $RUN_LABEL baseline repeat $run_index/$REPEAT_COUNT with NPROC=$NPROC_VALUE"
  log_path="data/generated/benchmarks/wrf_validation_24h_nproc${NPROC_VALUE}_repeat_${run_index}.log"
  start_seconds=$(date +%s.%N)

  set +e
  NPROC="$NPROC_VALUE" "${COMMAND[@]}" > "$log_path" 2>&1
  exit_code=$?
  set -e

  end_seconds=$(date +%s.%N)
  seconds=$(awk -v start="$start_seconds" -v end="$end_seconds" 'BEGIN { printf "%.2f", end - start }')

  printf '%s,%s,%s,%s,%s,%s,%s,"%s"\n' \
    "$RUN_LABEL" \
    "$run_index" \
    "$NPROC_VALUE" \
    "$seconds" \
    "$exit_code" \
    "$git_commit" \
    "$log_path" \
    "$COMMAND_TEXT" >> "$OUTPUT_PATH"

  if (( exit_code != 0 )); then
    echo "Repeat $run_index failed. See $log_path" >&2
    failed_count=$((failed_count + 1))
  fi
done

echo "24h 4-core baseline benchmark written to $OUTPUT_PATH"

if (( failed_count > 0 )); then
  echo "$failed_count baseline benchmark repeat(s) failed." >&2
  exit 1
fi
