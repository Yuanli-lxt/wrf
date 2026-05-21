#!/usr/bin/env bash
set -euo pipefail

DOMAIN_SIZE=${DOMAIN_SIZE:-80}
WINDOW_HOURS=${WINDOW_HOURS:-24}
WRF_RUN_DIR=/home/wrfuser/WRF/run
WPS_OUT=/work/data/wps/domain_${DOMAIN_SIZE}_validation_20241001_00
OUT_DIR=/work/data/wrfout/domain_${DOMAIN_SIZE}_${WINDOW_HOURS}h_validation_20241001_00
NPROC=${NPROC:-1}
export LD_LIBRARY_PATH="/opt/netcdf/lib:/opt/hdf5/lib:/opt/intel/oneapi/compiler/2023.1.0/linux/compiler/lib/intel64_lin:/opt/jasper/lib:/opt/libpng/lib:${LD_LIBRARY_PATH:-}"
export PATH="/opt/intel/oneapi/mpi/2021.9.0/bin:${PATH}"
export I_MPI_FABRICS=shm
ulimit -s unlimited

if [[ ! "$DOMAIN_SIZE" =~ ^[0-9]+$ ]]; then
  echo "DOMAIN_SIZE must be numeric." >&2
  exit 1
fi

case "$WINDOW_HOURS" in
  24)
    NAMELIST_TEMPLATE=/work/wrf/namelists/namelist.input.template
    FINAL_NATIVE=wrfout_d01_2024-10-02_00:00:00
    FINAL_SAFE=wrfout_d01_2024-10-02_00-00-00
    ;;
  72)
    NAMELIST_TEMPLATE=/work/wrf/namelists/namelist.input.72h.template
    FINAL_NATIVE=wrfout_d01_2024-10-04_00:00:00
    FINAL_SAFE=wrfout_d01_2024-10-04_00-00-00
    ;;
  *)
    echo "WINDOW_HOURS must be 24 or 72." >&2
    exit 1
    ;;
esac

mkdir -p "$OUT_DIR"
rm -f "$OUT_DIR"/wrfout_d01_*

if [[ "$(find "$WPS_OUT" -maxdepth 1 -name 'met_em.d01.*_??-??-??.nc' | wc -l)" -ne 25 ]]; then
  echo "Expected 25 met_em files in $WPS_OUT. Run run_wps_domain_size.sh for DOMAIN_SIZE=$DOMAIN_SIZE first." >&2
  exit 1
fi

cd "$WRF_RUN_DIR"
rm -f met_em.d01.*.nc wrfinput_d01 wrfbdy_d01 wrfout_d01_* rsl.out.* rsl.error.* namelist.input

awk -v size="$DOMAIN_SIZE" '
  /^[[:space:]]*e_we[[:space:]]*=/ { sub(/=.*/, "= " size ","); print; next }
  /^[[:space:]]*e_sn[[:space:]]*=/ { sub(/=.*/, "= " size ","); print; next }
  { print }
' "$NAMELIST_TEMPLATE" > namelist.input

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
test -f "$FINAL_NATIVE"

cp namelist.input rsl.out.* rsl.error.* "$OUT_DIR"/
cp wrfinput_d01 wrfbdy_d01 "$OUT_DIR"/
for native_path in wrfout_d01_*; do
  native_name=$(basename "$native_path")
  safe_name=${native_name//:/-}
  cp "$native_path" "$OUT_DIR/$safe_name"
done
test -f "$OUT_DIR/$FINAL_SAFE"

echo "WRF domain-size validation complete with DOMAIN_SIZE=$DOMAIN_SIZE WINDOW_HOURS=$WINDOW_HOURS NPROC=$NPROC: $OUT_DIR"
