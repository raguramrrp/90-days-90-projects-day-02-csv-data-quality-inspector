"""
Report Generator Module
Produces comprehensive data quality reports in HTML (standalone presentation),
JSON (machine-readable pipeline schema), Markdown (PR/Slack summary), and CSV.
"""

import json
from typing import Any, Dict


def generate_json_report(
    profile: Dict[str, Any], validation: Dict[str, Any], quality: Dict[str, Any]
) -> str:
    """
    Serializes the complete profiling and quality assessment into a structured JSON string.
    """
    report_dict = {
        "report_version": "1.0.0",
        "system": "Automated Dataset Quality & Profiling Engine",
        "metadata": profile.get("metadata", {}),
        "overall_quality": {
            "score": quality.get("overall_score"),
            "grade": quality.get("grade"),
            "description": quality.get("grade_description"),
        },
        "dimensions": quality.get("dimensions", {}),
        "validation_status": {
            "is_valid": validation.get("is_valid"),
            "fatal_errors": validation.get("fatal_errors", []),
            "warnings": validation.get("warnings", []),
            "info": validation.get("info", []),
        },
        "overview": profile.get("overview", {}),
        "columns": profile.get("columns", {}),
        "column_scores": quality.get("columns", {}),
        "recommendations": quality.get("recommendations", []),
    }
    return json.dumps(report_dict, indent=2, default=str)


