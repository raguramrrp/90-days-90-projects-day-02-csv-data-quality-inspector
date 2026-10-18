"""
End-to-End Integration tests running on full sample datasets.
"""

import os
import pytest
from src.parser import parse_csv
from src.validator import validate_dataset
from src.profiler import profile_dataset
from src.quality_engine import calculate_quality_score
from src.report_generator import generate_html_report, generate_json_report, generate_markdown_report


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def test_e2e_clean_baseline():
    file_path = os.path.join(DATA_DIR, "sample_clean_baseline.csv")
    assert os.path.exists(file_path), "sample_clean_baseline.csv must exist"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    df, meta = parse_csv(file_bytes, filename="sample_clean_baseline.csv")
    assert len(df) == 400
    assert len(df.columns) == 9

    val = validate_dataset(df, meta)
    assert val["is_valid"]
    assert val["can_profile"]

    prof = profile_dataset(df, meta)
    assert prof["overview"]["duplicate_rows_count"] == 0
    assert prof["overview"]["overall_missing_percentage"] == 0.0

    quality = calculate_quality_score(prof, val)
    assert quality["overall_score"] >= 90.0
    assert quality["grade"] == "A"

    # Reports generation check
    html = generate_html_report(prof, val, quality)
    json_rep = generate_json_report(prof, val, quality)
    md = generate_markdown_report(prof, val, quality)
    assert len(html) > 500
    assert len(json_rep) > 500
    assert len(md) > 200


def test_e2e_dirty_ecommerce():
    file_path = os.path.join(DATA_DIR, "sample_ecommerce_dirty.csv")
    assert os.path.exists(file_path), "sample_ecommerce_dirty.csv must exist"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    df, meta = parse_csv(file_bytes, filename="sample_ecommerce_dirty.csv")
    assert len(df) > 500

    val = validate_dataset(df, meta)
    prof = profile_dataset(df, meta)
    quality = calculate_quality_score(prof, val)

    # Must reflect defects
    assert prof["overview"]["duplicate_rows_count"] > 0
    assert prof["overview"]["overall_missing_percentage"] > 0.0
    assert prof["overview"]["total_outliers_detected"] > 0
    assert quality["overall_score"] < 80.0
    assert len(quality["recommendations"]) >= 3


def test_e2e_employee_records():
    file_path = os.path.join(DATA_DIR, "sample_employee_records.csv")
    assert os.path.exists(file_path), "sample_employee_records.csv must exist"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    df, meta = parse_csv(file_bytes, filename="sample_employee_records.csv")
    assert len(df) >= 350

    val = validate_dataset(df, meta)
    prof = profile_dataset(df, meta)
    quality = calculate_quality_score(prof, val)

    # Constant column check and grade check
    assert prof["columns"]["company_name"]["is_constant"]
    assert quality["overall_score"] < 90.0
    assert quality["grade"] in ["B", "C"]
