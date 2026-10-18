"""
Unit tests for the Data Quality Engine Module.
"""

import numpy as np
import pandas as pd
import pytest
from src.profiler import profile_dataset
from src.validator import validate_dataset
from src.quality_engine import calculate_quality_score, calculate_column_health


def test_quality_score_pristine_data():
    df = pd.DataFrame({
        "id": range(1, 101),
        "name": [f"User_{i}" for i in range(1, 101)],
        "score": np.random.normal(50, 5, 100),
    })
    meta = {"filename": "pristine.csv"}
    val = validate_dataset(df, meta)
    prof = profile_dataset(df, meta)
    quality = calculate_quality_score(prof, val)

    assert quality["overall_score"] >= 85.0
    assert quality["grade"] in ["A", "B"]
    assert quality["dimensions"]["completeness"]["score"] == 100.0
    assert quality["dimensions"]["uniqueness"]["score"] == 100.0


def test_quality_score_heavily_degraded_data():
    # 50% missing, 50% duplicates, constant column
    df = pd.DataFrame({
        "all_null": [np.nan] * 50,
        "constant": ["SAME"] * 50,
        "duplicates": [1, 2] * 25,
    })
    meta = {"filename": "bad.csv"}
    val = validate_dataset(df, meta)
    prof = profile_dataset(df, meta)
    quality = calculate_quality_score(prof, val)

    assert quality["overall_score"] < 65.0
    assert quality["grade"] in ["D", "F"]
    assert len(quality["recommendations"]) > 0


def test_column_health_grading():
    clean_col = {
        "missing_percentage": 0.0,
        "is_constant": False,
        "outliers_iqr": {"outlier_percentage": 0.0},
    }
    score, grade, issues = calculate_column_health(clean_col)
    assert score == 100.0
    assert grade == "A"
    assert len(issues) == 0

    dirty_col = {
        "missing_percentage": 95.0,
        "is_constant": True,
        "outliers_iqr": {"outlier_percentage": 10.0},
    }
    score_dirty, grade_dirty, issues_dirty = calculate_column_health(dirty_col)
    assert score_dirty < 50.0
    assert grade_dirty == "F"
    assert len(issues_dirty) >= 2