def generate_markdown_report(
    profile: Dict[str, Any], validation: Dict[str, Any], quality: Dict[str, Any]
) -> str:
    """
    Renders an executive data quality summary formatted as GitHub Flavored Markdown.
    """
    overview = profile.get("overview", {})
    score = quality.get("overall_score", 0.0)
    grade = quality.get("grade", "N/A")
    desc = quality.get("grade_description", "")
    metadata = profile.get("metadata", {})

    md = []
    md.append(f"# 📊 Data Quality Audit Report — {metadata.get('filename', 'dataset.csv')}\n")
    md.append(f"**Overall Quality Score:** `{score} / 100` | **Grade:** `{grade}` ({desc})\n")
    md.append("---\n")

    # Executive Summary KPIs
    md.append("## 📈 Executive Summary KPIs\n")
    md.append("| Metric | Value | Status |")
    md.append("| :--- | :--- | :--- |")
    md.append(f"| **Total Rows** | {overview.get('total_rows', 0):,} | ℹ️ Count |")
    md.append(f"| **Total Columns** | {overview.get('total_columns', 0):,} | ℹ️ Schema |")
    md.append(f"| **Memory Footprint** | {overview.get('memory_usage_str', '0 KB')} | ℹ️ Footprint |")

    missing_pct = overview.get("overall_missing_percentage", 0.0)
    missing_icon = "🟢" if missing_pct < 2 else ("🟡" if missing_pct < 10 else "🔴")
    md.append(f"| **Missing Cells** | {overview.get('total_missing_cells', 0):,} ({missing_pct}%) | {missing_icon} |")

    dup_pct = overview.get("duplicate_rows_percentage", 0.0)
    dup_icon = "🟢" if dup_pct == 0 else ("🟡" if dup_pct < 5 else "🔴")
    md.append(f"| **Duplicate Rows** | {overview.get('duplicate_rows_count', 0):,} ({dup_pct}%) | {dup_icon} |")

    outliers_cnt = overview.get("total_outliers_detected", 0)
    outlier_icon = "🟢" if outliers_cnt == 0 else "🟡"
    md.append(f"| **Outliers Detected (IQR)** | {outliers_cnt:,} | {outlier_icon} |\n")

    # Pillar Scores
    md.append("## 🎯 Quality Dimension Breakdown\n")
    md.append("| Dimension | Score (0-100) | Weight | Description |")
    md.append("| :--- | :--- | :--- | :--- |")
    for dim_key, dim_data in quality.get("dimensions", {}).items():
        s = dim_data["score"]
        bar = "█" * int(s / 10) + "░" * (10 - int(s / 10))
        md.append(f"| **{dim_data['label']}** | `{s:.1f}` ({bar}) | {int(dim_data['weight']*100)}% | {dim_data['description']} |")
    md.append("\n")

    # Column Health Table
    md.append("## 🔍 Column Health & Statistical Summary\n")
    md.append("| Column | Inferred Type | Missing % | Distinct | Outliers (IQR) | Health Grade | Issues |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    col_scores = quality.get("columns", {})
    for col_name, c_prof in profile.get("columns", {}).items():
        c_health = col_scores.get(col_name, {})
        grade_badge = f"`{c_health.get('grade', 'N/A')}` ({c_health.get('score', 0)}%)"
        iqr_info = c_prof.get("outliers_iqr")
        outliers_str = f"{iqr_info['outlier_count']} ({iqr_info['outlier_percentage']}%)" if iqr_info else "N/A"
        issues_str = "; ".join(c_health.get("issues", [])) or "None (Clean)"
        md.append(
            f"| `{col_name}` | {c_prof.get('logical_type', '')} | {c_prof.get('missing_percentage', 0)}% | "
            f"{c_prof.get('distinct_count', 0):,} | {outliers_str} | {grade_badge} | {issues_str} |"
        )
    md.append("\n")

    # Prioritized Recommendations
    recs = quality.get("recommendations", [])
    md.append("## 💡 Automated Remediation Recommendations\n")
    if not recs:
        md.append("🎉 **No critical data hygiene issues detected! Dataset is in pristine condition.**\n")
    else:
        for idx, rec in enumerate(recs, 1):
            badge = "🚨 CRITICAL" if rec["priority"] == "CRITICAL" else ("⚠️ HIGH" if rec["priority"] == "HIGH" else "ℹ️ MEDIUM/LOW")
            md.append(f"{idx}. **[{badge}] {rec['category']}:** {rec['message']}")
            if rec.get("action"):
                md.append(f"   ```python\n   {rec['action']}\n   ```")
        md.append("\n")

    return "\n".join(md)


def generate_html_report(
    profile: Dict[str, Any], validation: Dict[str, Any], quality: Dict[str, Any]
) -> str:
    """
    Renders an interactive, responsive standalone HTML audit report
    with embedded modern styling and CSS badges.
    """
    overview = profile.get("overview", {})
    metadata = profile.get("metadata", {})
    score = quality.get("overall_score", 0.0)
    grade = quality.get("grade", "N/A")
    desc = quality.get("grade_description", "")
    grade_color = quality.get("grade_color", "#3b82f6")
    dimensions = quality.get("dimensions", {})
    columns = profile.get("columns", {})
    col_scores = quality.get("columns", {})
    recommendations = quality.get("recommendations", [])

    # Build dimensions HTML
    dims_html = ""
    for dim_key, dim_data in dimensions.items():
        s = dim_data["score"]
        bar_color = "#22c55e" if s >= 80 else ("#eab308" if s >= 60 else "#ef4444")
        dims_html += f"""
        <div class="dim-card">
            <div class="dim-header">
                <span class="dim-label">{dim_data['label']}</span>
                <span class="dim-score" style="color: {bar_color}">{s:.1f} / 100</span>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width: {s}%; background-color: {bar_color};"></div>
            </div>
            <p class="dim-desc">{dim_data['description']} (Weight: {int(dim_data['weight']*100)}%)</p>
        </div>
        """

    # Build column rows HTML
    col_rows_html = ""
    for col_name, c_prof in columns.items():
        c_health = col_scores.get(col_name, {})
        c_grade = c_health.get("grade", "N/A")
        badge_bg = (
            "#dcfce7; color: #166534"
            if c_grade == "A"
            else (
                "#dbeafe; color: #1e40af"
                if c_grade == "B"
                else (
                    "#fef9c3; color: #854d0e"
                    if c_grade == "C"
                    else "#fee2e2; color: #991b1b"
                )
            )
        )
        iqr_info = c_prof.get("outliers_iqr")
        outliers_str = f"{iqr_info['outlier_count']} ({iqr_info['outlier_percentage']}%)" if iqr_info else "—"
        issues_list = c_health.get("issues", [])
        issues_badge = (
            '<span class="badge-clean">Clean</span>'
            if not issues_list
            else "<br>".join([f'<span class="badge-issue">• {iss}</span>' for iss in issues_list])
        )

        col_rows_html += f"""
        <tr>
            <td><strong>{col_name}</strong></td>
            <td><span class="tag-type">{c_prof.get('logical_type', '')}</span></td>
            <td>{c_prof.get('missing_count', 0)} ({c_prof.get('missing_percentage', 0)}%)</td>
            <td>{c_prof.get('distinct_count', 0):,}</td>
            <td>{outliers_str}</td>
            <td><span class="grade-pill" style="background-color: {badge_bg}; font-weight: bold; padding: 4px 10px; border-radius: 9999px;">{c_grade} ({c_health.get('score', 0)}%)</span></td>
            <td>{issues_badge}</td>
        </tr>
        """

    # Build recommendations HTML
    recs_html = ""
    if not recommendations:
        recs_html = '<div class="alert-clean">🎉 No critical data hygiene issues detected. Dataset passed quality benchmarks!</div>'
    else:
        for rec in recommendations:
            badge_class = "badge-crit" if rec["priority"] == "CRITICAL" else ("badge-high" if rec["priority"] == "HIGH" else "badge-med")
            action_snippet = f'<pre><code>{rec["action"]}</code></pre>' if rec.get("action") else ""
            recs_html += f"""
            <div class="rec-item">
                <div class="rec-header">
                    <span class="priority-badge {badge_class}">{rec['priority']}</span>
                    <span class="rec-category">[{rec['category']}]</span>
                    <span class="rec-msg">{rec['message']}</span>
                </div>
                {action_snippet}
            </div>
            """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dataset Quality Report — {metadata.get('filename', 'dataset.csv')}</title>
    <style>
        :root {{
            --bg: #f8fafc;
            --surface: #ffffff;
            --border: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --primary: #2563eb;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            padding: 32px 16px;
            line-height: 1.5;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}
        .header {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .header-title h1 {{ font-size: 24px; font-weight: 700; color: #1e293b; }}
        .header-title p {{ color: var(--text-muted); font-size: 14px; margin-top: 4px; }}
        .score-hero {{
            display: flex;
            align-items: center;
            gap: 16px;
            background: #f1f5f9;
            padding: 12px 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
        }}
        .score-circle {{
            font-size: 32px;
            font-weight: 800;
            color: {grade_color};
        }}
        .grade-badge {{
            font-size: 28px;
            font-weight: 900;
            padding: 4px 14px;
            border-radius: 8px;
            background: {grade_color};
            color: white;
        }}
        .grid-kpis {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }}
        .kpi-val {{ font-size: 22px; font-weight: 700; color: #0f172a; }}
        .kpi-label {{ font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }}
        .section {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .section-title {{ font-size: 18px; font-weight: 700; margin-bottom: 16px; color: #1e293b; }}
        .dim-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
        .dim-card {{ background: #f8fafc; border: 1px solid var(--border); border-radius: 8px; padding: 14px; }}
        .dim-header {{ display: flex; justify-content: space-between; font-weight: 600; font-size: 14px; margin-bottom: 8px; }}
        .progress-bar-bg {{ background: #e2e8f0; height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 6px; }}
        .progress-bar-fill {{ height: 100%; border-radius: 4px; }}
        .dim-desc {{ font-size: 12px; color: var(--text-muted); }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }}
        th {{ background: #f1f5f9; padding: 10px 12px; border-bottom: 2px solid var(--border); color: #475569; font-weight: 600; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); }}
        tr:hover {{ background-color: #f8fafc; }}
        .tag-type {{ background: #f1f5f9; color: #334155; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-family: monospace; }}
        .badge-clean {{ color: #16a34a; font-weight: 600; font-size: 12px; }}
        .badge-issue {{ color: #dc2626; font-size: 11px; }}
        .rec-item {{ background: #f8fafc; border: 1px solid var(--border); border-radius: 8px; padding: 12px; margin-bottom: 10px; }}
        .rec-header {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
        .priority-badge {{ font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; }}
        .badge-crit {{ background: #fee2e2; color: #b91c1c; }}
        .badge-high {{ background: #ffedd5; color: #c2410c; }}
        .badge-med {{ background: #fef9c3; color: #a16207; }}
        .rec-category {{ font-weight: 600; font-size: 12px; color: #475569; }}
        .rec-msg {{ font-size: 13px; color: #1e293b; }}
        pre {{ background: #1e293b; color: #f8fafc; padding: 8px 12px; border-radius: 6px; font-size: 12px; margin-top: 8px; overflow-x: auto; }}
        .footer {{ text-align: center; font-size: 12px; color: var(--text-muted); margin-top: 32px; }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="header-title">
                <h1>Data Quality & Profiling Report</h1>
                <p>Generated by <strong>Automated Dataset Quality & Profiling Engine</strong> | Target: <code>{metadata.get('filename', 'dataset.csv')}</code></p>
            </div>
            <div class="score-hero">
                <div class="grade-badge">{grade}</div>
                <div>
                    <div class="score-circle">{score:.1f}<span style="font-size: 18px; color: #64748b;"> / 100</span></div>
                    <div style="font-size: 12px; color: #64748b; font-weight: 500;">{desc}</div>
                </div>
            </div>
        </div>

        <!-- KPI Grid -->
        <div class="grid-kpis">
            <div class="kpi-card">
                <div class="kpi-val">{overview.get('total_rows', 0):,}</div>
                <div class="kpi-label">Total Rows</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-val">{overview.get('total_columns', 0):,}</div>
                <div class="kpi-label">Total Columns</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-val">{overview.get('memory_usage_str', '0 KB')}</div>
                <div class="kpi-label">Memory Size</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-val">{overview.get('overall_missing_percentage', 0.0)}%</div>
                <div class="kpi-label">Missing Cells</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-val">{overview.get('duplicate_rows_count', 0):,}</div>
                <div class="kpi-label">Duplicate Rows</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-val">{overview.get('total_outliers_detected', 0):,}</div>
                <div class="kpi-label">Outliers (IQR)</div>
            </div>
        </div>

        <!-- Quality Dimensions -->
        <div class="section">
            <h2 class="section-title">Quality Dimension Breakdown</h2>
            <div class="dim-grid">
                {dims_html}
            </div>
        </div>

        <!-- Remediation Recommendations -->
        <div class="section">
            <h2 class="section-title">Automated Remediation Actions</h2>
            {recs_html}
        </div>

        <!-- Column Health Table -->
        <div class="section" style="overflow-x: auto;">
            <h2 class="section-title">Column Health & Profiling Matrix</h2>
            <table>
                <thead>
                    <tr>
                        <th>Column Name</th>
                        <th>Logical Type</th>
                        <th>Missing Count (%)</th>
                        <th>Distinct</th>
                        <th>Outliers (IQR)</th>
                        <th>Grade</th>
                        <th>Detected Anomalies</th>
                    </tr>
                </thead>
                <tbody>
                    {col_rows_html}
                </tbody>
            </table>
        </div>

        <!-- Footer -->
        <div class="footer">
            Automated Dataset Quality & Profiling Engine • Day 2 — 90 Days 90 Projects Challenge • Built with Python & Pandas
        </div>
    </div>
</body>
</html>
"""
    return html
