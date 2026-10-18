"""
Dataset Validator Module
Performs structural, schema, and health sanity checks prior to deep profiling.
"""

from typing import Dict, List, Optional
import pandas as pd


def validate_dataset(df: pd.DataFrame, metadata: Optional[Dict] = None) -> Dict:
    """
    Validates the structure and basic integrity of the ingested DataFrame.

    Returns:
        A dictionary with validation status, errors, warnings, and column-level notices.
    """
    result: Dict = {
        "is_valid": True,
        "can_profile": True,
        "fatal_errors": [],
        "warnings": [],
        "info": [],
        "column_issues": {},
    }

    metadata = metadata or {}

    # 1. Check for empty dataset
    if df is None or df.empty:
        result["is_valid"] = False
        result["can_profile"] = False
        result["fatal_errors"].append("The dataset contains 0 rows or is completely empty.")
        return result

    if len(df.columns) == 0:
        result["is_valid"] = False
        result["can_profile"] = False
        result["fatal_errors"].append("The dataset contains 0 columns.")
        return result

    # 2. Check for delimiter failure (single column containing delimiters)
    if len(df.columns) == 1:
        col_name = str(df.columns[0])
        common_delims = [",", ";", "\t", "|"]
        found_in_header = [d for d in common_delims if d in col_name]

        sample_rows = df[col_name].dropna().head(10).astype(str).tolist()
        found_in_rows = [
            d for d in common_delims
            if any(d in str(r) for r in sample_rows)
        ]

        if found_in_header or found_in_rows:
            suspect = (found_in_header + found_in_rows)[0]
            result["warnings"].append(
                f"Dataset parsed as a single column '{col_name}', but delimiter '{suspect}' "
                f"was detected in values. You may need to specify the correct delimiter."
            )

    # 3. Column header analysis
    col_names = [str(c) for c in df.columns]
    unnamed_cols = [c for c in col_names if c.startswith("Unnamed:") or c.strip() == ""]
    if unnamed_cols:
        result["warnings"].append(
            f"Found {len(unnamed_cols)} unnamed or index-exported column(s): {', '.join(unnamed_cols[:3])}"
            + (f" and {len(unnamed_cols)-3} more" if len(unnamed_cols) > 3 else "")
        )

    # Duplicate column names check
    seen = set()
    dup_cols = []
    for c in col_names:
        clean = c.split(".")[0] if "." in c and c.split(".")[-1].isdigit() else c
        if clean in seen and c not in dup_cols:
            dup_cols.append(c)
        seen.add(clean)

    if dup_cols:
        result["warnings"].append(
            f"Potential duplicate column headers detected: {', '.join(dup_cols[:3])}"
        )

    # 4. Row and cell integrity
    total_rows = len(df)
    total_cols = len(df.columns)

    if total_rows < 5:
        result["info"].append(
            f"Dataset is very small ({total_rows} rows). Statistical distributions may have limited variance."
        )

    # All-NaN rows check
    all_nan_rows = df.isna().all(axis=1).sum()
    if all_nan_rows > 0:
        result["warnings"].append(
            f"Dataset contains {all_nan_rows} completely empty (all-NaN) row(s) ({(all_nan_rows/total_rows)*100:.1f}%)."
        )

    # All-NaN columns check
    all_nan_cols = [c for c in df.columns if df[c].isna().all()]
    if all_nan_cols:
        result["warnings"].append(
            f"Dataset contains {len(all_nan_cols)} completely empty (100% missing) column(s): {', '.join(map(str, all_nan_cols[:3]))}"
        )

    # Constant columns check (only 1 unique value)
    constant_cols = [c for c in df.columns if df[c].nunique(dropna=True) == 1]
    if constant_cols:
        result["info"].append(
            f"Found {len(constant_cols)} constant column(s) with zero variance: {', '.join(map(str, constant_cols[:3]))}"
        )

    # 5. Populate per-column issues
    for col in df.columns:
        col_str = str(col)
        issues: List[str] = []
        series = df[col]

        missing_cnt = series.isna().sum()
        missing_pct = (missing_cnt / total_rows) * 100 if total_rows > 0 else 0

        if missing_pct >= 90:
            issues.append(f"Severe missingness: {missing_pct:.1f}% values missing")
        elif missing_pct >= 30:
            issues.append(f"Moderate missingness: {missing_pct:.1f}% values missing")

        distinct_cnt = series.nunique(dropna=True)
        if distinct_cnt == 1:
            issues.append("Constant column (single unique value)")
        elif distinct_cnt == 0:
            issues.append("Entirely empty column (0 non-null values)")

        # Check for whitespace anomalies in string columns
        if pd.api.types.is_string_dtype(series) or series.dtype == "object":
            str_sample = series.dropna().astype(str)
            whitespace_count = str_sample.apply(
                lambda s: len(s) != len(s.strip())
            ).sum()
            if whitespace_count > 0:
                issues.append(
                    f"{whitespace_count} value(s) contain un-trimmed leading/trailing whitespace"
                )

        if issues:
            result["column_issues"][col_str] = issues

    return result
