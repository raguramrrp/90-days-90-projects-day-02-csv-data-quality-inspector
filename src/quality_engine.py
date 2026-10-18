"""
Data Quality Engine Module
Calculates multi-dimensional data quality scores, assigns column-level health grades,
and produces prioritized automated remediation recommendations.
"""

from typing import Any, Dict, List, Tuple


def calculate_column_health(col_prof: Dict[str, Any]) -> Tuple[float, str, List[str]]:
    """
    Evaluates health score (0-100) and letter grade for an individual column.
    """
    score = 100.0
    issues: List[str] = []

    missing_pct = col_prof.get("missing_percentage", 0.0)
    if missing_pct >= 90:
        score -= 60
        issues.append(f"Severe missingness: {missing_pct:.1f}% values missing")
    elif missing_pct >= 50:
        score -= 40
        issues.append(f"High missingness: {missing_pct:.1f}% values missing")
    elif missing_pct >= 20:
        score -= 20
        issues.append(f"Moderate missingness: {missing_pct:.1f}% values missing")
    elif missing_pct > 0:
        score -= missing_pct * 0.5
        issues.append(f"Minor missingness: {missing_pct:.1f}% values missing")

    if col_prof.get("is_constant"):
        score -= 30
        issues.append("Constant column (single unique value; zero informational entropy)")

    # Outliers in numeric columns
    outliers = col_prof.get("outliers_iqr")
    if outliers and outliers.get("outlier_percentage", 0) > 0:
        outlier_pct = outliers["outlier_percentage"]
        if outlier_pct > 5.0:
            score -= min(25.0, outlier_pct * 2.0)
            issues.append(f"High outlier volume: {outlier_pct:.1f}% statistical outliers detected")
        elif outlier_pct > 0:
            score -= outlier_pct * 1.0
            issues.append(f"Minor outliers: {outlier_pct:.1f}% outliers detected")

    # Whitespace or type issues
    cat_stats = col_prof.get("categorical_stats")
    if cat_stats and cat_stats.get("whitespace_issues", 0) > 0:
        ws_cnt = cat_stats["whitespace_issues"]
        score -= min(15.0, ws_cnt * 1.5)
        issues.append(f"{ws_cnt} value(s) contain un-trimmed whitespace")

    log_type = col_prof.get("logical_type", "")
    if "(as string)" in log_type:
        score -= 10
        issues.append(f"Type mismatch: Column appears to be {log_type}")

    final_score = max(0.0, min(100.0, round(score, 1)))

    if final_score >= 90:
        grade = "A"
    elif final_score >= 80:
        grade = "B"
    elif final_score >= 70:
        grade = "C"
    elif final_score >= 60:
        grade = "D"
    else:
        grade = "F"

    return final_score, grade, issues


