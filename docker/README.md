# Local WRF Runtime

Start Docker Desktop before using this runtime.

Validate the Compose file:

```powershell
docker compose -f docker/docker-compose.yml config
```

Open a shell in the WRF container:

```powershell
docker compose -f docker/docker-compose.yml run --rm wrf bash
```

The configured image is `ncar/iwrf:lulc-2024-10-04`. A lightweight availability check is:

```powershell
docker manifest inspect ncar/iwrf:lulc-2024-10-04
```

The first validation target is 2024-10-01 00:00 to 2024-10-04 00:00 for the site at 37.94N, 118.53E.

Place WRF geographic data under `data/geog/` and boundary data under `data/raw_boundary/` before running WPS.

Prepare the first validation inputs from Windows PowerShell:

```powershell
.\scripts\prepare_geog.ps1
.\scripts\prepare_gfs_boundary.ps1
```

The geog script downloads the official WPS low-resolution mandatory package and extracts it under `data/geog/WPS_GEOG_LOW_RES`. The GFS script downloads 2024-10-01 00Z forecast hours 000-072 every 3 hours at 1.0 degree resolution under `data/raw_boundary/gfs.20241001.00.1p00`.

Run the WPS validation stage from Windows PowerShell:

```powershell
docker compose -f docker/docker-compose.yml run --rm wrf bash /work/scripts/run_wps_validation.sh
```

WPS outputs are copied to `data/wps/validation_20241001_00`.

Run the WRF validation stage:

```powershell
docker compose -f docker/docker-compose.yml run --rm wrf bash /work/scripts/run_wrf_validation.sh
```

WRF outputs are copied to `data/wrfout/validation_20241001_00`.
