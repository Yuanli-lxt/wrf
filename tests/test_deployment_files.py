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


def test_72h_namelist_extends_validation_window_without_replacing_24h_baseline():
    wrf = Path("wrf/namelists/namelist.input.72h.template").read_text(encoding="utf-8")
    baseline = Path("wrf/namelists/namelist.input.template").read_text(encoding="utf-8")

    assert "run_days                            = 3" in wrf
    assert "run_hours                           = 0" in wrf
    assert "start_year                          = 2024" in wrf
    assert "start_month                         = 10" in wrf
    assert "start_day                           = 01" in wrf
    assert "start_hour                          = 00" in wrf
    assert "end_year                            = 2024" in wrf
    assert "end_month                           = 10" in wrf
    assert "end_day                             = 04" in wrf
    assert "end_hour                            = 00" in wrf
    assert "history_interval                    = 60" in wrf
    assert "frames_per_outfile                  = 24" in wrf
    assert "time_step                           = 54" in wrf
    assert "e_vert                              = 45" in wrf
    assert "mp_physics                          = 3" in wrf
    assert "run_hours                           = 24" in baseline
    assert "end_day                             = 02" in baseline


def test_168h_namelist_defines_50x50_seven_day_validation_window():
    wrf = Path("wrf/namelists/namelist.input.168h.template").read_text(encoding="utf-8")

    assert "run_days                            = 7" in wrf
    assert "run_hours                           = 0" in wrf
    assert "start_year                          = 2024" in wrf
    assert "start_month                         = 10" in wrf
    assert "start_day                           = 01" in wrf
    assert "start_hour                          = 00" in wrf
    assert "end_year                            = 2024" in wrf
    assert "end_month                           = 10" in wrf
    assert "end_day                             = 08" in wrf
    assert "end_hour                            = 00" in wrf
    assert "interval_seconds                    = 10800" in wrf
    assert "history_interval                    = 60" in wrf
    assert "frames_per_outfile                  = 24" in wrf
    assert "e_we                                = 50" in wrf
    assert "e_sn                                = 50" in wrf
    assert "time_step                           = 54" in wrf
    assert "mp_physics                          = 3" in wrf


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


def test_wrf_validation_72h_script_keeps_outputs_separate_from_24h_baseline():
    text = Path("scripts/run_wrf_validation_72h.sh").read_text(encoding="utf-8")

    assert "/home/wrfuser/WRF/run" in text
    assert "/work/data/wps/validation_20241001_00" in text
    assert "/work/data/wrfout/validation_20241001_00_72h" in text
    assert "/work/wrf/namelists/namelist.input.72h.template" in text
    assert 'rm -f "$OUT_DIR"/wrfout_d01_*' in text
    assert "LD_LIBRARY_PATH" in text
    assert "I_MPI_FABRICS=shm" in text
    assert "/opt/intel/oneapi/mpi/2021.9.0/bin" in text
    assert "NPROC=" in text
    assert "mpirun -np" in text
    assert "met_em.d01.*_??-??-??.nc" in text
    assert '"$(find "$WPS_OUT" -maxdepth 1 -name' in text
    assert "-ne 25" in text
    assert "./real.exe" in text
    assert "./wrf.exe" in text
    assert "wrfinput_d01" in text
    assert "wrfbdy_d01" in text
    assert "safe_name=${native_name//:/-}" in text
    assert "wrfout_d01_2024-10-04_00-00-00" in text
    assert "WRF 72h validation complete" in text


def test_wps_domain_size_script_generates_matching_wps_grid_outputs():
    text = Path("scripts/run_wps_domain_size.sh").read_text(encoding="utf-8")

    assert "DOMAIN_SIZE=${DOMAIN_SIZE:-80}" in text
    assert "domain_${DOMAIN_SIZE}_validation_20241001_00" in text
    assert "namelist.wps.template" in text
    assert "e_we" in text
    assert "e_sn" in text
    assert "gfs.20241001.00.1p00" in text
    assert "Expected 25 GFS files" in text
    assert "./geogrid.exe" in text
    assert "./ungrib.exe" in text
    assert "./metgrid.exe" in text
    assert "safe_name=${native_name//:/-}" in text
    assert "met_em.d01.2024-10-04_00-00-00.nc" in text


def test_wps_domain_50_168h_script_generates_seven_day_metgrid_outputs():
    text = Path("scripts/run_wps_domain_50_168h.sh").read_text(encoding="utf-8")

    assert "DOMAIN_SIZE=50" in text
    assert "domain_50_168h_validation_20241001_00" in text
    assert "namelist.wps.template" in text
    assert "2024-10-08_00:00:00" in text
    assert "e_we" in text
    assert "e_sn" in text
    assert "gfs.20241001.00.1p00" in text
    assert "Expected 57 GFS files" in text
    assert "./geogrid.exe" in text
    assert "./ungrib.exe" in text
    assert "./metgrid.exe" in text
    assert "safe_name=${native_name//:/-}" in text
    assert "met_em.d01.2024-10-08_00-00-00.nc" in text


