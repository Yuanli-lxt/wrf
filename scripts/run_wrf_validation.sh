#!/usr/bin/env bash
set -euo pipefail

WRF_RUN_DIR=/home/wrfuser/WRF/run
WPS_OUT=/work/data/wps/validation_20241001_00
OUT_DIR=/work/data/wrfout/validation_20241001_00
NAMELIST=/work/wrf/namelists/namelist.input.template
export LD_LIBRARY_PATH="/opt/netcdf/lib:/opt/hdf5/lib:/opt/intel/oneapi/compiler/2023.1.0/linux/compiler/lib/intel64_lin:/opt/jasper/lib:/opt/libpng/lib:${LD_LIBRARY_PATH:-}"
export I_MPI_FABRICS=shm
ulimit -s unlimited

mkdir -p "$OUT_DIR"

if [[ "$(find "$WPS_OUT" -maxdepth 1 -name 'met_em.d01.*.nc' | wc -l)" -ne 25 ]]; then
  echo "Expected 25 met_em files in $WPS_OUT. Run /work/scripts/run_wps_validation.sh first." >&2
  exit 1
fi

cd "$WRF_RUN_DIR"
rm -f met_em.d01.*.nc wrfinput_d01 wrfbdy_d01 wrfout_d01_* rsl.out.* rsl.error.* namelist.input

cp "$NAMELIST" namelist.input
ln -sf "$WPS_OUT"/met_em.d01.*.nc .

./real.exe
test -f wrfinput_d01
test -f wrfbdy_d01

./wrf.exe
test -f wrfout_d01_2024-10-01_00:00:00

cp namelist.input rsl.out.* rsl.error.* "$OUT_DIR"/
cp wrfinput_d01 wrfbdy_d01 "$OUT_DIR"/
cp wrfout_d01_* "$OUT_DIR"/

echo "WRF validation complete: $OUT_DIR"
