"""
Unit tests for the Report Generator Module.
"""

import json
import pandas as pd
import pytest
from src.parser import parse_csv
from src.validator import validate_dataset
from src.profiler import profile_dataset
from src.quality_engine import calculate_quality_score
from src.report_generator import (
    generate_json_report,
    generate_markdown_report,
    generate_html_report,
)


@pytest.fixture
def sample_assessment():
    content = "id,name,val\n1,Alpha,10.5\n2,Beta,20.0\n3,Gamma,35.2"
    df, meta = parse_csv(content)
    val = validate_dataset(df, meta)
    prof = profile_dataset(df, meta)
    quality = calculate_quality_score(prof, val)
    return prof, val, quality


def test_generate_json_report(sample_assessment):
    prof, val, quality = sample_assessment
    json_str = generate_json_report(prof, val, quality)
    parsed = json.loads(json_str)

    assert "report_version" in parsed
    assert "overall_quality" in parsed
    assert "dimensions" in parsed
    assert parsed["overall_quality"]["grade"] in ["A", "B", "C", "D", "F"]


def test_generate_markdown_report(sample_assessment):
    prof, val, quality = sample_assessment
    md_str = generate_markdown_report(prof, val, quality)

    assert "# 📊 Data Quality Audit Report" in md_str
    assert "Executive Summary KPIs" in md_str
    assert "Quality Dimension Breakdown" in md_str
    assert "| **Total Rows** |" in md_str


def test_generate_html_report(sample_assessment):
    prof, val, quality = sample_assessment
    html_str = generate_html_report(prof, val, quality)

    assert "<!DOCTYPE html>" in html_str
    assert "<title>Dataset Quality Report" in html_str
    assert "score-hero" in html_str
    assert "dim-card" in html_str
