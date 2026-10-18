"""
Unit tests for the Dataset Validator Module.
"""

import numpy as np
import pandas as pd
import pytest
from src.validator import validate_dataset


def test_validate_empty_dataset():
    df_empty = pd.DataFrame()
    val = validate_dataset(df_empty)
    assert not val["is_valid"]
    assert not val["can_profile"]
    assert len(val["fatal_errors"]) > 0


def test_validate_clean_dataset():
    df = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "score": [88.5, 92.0, 79.5, 95.0, 84.0],
    })
    val = validate_dataset(df)
    assert val["is_valid"]
    assert val["can_profile"]
    assert len(val["fatal_errors"]) == 0
    assert len(val["warnings"]) == 0


def test_validate_delimiter_failure():
    # A single column containing commas
    df = pd.DataFrame({"id,name,score": ["1,Alice,88", "2,Bob,92", "3,Charlie,79"]})
    val = validate_dataset(df)
    assert any("delimiter" in w.lower() for w in val["warnings"])


def test_validate_unnamed_and_duplicate_columns():
    df = pd.DataFrame({
        "id": [1, 2],
        "Unnamed: 0": [0, 1],
        "score": [10, 20],
        "score.1": [10, 20],
    })
    val = validate_dataset(df)
    assert any("unnamed" in w.lower() for w in val["warnings"])
    assert any("duplicate" in w.lower() for w in val["warnings"])


def test_validate_all_nan_rows_and_cols():
    df = pd.DataFrame({
        "id": [1, np.nan, 3],
        "empty_col": [np.nan, np.nan, np.nan],
    })
    val = validate_dataset(df)
    assert any("empty" in w.lower() for w in val["warnings"])
    assert "empty_col" in val["column_issues"]
