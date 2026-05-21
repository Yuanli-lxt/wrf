from pathlib import Path


def test_export_validation_met_script_uses_wrfout_and_writes_apsim_met():
    text = Path("scripts/export_validation_met.py").read_text(encoding="utf-8")

    assert "data/wrfout/validation_20241001_00" in text
    assert "data/generated/wrfout_validation_ascii" in text
    assert "data/generated/apsim/validation_wrf_20241001.met" in text
    assert "wrfout_d01_*" in text
    assert "safe_files" in text
    assert "aggregate_wrf_dataset" in text
    assert "write_met_file" in text


def test_export_validation_72h_met_script_uses_separate_wrfout_and_output_paths():
    text = Path("scripts/export_validation_72h_met.py").read_text(encoding="utf-8")

    assert "data/wrfout/validation_20241001_00_72h" in text
    assert "data/generated/wrfout_validation_72h_ascii" in text
    assert "data/generated/apsim/validation_wrf_20241001_72h.met" in text
    assert "wrfout_d01_*" in text
    assert "safe_files" in text
    assert "aggregate_wrf_dataset" in text
    assert "write_met_file" in text


def test_export_domain_size_met_script_uses_size_and_window_specific_paths():
    text = Path("scripts/export_domain_size_met.py").read_text(encoding="utf-8")

    assert "DOMAIN_SIZE" in text
    assert "WINDOW_HOURS" in text
    assert "data/wrfout/domain_{domain_size}_{window_hours}h_validation_20241001_00" in text
    assert "data/generated/wrfout_domain_{domain_size}_{window_hours}h_ascii" in text
    assert "data/generated/apsim/domain_{domain_size}_{window_hours}h_validation_wrf_20241001.met" in text
    assert "wrfout_d01_*" in text
    assert "aggregate_wrf_dataset" in text
    assert "write_met_file" in text


def test_summarize_domain_size_sweep_compares_against_80x80_reference():
    text = Path("scripts/summarize_domain_size_sweep.py").read_text(encoding="utf-8")

    assert "REFERENCE_DOMAIN_SIZE = 80" in text
    assert "domain_size_sweep.csv" in text
    assert "domain_size_sweep_summary.csv" in text
    assert "mean_abs_radn" in text
    assert "max_abs_radn" in text
    assert "mean_abs_maxt" in text
    assert "max_abs_maxt" in text
    assert "mean_abs_mint" in text
    assert "max_abs_mint" in text
    assert "mean_abs_rain" in text
    assert "max_abs_rain" in text
    assert "parse_met_file" in text


def test_export_domain_50_168h_met_script_writes_seven_day_output():
    text = Path("scripts/export_domain_50_168h_met.py").read_text(encoding="utf-8")

    assert "data/wrfout/domain_50_168h_validation_20241001_00" in text
    assert "data/generated/wrfout_domain_50_168h_ascii" in text
    assert "data/generated/apsim/domain_50_168h_validation_wrf_20241001.met" in text
    assert "wrfout_d01_*" in text
    assert "aggregate_wrf_dataset" in text
    assert "write_met_file" in text
    assert "expected_records = 7" in text
    assert "2024-10-01" in text
    assert "2024-10-07" in text
