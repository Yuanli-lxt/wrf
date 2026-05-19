from pathlib import Path


def test_docker_compose_declares_wrf_service_and_mounts_project_dirs():
    text = Path("docker/docker-compose.yml").read_text(encoding="utf-8")

    assert "wrf:" in text
    assert "ncar/iwrf:lulc-2024-10-04" in text
    assert "../data:/work/data" in text
    assert "../wrf:/work/wrf" in text


def test_namelists_define_single_9km_domain_centered_on_site():
    wps = Path("wrf/namelists/namelist.wps.template").read_text(encoding="utf-8")
    wrf = Path("wrf/namelists/namelist.input.template").read_text(encoding="utf-8")

    assert "ref_lat" in wps
    assert "37.94" in wps
    assert "ref_lon" in wps
    assert "118.53" in wps
    assert "dx = 9000" in wps
    assert "dy = 9000" in wps
    assert "time_step                           = 54" in wrf
    assert "history_interval                    = 60" in wrf
