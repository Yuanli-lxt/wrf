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

The first validation target is 2024-10-01 00:00 to 2024-10-04 00:00 for the site at 37.94N, 118.53E.

Place WRF geographic data under `data/geog/` and boundary data under `data/raw_boundary/` before running WPS.
