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