def test_wrf_domain_size_script_uses_matching_wps_grid_and_window_outputs():
    text = Path("scripts/run_wrf_domain_size.sh").read_text(encoding="utf-8")

    assert "DOMAIN_SIZE=${DOMAIN_SIZE:-80}" in text
    assert "WINDOW_HOURS=${WINDOW_HOURS:-24}" in text
    assert "domain_${DOMAIN_SIZE}_validation_20241001_00" in text
    assert "domain_${DOMAIN_SIZE}_${WINDOW_HOURS}h_validation_20241001_00" in text
    assert "namelist.input.template" in text
    assert "namelist.input.72h.template" in text
    assert "e_we" in text
    assert "e_sn" in text
    assert "-ne 25" in text
    assert "mpirun -np" in text
    assert "wrfout_d01_2024-10-02_00-00-00" in text
    assert "wrfout_d01_2024-10-04_00-00-00" in text
    assert "WRF domain-size validation complete" in text


def test_wrf_domain_50_168h_script_runs_from_seven_day_wps_outputs():
    text = Path("scripts/run_wrf_domain_50_168h.sh").read_text(encoding="utf-8")

    assert "/home/wrfuser/WRF/run" in text
    assert "/work/data/wps/domain_50_168h_validation_20241001_00" in text
    assert "/work/data/wrfout/domain_50_168h_validation_20241001_00" in text
    assert "/work/wrf/namelists/namelist.input.168h.template" in text
    assert "-ne 57" in text
    assert "NPROC=" in text
    assert "mpirun -np" in text
    assert "./real.exe" in text
    assert "./wrf.exe" in text
    assert "safe_name=${native_name//:/-}" in text
    assert "wrfout_d01_2024-10-08_00-00-00" in text
    assert "WRF 50x50 168h validation complete" in text


def test_domain_size_sweep_benchmark_records_runtime_comparison_inputs():
    text = Path("scripts/benchmark_domain_size_sweep.sh").read_text(encoding="utf-8")

    assert 'DOMAIN_SIZES=${DOMAIN_SIZES:-"80 60 50"}' in text
    assert 'WINDOW_HOURS_LIST=${WINDOW_HOURS_LIST:-"24 72"}' in text
    assert "domain_size_sweep.csv" in text
    assert "run_wps_domain_size.sh" in text
    assert "run_wrf_domain_size.sh" in text
    assert "export_domain_size_met.py" in text
    assert "summarize_domain_size_sweep.py" in text
    assert "-e DOMAIN_SIZE=" in text
    assert "-e WINDOW_HOURS=" in text
    assert "-e NPROC=" in text
    assert "domain_size,window_hours,wps_seconds,wrf_seconds,export_seconds,exit_code" in text
    assert "NPROC_VALUE=${NPROC_VALUE:-4}" in text


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


def test_24h_4core_baseline_benchmark_records_repeatable_metadata():
    text = Path("scripts/benchmark_wrf_24h_nproc4_baseline.ps1").read_text(encoding="utf-8")

    assert "$RepeatCount = 3" in text
    assert "$Nproc = 4" in text
    assert "data/generated/benchmarks/wrf_validation_24h_nproc4_baseline.csv" in text
    assert "validation_20241001_00" in text
    assert "docker compose -f docker/docker-compose.yml run --rm wrf bash /work/scripts/run_wrf_validation.sh" in text
    assert "$env:NPROC = [string]$Nproc" in text
    assert "Measure-Command" in text
    assert "Export-Csv" in text
    assert "run_label" in text
    assert "run_index" in text
    assert "nproc" in text
    assert "seconds" in text
    assert "exit_code" in text
    assert "git_commit" in text
    assert "log" in text
    assert "command" in text
    assert "throw" in text


def test_ubuntu_24h_4core_baseline_benchmark_records_repeatable_metadata():
    text = Path("scripts/benchmark_wrf_24h_nproc4_baseline.sh").read_text(encoding="utf-8")

    assert "REPEAT_COUNT=${REPEAT_COUNT:-3}" in text
    assert "NPROC_VALUE=${NPROC_VALUE:-4}" in text
    assert "data/generated/benchmarks/wrf_validation_24h_nproc4_baseline.csv" in text
    assert "RUN_LABEL=validation_20241001_00" in text
    assert "docker compose -f docker/docker-compose.yml run --rm wrf bash /work/scripts/run_wrf_validation.sh" in text
    assert "NPROC=\"$NPROC_VALUE\"" in text
    assert "date +%s" in text
    assert "run_label,run_index,nproc,seconds,exit_code,git_commit,log,command" in text
    assert "wrf_validation_24h_nproc${NPROC_VALUE}_repeat_${run_index}.log" in text
    assert "failed_count" in text
    assert "exit 1" in text
