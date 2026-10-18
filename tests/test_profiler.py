"""
Unit tests for the Dataset Profiler Module.
"""

import numpy as np
import pandas as pd
import pytest
from src.profiler import (
    infer_logical_type,
    detect_outliers_iqr,
    detect_outliers_zscore,
    profile_column,
    profile_dataset,
)


def test_infer_logical_type():
    assert infer_logical_type(pd.Series([True, False, True])) == "Boolean"
    assert infer_logical_type(pd.Series(["yes", "no", "yes"])) == "Boolean"
    assert infer_logical_type(pd.Series([1, 2, 3, 4])) == "Integer"
    assert infer_logical_type(pd.Series([1.5, 2.7, 3.2])) == "Float"
    assert "Datetime" in infer_logical_type(pd.Series(["2024-01-01", "2024-01-02", "2024-01-03"]))
    assert infer_logical_type(pd.Series(["CategoryA", "CategoryB", "CategoryA"] * 20)) == "Categorical"


def test_detect_outliers_iqr():
    # Normal distribution with extreme outlier
    data = [10, 11, 10, 12, 11, 10, 12, 1000]
    series = pd.Series(data)
    res = detect_outliers_iqr(series)
    assert res["outlier_count"] == 1
    assert 1000 in res["sample_outliers"]
    assert res["upper_bound"] < 1000


def test_detect_outliers_zscore():
    data = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 1000]
    series = pd.Series(data)
    res = detect_outliers_zscore(series, threshold=2.5)
    assert res["outlier_count"] >= 1


def test_profile_column_numeric():
    series = pd.Series([10, 20, 30, 40, np.nan], name="val")
    prof = profile_column(series, total_rows=5)
    assert prof["name"] == "val"
    assert prof["missing_count"] == 1
    assert prof["missing_percentage"] == 20.0
    assert prof["numeric_stats"] is not None
    assert prof["numeric_stats"]["mean"] == 25.0
    assert prof["numeric_stats"]["median"] == 25.0


def test_profile_dataset():
    df = pd.DataFrame({
        "id": [1, 2, 3, 1],
        "category": ["A", "B", "A", "A"],
        "price": [10.0, 20.0, np.nan, 10.0],
    })
    prof = profile_dataset(df)
    assert prof["overview"]["total_rows"] == 4
    assert prof["overview"]["total_columns"] == 3
    assert prof["overview"]["duplicate_rows_count"] == 1
    assert prof["overview"]["total_missing_cells"] == 1
    assert "price" in prof["columns"]
    assert "category" in prof["columns"]