def calculate_quality_score(profile: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes holistic dataset quality score across 5 key dimensions:
    1. Completeness (25%)
    2. Uniqueness (20%)
    3. Consistency & Validity (20%)
    4. Outlier Health (15%)
    5. Structural Integrity (20%)

    Returns:
        Structured dictionary with composite score, dimension breakdown,
        column grades, and prioritized recommendations.
    """
    overview = profile.get("overview", {})
    columns = profile.get("columns", {})
    total_rows = overview.get("total_rows", 0)
    total_cols = overview.get("total_columns", 0)

    recommendations: List[Dict[str, str]] = []

    # 1. Dimension: Completeness (Weight: 25%)
    overall_missing_pct = overview.get("overall_missing_percentage", 0.0)
    completeness_score = max(0.0, 100.0 - (overall_missing_pct * 2.5))
    if overview.get("empty_rows_count", 0) > 0:
        completeness_score -= min(20.0, overview["empty_rows_count"] * 5.0)
    if overview.get("empty_columns_count", 0) > 0:
        completeness_score -= overview["empty_columns_count"] * 15.0
    completeness_score = max(0.0, min(100.0, round(completeness_score, 1)))

    # 2. Dimension: Uniqueness (Weight: 20%)
    dup_rows_cnt = overview.get("duplicate_rows_count", 0)
    dup_rows_pct = overview.get("duplicate_rows_percentage", 0.0)
    if dup_rows_cnt == 0:
        uniqueness_score = 100.0
    else:
        uniqueness_score = max(0.0, 100.0 - 10.0 - (dup_rows_pct * 4.0))
    uniqueness_score = max(0.0, min(100.0, round(uniqueness_score, 1)))

    # 3. Dimension: Consistency & Validity (Weight: 20%)
    validity_score = 100.0
    type_mismatches = 0
    whitespace_columns = 0
    negative_value_columns = 0

    for col_name, c_prof in columns.items():
        if "(as string)" in c_prof.get("logical_type", ""):
            type_mismatches += 1
        c_stats = c_prof.get("categorical_stats")
        if c_stats and c_stats.get("whitespace_issues", 0) > 0:
            whitespace_columns += 1
        n_stats = c_prof.get("numeric_stats")
        if n_stats and n_stats.get("negative_count", 0) > 0:
            negative_value_columns += 1

    validity_score -= type_mismatches * 8.0
    validity_score -= whitespace_columns * 8.0
    validity_score -= negative_value_columns * 10.0
    validity_score = max(0.0, min(100.0, round(validity_score, 1)))

    # 4. Dimension: Outlier Health (Weight: 15%)
    numeric_cols = [
        c for c in columns.values()
        if c.get("outliers_iqr") is not None
    ]
    if numeric_cols:
        avg_outlier_pct = sum(
            c["outliers_iqr"].get("outlier_percentage", 0.0) for c in numeric_cols
        ) / len(numeric_cols)
        outlier_score = max(0.0, 100.0 - (avg_outlier_pct * 6.0) - (10.0 if negative_value_columns > 0 else 0.0))
    else:
        outlier_score = 100.0
    outlier_score = max(0.0, min(100.0, round(outlier_score, 1)))

    # 5. Dimension: Structural Integrity (Weight: 20%)
    structure_score = 100.0
    fatal_errors = validation.get("fatal_errors", [])
    warnings = validation.get("warnings", [])

    if fatal_errors:
        structure_score -= 50.0
    structure_score -= len(warnings) * 5.0

    constant_cols_count = sum(1 for c in columns.values() if c.get("is_constant"))
    structure_score -= constant_cols_count * 15.0
    structure_score = max(0.0, min(100.0, round(structure_score, 1)))

    # Composite Score
    weights = {
        "completeness": 0.25,
        "uniqueness": 0.20,
        "validity": 0.20,
        "outlier_health": 0.15,
        "structural_integrity": 0.20,
    }
    composite_score = round(
        (completeness_score * weights["completeness"])
        + (uniqueness_score * weights["uniqueness"])
        + (validity_score * weights["validity"])
        + (outlier_score * weights["outlier_health"])
        + (structure_score * weights["structural_integrity"]),
        1,
    )
    composite_score = max(0.0, min(100.0, composite_score))

    # Overall Letter Grade
    if composite_score >= 90:
        overall_grade = "A"
        grade_desc = "Excellent / Production Ready"
        grade_color = "#22c55e"
    elif composite_score >= 80:
        overall_grade = "B"
        grade_desc = "Good / Minor Remediation Recommended"
        grade_color = "#3b82f6"
    elif composite_score >= 70:
        overall_grade = "C"
        grade_desc = "Fair / Moderate Cleaning Required"
        grade_color = "#eab308"
    elif composite_score >= 60:
        overall_grade = "D"
        grade_desc = "Poor / Significant Data Risks"
        grade_color = "#f97316"
    else:
        overall_grade = "F"
        grade_desc = "Critical / Major Inconsistencies"
        grade_color = "#ef4444"

    # Evaluate individual column health
    column_scores: Dict[str, Dict[str, Any]] = {}
    for col_name, c_prof in columns.items():
        c_score, c_grade, c_issues = calculate_column_health(c_prof)
        column_scores[col_name] = {
            "score": c_score,
            "grade": c_grade,
            "issues": c_issues,
            "logical_type": c_prof.get("logical_type"),
            "missing_percentage": c_prof.get("missing_percentage"),
        }

    # Generate Prioritized Recommendations
    # Critical Recommendations
    if overview.get("duplicate_rows_count", 0) > 0:
        recommendations.append({
            "priority": "HIGH",
            "category": "Deduplication",
            "message": f"Found {overview['duplicate_rows_count']} duplicate row(s) ({overview['duplicate_rows_percentage']}%). Apply deduplication before data warehousing or model training.",
            "action": "df.drop_duplicates(inplace=True)",
        })

    if overview.get("empty_rows_count", 0) > 0:
        recommendations.append({
            "priority": "HIGH",
            "category": "Completeness",
            "message": f"Dataset has {overview['empty_rows_count']} all-null row(s). These provide zero signal.",
            "action": "df.dropna(how='all', inplace=True)",
        })

    for col_name, c_prof in columns.items():
        # Empty column
        if c_prof.get("missing_percentage", 0) == 100.0:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Missing Data",
                "message": f"Column '{col_name}' is 100% missing. Remove this redundant column to optimize memory.",
                "action": f"df.drop(columns=['{col_name}'], inplace=True)",
            })
        elif c_prof.get("missing_percentage", 0) >= 50.0:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Missing Data",
                "message": f"Column '{col_name}' has {c_prof['missing_percentage']}% missing values. Consider domain imputation or dropping.",
                "action": f"# Impute or drop '{col_name}' based on business rules",
            })

        # Constant column
        if c_prof.get("is_constant") and total_rows > 1:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Feature Variance",
                "message": f"Column '{col_name}' is constant (zero variance). It provides no discriminatory power for analytics or ML.",
                "action": f"df.drop(columns=['{col_name}'], inplace=True)",
            })

        # Type conversion
        log_type = c_prof.get("logical_type", "")
        if "Datetime (as string)" in log_type:
            recommendations.append({
                "priority": "HIGH",
                "category": "Type Consistency",
                "message": f"Column '{col_name}' contains date strings. Convert to native datetime for temporal operations.",
                "action": f"df['{col_name}'] = pd.to_datetime(df['{col_name}'], errors='coerce')",
            })
        elif "Integer (as string)" in log_type or "Float (as string)" in log_type:
            recommendations.append({
                "priority": "HIGH",
                "category": "Type Consistency",
                "message": f"Column '{col_name}' stores numerical values as strings/objects. Cast to numeric.",
                "action": f"df['{col_name}'] = pd.to_numeric(df['{col_name}'], errors='coerce')",
            })

        # Whitespace
        c_stats = c_prof.get("categorical_stats")
        if c_stats and c_stats.get("whitespace_issues", 0) > 0:
            recommendations.append({
                "priority": "LOW",
                "category": "Text Hygiene",
                "message": f"Column '{col_name}' contains {c_stats['whitespace_issues']} values with untrimmed whitespace.",
                "action": f"df['{col_name}'] = df['{col_name}'].astype(str).str.strip()",
            })

        # Extreme Outliers
        outliers = c_prof.get("outliers_iqr")
        if outliers and outliers.get("outlier_count", 0) > 0:
            o_pct = outliers["outlier_percentage"]
            if o_pct > 3.0:
                recommendations.append({
                    "priority": "MEDIUM",
                    "category": "Outliers",
                    "message": f"Column '{col_name}' has {outliers['outlier_count']} IQR outliers ({o_pct}%). Evaluate winsorization or domain capping.",
                    "action": f"# Inspect bounds [{outliers['lower_bound']}, {outliers['upper_bound']}] for '{col_name}'",
                })

    return {
        "overall_score": composite_score,
        "grade": overall_grade,
        "grade_description": grade_desc,
        "grade_color": grade_color,
        "dimensions": {
            "completeness": {
                "score": completeness_score,
                "weight": weights["completeness"],
                "label": "Completeness",
                "description": "Measures missing data and empty row/column density",
            },
            "uniqueness": {
                "score": uniqueness_score,
                "weight": weights["uniqueness"],
                "label": "Uniqueness",
                "description": "Measures exact duplicate rows and entity duplication",
            },
            "validity": {
                "score": validity_score,
                "weight": weights["validity"],
                "label": "Consistency & Validity",
                "description": "Measures logical type concordance, whitespace hygiene, and formatting",
            },
            "outlier_health": {
                "score": outlier_score,
                "weight": weights["outlier_health"],
                "label": "Outlier Health",
                "description": "Measures prevalence of statistical anomalies across numerical dimensions",
            },
            "structural_integrity": {
                "score": structure_score,
                "weight": weights["structural_integrity"],
                "label": "Structural Integrity",
                "description": "Measures schema soundness, column variance, and header hygiene",
            },
        },
        "columns": column_scores,
        "recommendations": recommendations,
    }
