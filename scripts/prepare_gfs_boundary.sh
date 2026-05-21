#!/usr/bin/env bash
set -euo pipefail

DATE=${DATE:-20241001}
CYCLE=${CYCLE:-00}
RESOLUTION=${RESOLUTION:-1p00}
TARGET_ROOT=${TARGET_ROOT:-data/raw_boundary}
MAX_FORECAST_HOUR=${MAX_FORECAST_HOUR:-72}

if [[ ! "$MAX_FORECAST_HOUR" =~ ^[0-9]+$ ]]; then
  echo "MAX_FORECAST_HOUR must be numeric." >&2
  exit 1
fi

target_dir="$TARGET_ROOT/gfs.$DATE.$CYCLE.$RESOLUTION"
mkdir -p "$target_dir"

for hour in $(seq 0 3 "$MAX_FORECAST_HOUR"); do
  forecast=$(printf "%03d" "$hour")
  file_name="gfs.t${CYCLE}z.pgrb2.${RESOLUTION}.f$forecast"
  url="https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.$DATE/$CYCLE/atmos/$file_name"
  target="$target_dir/$file_name"

  echo "Checking $file_name"
  headers=$(curl -fsSLI --retry 5 --retry-all-errors --connect-timeout 20 --max-time 120 "$url")
  length=$(printf "%s\n" "$headers" | awk 'tolower($1)=="content-length:" { value=$2 } END { gsub("\r", "", value); print value }')
  if [[ -z "$length" ]]; then
    echo "Could not determine Content-Length for $url" >&2
    exit 1
  fi

  if [[ -f "$target" ]]; then
    local_size=$(stat -c%s "$target")
    if [[ "$local_size" == "$length" ]]; then
      echo "Already downloaded: $file_name ($length bytes)"
      continue
    fi
    echo "Removing incomplete file: $target"
    rm -f "$target"
  fi

  echo "Downloading $file_name ($length bytes)"
  curl -fL --retry 5 --retry-all-errors --connect-timeout 20 --max-time 600 "$url" -o "$target"
  local_size=$(stat -c%s "$target")
  if [[ "$local_size" != "$length" ]]; then
    echo "Downloaded size mismatch for $file_name: expected $length, got $local_size" >&2
    exit 1
  fi
done

echo "GFS boundary preparation complete: $target_dir"
