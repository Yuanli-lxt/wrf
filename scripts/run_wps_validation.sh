#!/usr/bin/env bash
set -euo pipefail

WPS_DIR=/home/wrfuser/WPS
RUN_DIR=/work/data/wps/validation_20241001_00
GFS_DIR=/work/data/raw_boundary/gfs.20241001.00.1p00
NAMELIST=/work/wrf/namelists/namelist.wps.template
export LD_LIBRARY_PATH="/opt/netcdf/lib:/opt/hdf5/lib:/opt/intel/oneapi/compiler/2023.1.0/linux/compiler/lib/intel64_lin:/opt/jasper/lib:/opt/libpng/lib:${LD_LIBRARY_PATH:-}"
export I_MPI_FABRICS=shm
ulimit -s unlimited

mkdir -p "$RUN_DIR"

if [[ ! -d /work/data/geog/WPS_GEOG_LOW_RES ]]; then
  echo "Missing /work/data/geog/WPS_GEOG_LOW_RES. Run scripts/prepare_geog.ps1 on the Windows host first." >&2
  exit 1
fi

if [[ "$(find "$GFS_DIR" -maxdepth 1 -type f -name 'gfs.t00z.pgrb2.1p00.f*' | wc -l)" -ne 25 ]]; then
  echo "Expected 25 GFS files in $GFS_DIR. Run scripts/prepare_gfs_boundary.ps1 on the Windows host first." >&2
  exit 1
fi

cd "$WPS_DIR"
rm -f GRIBFILE.* FILE:* geo_em.d01.nc met_em.d01.*.nc geogrid.log ungrib.log metgrid.log Vtable namelist.wps

cp "$NAMELIST" namelist.wps
ln -sf ungrib/Variable_Tables/Vtable.GFS Vtable
./link_grib.csh "$GFS_DIR"/gfs.t00z.pgrb2.1p00.f*

./geogrid.exe
./ungrib.exe
./metgrid.exe

cp namelist.wps geogrid.log ungrib.log metgrid.log "$RUN_DIR"/
cp geo_em.d01.nc "$RUN_DIR"/
cp met_em.d01.*.nc "$RUN_DIR"/

test -f "$RUN_DIR/geo_em.d01.nc"
test -f "$RUN_DIR/met_em.d01.2024-10-04_00:00:00.nc"

echo "WPS validation complete: $RUN_DIR"
