from pathlib import Path


def test_docker_compose_declares_wrf_service_and_mounts_project_dirs():
    text = Path("docker/docker-compose.yml").read_text(encoding="utf-8")

    assert "wrf:" in text
    assert "ncar/iwrf:lulc-2024-10-04" in text
    assert "NPROC: ${NPROC:-1}" in text
    assert "../data:/work/data" in text
    assert "../wrf:/work/wrf" in text


def test_namelists_define_single_9km_domain_centered_on_site():
    wps = Path("wrf/namelists/namelist.wps.template").read_text(encoding="utf-8")
    wrf = Path("wrf/namelists/namelist.input.template").read_text(encoding="utf-8")

    assert "ref_lat" in wps
    assert "37.94" in wps
    assert "ref_lon" in wps
    assert "118.53" in wps
    assert "geog_data_res     = 'lowres'" in wps
    assert "dx = 9000" in wps
    assert "dy = 9000" in wps
    assert "interval_seconds = 10800" in wps
    assert "interval_seconds                    = 10800" in wrf
    assert "run_hours                           = 24" in wrf
    assert "end_day                             = 02" in wrf
    assert "end_hour                            = 00" in wrf
    assert "e_vert                              = 45" in wrf
    assert "geog_data_path = '/work/data/geog/WPS_GEOG_LOW_RES'" in wps
    assert "time_step                           = 54" in wrf
    assert "history_interval                    = 60" in wrf
    assert "physics_suite" not in wrf
    assert "mp_physics                          = 3" in wrf
    assert "cu_physics                          = 1" in wrf


def test_gitignore_excludes_downloaded_weather_inputs():
    text = Path(".gitignore").read_text(encoding="utf-8")

    assert "data/downloads/" in text
    assert "data/raw_boundary/" in text
    assert "data/geog/" in text


def test_wps_validation_script_runs_expected_wps_stages():
    text = Path("scripts/run_wps_validation.sh").read_text(encoding="utf-8")

    assert "/home/wrfuser/WPS" in text
    assert "LD_LIBRARY_PATH" in text
    assert "I_MPI_FABRICS=shm" in text
    assert "ulimit -s unlimited" in text
    assert "/opt/netcdf/lib" in text
    assert "/opt/hdf5/lib" in text
    assert "/opt/intel/oneapi/compiler/2023.1.0/linux/compiler/lib/intel64_lin" in text
    assert "/opt/jasper/lib" in text
    assert "/opt/libpng/lib" in text
    assert "Vtable.GFS" in text
    assert "link_grib.csh" in text
    assert "./geogrid.exe" in text
    assert "./ungrib.exe" in text
    assert "./metgrid.exe" in text
    assert "/work/data/wps/validation_20241001_00" in text
    assert 'rm -f "$RUN_DIR"/met_em.d01.*.nc' in text
    assert "safe_name=${native_name//:/-}" in text
    assert "met_em.d01.2024-10-04_00-00-00.nc" in text


def test_wrf_validation_script_runs_real_and_wrf_from_metgrid_outputs():
    text = Path("scripts/run_wrf_validation.sh").read_text(encoding="utf-8")

    assert "/home/wrfuser/WRF/run" in text
    assert "/work/data/wps/validation_20241001_00" in text
    assert "/work/data/wrfout/validation_20241001_00" in text
    assert 'rm -f "$OUT_DIR"/wrfout_d01_*' in text
    assert "LD_LIBRARY_PATH" in text
    assert "I_MPI_FABRICS=shm" in text
    assert "/opt/intel/oneapi/mpi/2021.9.0/bin" in text
    assert "NPROC=" in text
    assert "mpirun -np" in text
    assert "met_em.d01.*_??-??-??.nc" in text
    assert "./real.exe" in text
    assert "./wrf.exe" in text
    assert "wrfinput_d01" in text
    assert "wrfbdy_d01" in text
    assert "safe_name=${native_name//:/-}" in text
    assert "wrfout_d01_2024-10-01_00-00-00" in text


def test_benchmark_wrf_script_runs_requested_core_counts_and_records_timing():
    text = Path("scripts/benchmark_wrf_validation.ps1").read_text(encoding="utf-8")

    assert "$CoreCounts = @(1, 2, 4)" in text
    assert "$env:NPROC = [string]$core" in text
    assert "Measure-Command" in text
    assert "$ErrorActionPreference = \"Continue\"" in text
    assert "$ErrorActionPreference = $previousPreference" in text
    assert "cmd /c" in text
    assert "docker compose -f docker/docker-compose.yml run --rm wrf bash /work/scripts/run_wrf_validation.sh" in text
    assert "data/generated/benchmarks/wrf_validation_benchmark.csv" in text
