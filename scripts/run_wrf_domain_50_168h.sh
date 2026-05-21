#!/usr/bin/env bash
set -euo pipefail

WRF_RUN_DIR=/home/wrfuser/WRF/run
WPS_OUT=/work/data/wps/domain_50_168h_validation_20241001_00
OUT_DIR=/work/data/wrfout/domain_50_168h_validation_20241001_00
NAMELIST=/work/wrf/namelists/namelist.input.168h.template
NPROC=${NPROC:-1}
export LD_LIBRARY_PATH="/opt/netcdf/lib:/opt/hdf5/lib:/opt/intel/oneapi/compiler/2023.1.0/linux/compiler/lib/intel64_lin:/opt/jasper/lib:/opt/libpng/lib:${LD_LIBRARY_PATH:-}"
export PATH="/opt/intel/oneapi/mpi/2021.9.0/bin:${PATH}"
export I_MPI_FABRICS=shm
ulimit -s unlimited

mkdir -p "$OUT_DIR"
rm -f "$OUT_DIR"/wrfout_d01_*

if [[ "$(find "$WPS_OUT" -maxdepth 1 -name 'met_em.d01.*_??-??-??.nc' | wc -l)" -ne 57 ]]; then
  echo "Expected 57 met_em files in $WPS_OUT. Run /work/scripts/run_wps_domain_50_168h.sh first." >&2
  exit 1
fi

cd "$WRF_RUN_DIR"
rm -f met_em.d01.*.nc wrfinput_d01 wrfbdy_d01 wrfout_d01_* rsl.out.* rsl.error.* namelist.input

cp "$NAMELIST" namelist.input
for safe_path in "$WPS_OUT"/met_em.d01.*_??-??-??.nc; do
  safe_name=$(basename "$safe_path")
  date_part=${safe_name%_*}
  time_part=${safe_name##*_}
  native_name="${date_part}_${time_part//-/:}"
  ln -sf "$safe_path" "$native_name"
done

if [[ "$NPROC" -gt 1 ]]; then
  mpirun -np "$NPROC" ./real.exe
else
  ./real.exe
fi
test -f wrfinput_d01
test -f wrfbdy_d01

if [[ "$NPROC" -gt 1 ]]; then
  mpirun -np "$NPROC" ./wrf.exe
else
  ./wrf.exe
fi
test -f wrfout_d01_2024-10-08_00:00:00

cp namelist.input rsl.out.* rsl.error.* "$OUT_DIR"/
cp wrfinput_d01 wrfbdy_d01 "$OUT_DIR"/
for native_path in wrfout_d01_*; do
  native_name=$(basename "$native_path")
  safe_name=${native_name//:/-}
  cp "$native_path" "$OUT_DIR/$safe_name"
done
test -f "$OUT_DIR/wrfout_d01_2024-10-08_00-00-00"

echo "WRF 50x50 168h validation complete with NPROC=$NPROC: $OUT_DIR"
