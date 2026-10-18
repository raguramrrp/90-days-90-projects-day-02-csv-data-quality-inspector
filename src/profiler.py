"""
Dataset Profiler Module
Performs comprehensive exploratory data analysis, type inference, missing value profiling,
outlier detection (IQR & Z-score), and column-level statistical analysis.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from dateutil.parser import parse as parse_date


def infer_logical_type(series: pd.Series) -> str:
    """
    Infers the real semantic/logical data type of a pandas Series beyond its raw storage dtype.
    Categories: 'Boolean', 'Integer', 'Float', 'Datetime', 'Categorical', 'Text', 'Mixed'.
    """
    non_null = series.dropna()
    total_non_null = len(non_null)

    if total_non_null == 0:
        return "Empty"

    # 1. Native booleans or boolean-like strings
    if pd.api.types.is_bool_dtype(series):
        return "Boolean"

    is_string_or_obj = (
        pd.api.types.is_string_dtype(series) or series.dtype == "object"
    )

    if is_string_or_obj:
        # Check if unique string values are boolean-like
        unique_lower = {str(v).strip().lower() for v in non_null.unique()[:20]}
        if unique_lower.issubset({"true", "false", "yes", "no", "t", "f", "1", "0", "y", "n"}):
            return "Boolean"

    # 2. Check for numeric types (exclude boolean)
    if pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series):
        # Distinguish integer vs float
        if pd.api.types.is_integer_dtype(series):
            return "Integer"
        # Check if all floats are integers (e.g. 1.0, 2.0 with NaN)
        try:
            if (non_null % 1 == 0).all():
                return "Integer"
        except Exception:
            pass
        return "Float"

    # 3. Check if object/string column is actually numeric
    if is_string_or_obj:
        sample = non_null.head(100).astype(str)
        # Attempt conversion
        try:
            converted = pd.to_numeric(sample.str.replace(",", "").str.strip(), errors="coerce")
            valid_num_pct = converted.notna().sum() / len(sample)
            if valid_num_pct > 0.90:
                # Mostly numeric, check if integer or float
                all_converted = pd.to_numeric(
                    non_null.astype(str).str.replace(",", "").str.strip(), errors="coerce"
                )
                if (all_converted.dropna() % 1 == 0).all():
                    return "Integer (as string)"
                return "Float (as string)"
        except Exception:
            pass

    # 4. Check for Datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return "Datetime"

    if is_string_or_obj:
        sample = non_null.head(50).astype(str)
        # Must look like dates or timestamps
        date_successes = 0
        for val in sample:
            v_str = str(val).strip()
            # Avoid single numbers or short words being parsed as dates
            if len(v_str) >= 6 and any(sep in v_str for sep in ["-", "/", ":", ","]):
                try:
                    parse_date(v_str, fuzzy=False)
                    date_successes += 1
                except Exception:
                    pass
        if date_successes / len(sample) >= 0.80:
            return "Datetime (as string)"

    # 5. Check Categorical vs Text
    unique_count = non_null.nunique()
    if unique_count <= 50 or (total_non_null > 0 and (unique_count / total_non_null) < 0.05):
        return "Categorical"

    # 6. Check Text
    avg_len = non_null.astype(str).str.len().mean()
    if avg_len > 30:
        return "Text (Long)"

    return "Text"


def detect_outliers_iqr(series: pd.Series) -> Dict[str, Any]:
    """
    Detects numerical outliers using Tukey's Interquartile Range (IQR) method.
    Outlier if x < Q1 - 1.5*IQR or x > Q3 + 1.5*IQR.
    """
    numeric_series = pd.to_numeric(series, errors="coerce").dropna()
    if len(numeric_series) < 5:
        return {
            "method": "IQR",
            "outlier_count": 0,
            "outlier_percentage": 0.0,
            "lower_bound": None,
            "upper_bound": None,
            "sample_outliers": [],
        }

    q1 = float(numeric_series.quantile(0.25))
    q3 = float(numeric_series.quantile(0.75))
    iqr = q3 - q1

    lower_bound = round(q1 - 1.5 * iqr, 4)
    upper_bound = round(q3 + 1.5 * iqr, 4)

    outliers = numeric_series[(numeric_series < lower_bound) | (numeric_series > upper_bound)]
    count = int(len(outliers))
    pct = round((count / len(numeric_series)) * 100, 2)

    return {
        "method": "IQR",
        "outlier_count": count,
        "outlier_percentage": pct,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "sample_outliers": [round(float(x), 4) for x in outliers.head(5).tolist()],
    }


def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> Dict[str, Any]:
    """
    Detects numerical outliers using standard Z-score method (|z| > threshold).
    """
    numeric_series = pd.to_numeric(series, errors="coerce").dropna()
    if len(numeric_series) < 5:
        return {
            "method": "Z-score",
            "outlier_count": 0,
            "outlier_percentage": 0.0,
            "threshold": threshold,
        }

    mean = float(numeric_series.mean())
    std = float(numeric_series.std())

    if std == 0 or np.isnan(std):
        return {
            "method": "Z-score",
            "outlier_count": 0,
            "outlier_percentage": 0.0,
            "threshold": threshold,
        }

    z_scores = np.abs((numeric_series - mean) / std)
    outliers = numeric_series[z_scores > threshold]
    count = int(len(outliers))
    pct = round((count / len(numeric_series)) * 100, 2)

    return {
        "method": "Z-score",
        "outlier_count": count,
        "outlier_percentage": pct,
        "threshold": threshold,
        "sample_outliers": [round(float(x), 4) for x in outliers.head(5).tolist()],
    }


def profile_column(series: pd.Series, total_rows: int) -> Dict[str, Any]:
    """
    Generates a full statistical and structural profile for a single column.
    """
    col_name = str(series.name)
    raw_dtype = str(series.dtype)
    logical_type = infer_logical_type(series)

    non_null_series = series.dropna()
    missing_count = int(series.isna().sum())
    missing_pct = round((missing_count / total_rows) * 100, 2) if total_rows > 0 else 0.0

    distinct_count = int(non_null_series.nunique())
    distinct_ratio = (
        round(distinct_count / len(non_null_series), 4) if len(non_null_series) > 0 else 0.0
    )

    is_constant = distinct_count == 1
    is_primary_key_candidate = (
        distinct_count == total_rows and missing_count == 0 and total_rows > 1
    )

    profile: Dict[str, Any] = {
        "name": col_name,
        "raw_dtype": raw_dtype,
        "logical_type": logical_type,
        "total_count": total_rows,
        "non_null_count": int(len(non_null_series)),
        "missing_count": missing_count,
        "missing_percentage": missing_pct,
        "distinct_count": distinct_count,
        "distinct_ratio": distinct_ratio,
        "is_constant": is_constant,
        "is_primary_key_candidate": is_primary_key_candidate,
        "numeric_stats": None,
        "categorical_stats": None,
        "datetime_stats": None,
        "outliers_iqr": None,
        "outliers_zscore": None,
    }

    # Numerical statistics (strictly exclude boolean)
    is_numeric = (
        pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series)
    ) or ("Integer" in logical_type or "Float" in logical_type)

    if is_numeric and logical_type != "Boolean":
        num_s = pd.to_numeric(non_null_series, errors="coerce").dropna()
        if len(num_s) > 0:
            mean_val = float(num_s.mean())
            std_val = float(num_s.std()) if len(num_s) > 1 else 0.0
            min_val = float(num_s.min())
            q25 = float(num_s.quantile(0.25))
            median_val = float(num_s.median())
            q75 = float(num_s.quantile(0.75))
            max_val = float(num_s.max())
            skew_val = float(num_s.skew()) if len(num_s) > 2 else 0.0
            kurt_val = float(num_s.kurtosis()) if len(num_s) > 3 else 0.0

            zeros_cnt = int((num_s == 0).sum())
            zeros_pct = round((zeros_cnt / len(num_s)) * 100, 2)
            negative_cnt = int((num_s < 0).sum())
            negative_pct = round((negative_cnt / len(num_s)) * 100, 2)

            profile["numeric_stats"] = {
                "mean": round(mean_val, 4),
                "std": round(std_val, 4),
                "min": round(min_val, 4),
                "q25": round(q25, 4),
                "median": round(median_val, 4),
                "q75": round(q75, 4),
                "max": round(max_val, 4),
                "iqr": round(q75 - q25, 4),
                "skewness": round(skew_val, 4) if not np.isnan(skew_val) else 0.0,
                "kurtosis": round(kurt_val, 4) if not np.isnan(kurt_val) else 0.0,
                "zeros_count": zeros_cnt,
                "zeros_percentage": zeros_pct,
                "negative_count": negative_cnt,
                "negative_percentage": negative_pct,
            }

            profile["outliers_iqr"] = detect_outliers_iqr(num_s)
            profile["outliers_zscore"] = detect_outliers_zscore(num_s)

    # Categorical and text statistics
    if logical_type in ["Categorical", "Text", "Text (Long)", "Boolean"]:
        top_counts = non_null_series.value_counts().head(5)
        top_frequent = []
        for val, cnt in top_counts.items():
            top_frequent.append({
                "value": str(val),
                "count": int(cnt),
                "percentage": round((cnt / len(non_null_series)) * 100, 2),
            })

        # Length analysis
        str_series = non_null_series.astype(str)
        lens = str_series.str.len()
        whitespace_issues = int((str_series.str.strip() != str_series).sum())

        profile["categorical_stats"] = {
            "mode": str(top_counts.index[0]) if not top_counts.empty else None,
            "mode_frequency": int(top_counts.iloc[0]) if not top_counts.empty else 0,
            "top_frequent": top_frequent,
            "min_length": int(lens.min()) if not lens.empty else 0,
            "max_length": int(lens.max()) if not lens.empty else 0,
            "avg_length": round(float(lens.mean()), 2) if not lens.empty else 0.0,
            "whitespace_issues": whitespace_issues,
        }

    # Datetime statistics
    if "Datetime" in logical_type:
        try:
            dt_series = pd.to_datetime(non_null_series, errors="coerce").dropna()
            if len(dt_series) > 0:
                min_dt = dt_series.min()
                max_dt = dt_series.max()
                days_span = (max_dt - min_dt).total_seconds() / 86400.0
                profile["datetime_stats"] = {
                    "min_date": str(min_dt),
                    "max_date": str(max_dt),
                    "span_days": round(days_span, 1),
                }
        except Exception:
            pass

    return profile


def profile_dataset(df: pd.DataFrame, metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Executes an end-to-end exploratory data profiling suite on the ingested dataset.

    Returns:
        Structured dictionary containing overview KPIs, missing matrix stats,
        duplicate analysis, outlier aggregates, and per-column profiles.
    """
    metadata = metadata or {}
    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols

    # 1. Duplicate row analysis
    dup_rows_mask = df.duplicated()
    dup_rows_count = int(dup_rows_mask.sum())
    dup_rows_pct = round((dup_rows_count / total_rows) * 100, 2) if total_rows > 0 else 0.0

    # 2. Global missingness analysis
    missing_by_col = df.isna().sum()
    total_missing_cells = int(missing_by_col.sum())
    overall_missing_pct = (
        round((total_missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0.0
    )

    empty_rows_count = int(df.isna().all(axis=1).sum())
    empty_cols_count = int((missing_by_col == total_rows).sum())

    # 3. Column profiles
    columns_profile: Dict[str, Dict[str, Any]] = {}
    total_numeric_cols = 0
    total_categorical_cols = 0
    total_datetime_cols = 0
    total_boolean_cols = 0
    total_outliers_detected = 0

    for col in df.columns:
        col_prof = profile_column(df[col], total_rows)
        columns_profile[str(col)] = col_prof

        log_type = col_prof["logical_type"]
        if "Integer" in log_type or "Float" in log_type:
            total_numeric_cols += 1
            if col_prof.get("outliers_iqr"):
                total_outliers_detected += col_prof["outliers_iqr"]["outlier_count"]
        elif "Categorical" in log_type or "Text" in log_type:
            total_categorical_cols += 1
        elif "Datetime" in log_type:
            total_datetime_cols += 1
        elif "Boolean" in log_type:
            total_boolean_cols += 1

    # Memory calculation
    memory_usage_bytes = int(df.memory_usage(deep=True).sum())
    if memory_usage_bytes < 1024 * 1024:
        memory_usage_str = f"{memory_usage_bytes / 1024:.2f} KB"
    else:
        memory_usage_str = f"{memory_usage_bytes / (1024 * 1024):.2f} MB"

    return {
        "metadata": metadata,
        "overview": {
            "total_rows": total_rows,
            "total_columns": total_cols,
            "total_cells": total_cells,
            "memory_usage_bytes": memory_usage_bytes,
            "memory_usage_str": memory_usage_str,
            "duplicate_rows_count": dup_rows_count,
            "duplicate_rows_percentage": dup_rows_pct,
            "total_missing_cells": total_missing_cells,
            "overall_missing_percentage": overall_missing_pct,
            "empty_rows_count": empty_rows_count,
            "empty_columns_count": empty_cols_count,
            "total_numeric_columns": total_numeric_cols,
            "total_categorical_columns": total_categorical_cols,
            "total_datetime_columns": total_datetime_cols,
            "total_boolean_columns": total_boolean_cols,
            "total_outliers_detected": total_outliers_detected,
        },
        "columns": columns_profile,
    }
