#!/usr/bin/env bash
set -euo pipefail

DOMAIN_SIZE=50
WPS_DIR=/home/wrfuser/WPS
RUN_DIR=/work/data/wps/domain_50_168h_validation_20241001_00
GFS_DIR=/work/data/raw_boundary/gfs.20241001.00.1p00
NAMELIST_TEMPLATE=/work/wrf/namelists/namelist.wps.template
export LD_LIBRARY_PATH="/opt/netcdf/lib:/opt/hdf5/lib:/opt/intel/oneapi/compiler/2023.1.0/linux/compiler/lib/intel64_lin:/opt/jasper/lib:/opt/libpng/lib:${LD_LIBRARY_PATH:-}"
export I_MPI_FABRICS=shm
ulimit -s unlimited

mkdir -p "$RUN_DIR"
rm -f "$RUN_DIR"/met_em.d01.*.nc "$RUN_DIR"/geo_em.d01.nc

if [[ ! -d /work/data/geog/WPS_GEOG_LOW_RES ]]; then
  echo "Missing /work/data/geog/WPS_GEOG_LOW_RES. Run scripts/prepare_geog.ps1 first." >&2
  exit 1
fi

if [[ "$(find "$GFS_DIR" -maxdepth 1 -type f -name 'gfs.t00z.pgrb2.1p00.f*' | wc -l)" -ne 57 ]]; then
  echo "Expected 57 GFS files in $GFS_DIR. Run scripts/prepare_gfs_boundary.sh with MAX_FORECAST_HOUR=168 first." >&2
  exit 1
fi

cd "$WPS_DIR"
rm -f GRIBFILE.* FILE:* geo_em.d01.nc met_em.d01.*.nc geogrid.log ungrib.log metgrid.log Vtable namelist.wps

awk -v size="$DOMAIN_SIZE" '
  /^[[:space:]]*e_we[[:space:]]*=/ { sub(/=.*/, "= " size ","); print; next }
  /^[[:space:]]*e_sn[[:space:]]*=/ { sub(/=.*/, "= " size ","); print; next }
  /^[[:space:]]*end_date[[:space:]]*=/ { sub(/=.*/, "= '\''2024-10-08_00:00:00'\'',"); print; next }
  { print }
' "$NAMELIST_TEMPLATE" > namelist.wps

ln -sf ungrib/Variable_Tables/Vtable.GFS Vtable
./link_grib.csh "$GFS_DIR"/gfs.t00z.pgrb2.1p00.f*

./geogrid.exe
./ungrib.exe
./metgrid.exe

cp namelist.wps geogrid.log ungrib.log metgrid.log "$RUN_DIR"/
cp geo_em.d01.nc "$RUN_DIR"/
for native_path in met_em.d01.*.nc; do
  native_name=$(basename "$native_path")
  safe_name=${native_name//:/-}
  cp "$native_path" "$RUN_DIR/$safe_name"
done

test -f "$RUN_DIR/geo_em.d01.nc"
test -f "$RUN_DIR/met_em.d01.2024-10-08_00-00-00.nc"

echo "WPS 50x50 168h validation complete: $RUN_DIR"
