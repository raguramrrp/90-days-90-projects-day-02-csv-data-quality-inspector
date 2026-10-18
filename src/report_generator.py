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

    # Build dimensions HTML with signature high-vibrancy colors
    dim_color_map = {
        "completeness": "#A855F7",       # Hyper Neon Violet
        "uniqueness": "#FFD000",         # Radiant Solar Gold
        "validity_consistency": "#00C8FF",# Electric Azure
        "outlier_health": "#FF5533",     # Electric Sunset Coral
        "structural_integrity": "#00F59B",# Acid Cyber Mint
    }
    dims_html = ""
    for dim_key, dim_data in dimensions.items():
        s = dim_data["score"]
        bar_color = dim_color_map.get(dim_key, "#FF5533")
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
        grade_fg = (
            "#00F59B" if c_grade == "A"
            else ("#00C8FF" if c_grade == "B"
            else ("#FFD000" if c_grade == "C"
            else ("#FF5533" if c_grade == "D"
            else "#FF2E93")))
        )
        iqr_info = c_prof.get("outliers_iqr")
        outliers_str = f"{iqr_info['outlier_count']} ({iqr_info['outlier_percentage']}%)" if iqr_info else "—"
        issues_list = c_health.get("issues", [])
        issues_badge = (
            '<span class="badge-clean">NOMINAL (CLEAN)</span>'
            if not issues_list
            else "<br>".join([f'<span class="badge-issue">• {iss}</span>' for iss in issues_list])
        )

        col_rows_html += f"""
        <tr>
            <td style="font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace; font-weight: 600; color: #FFFFFF;">{col_name}</td>
            <td><span class="tag-type">{c_prof.get('logical_type', '')}</span></td>
            <td style="font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace; color: #FF2E93;">{c_prof.get('missing_count', 0)} ({c_prof.get('missing_percentage', 0)}%)</td>
            <td style="font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace; color: #00C8FF;">{c_prof.get('distinct_count', 0):,}</td>
            <td style="font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace; color: #FF5533;">{outliers_str}</td>
            <td><span class="grade-pill" style="border: 1px solid {grade_fg}; background: #151B2E; color: {grade_fg}; font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace; font-weight: 700; font-size: 11px; padding: 3px 8px; border-radius: 4px;">GRADE {c_grade} ({c_health.get('score', 0)}%)</span></td>
            <td>{issues_badge}</td>
        </tr>
        """

    # Build recommendations HTML
    recs_html = ""
    if not recommendations:
        recs_html = '<div class="alert-clean">✓ Zero critical data hygiene anomalies detected. Dataset satisfies nominal quality criteria.</div>'
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

    # Dynamic grade color for hero badge
    hero_grade_color = (
        "#00F59B" if grade == "A"
        else ("#00C8FF" if grade == "B"
        else ("#FFD000" if grade == "C"
        else ("#FF5533" if grade == "D"
        else "#FF2E93")))
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dataset Quality Report // {metadata.get('filename', 'dataset.csv')}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #080A10;
            --surface: #101422;
            --surface-card: #151B2E;
            --border: #202942;
            --border-subtle: #171E33;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --primary: #FF5533;
            --accent-violet: #A855F7;
            --accent-mint: #00F59B;
            --accent-gold: #FFD000;
            --accent-azure: #00C8FF;
            --accent-pink: #FF2E93;
            --font-head: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace;
            --font-body: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace;
            --font-mono: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace;
        }}

        @media (prefers-color-scheme: light) {{
            :root {{
                --bg: #F1F4F9;
                --surface: #FFFFFF;
                --surface-card: #F8FAFC;
                --border: #CBD5E1;
                --border-subtle: #E2E8F0;
                --text-main: #0F172A;
                --text-muted: #64748B;
                --primary: #EA580C;
                --accent-violet: #7C3AED;
                --accent-mint: #059669;
                --accent-gold: #D97706;
                --accent-azure: #0284C7;
                --accent-pink: #E11D48;
            }}
            body {{
                background-color: var(--bg) !important;
                color: var(--text-main) !important;
            }}
            .header {{
                box-shadow: 0 4px 20px rgba(15,23,42,0.06) !important;
            }}
            .header-title h1 {{
                color: #0F172A !important;
            }}
            .score-circle {{
                color: #0F172A !important;
            }}
            .kpi-val {{
                color: #0F172A !important;
            }}
            th {{
                background: #F8FAFC !important;
                color: #475569 !important;
                border-bottom: 1px solid #CBD5E1 !important;
            }}
            td {{
                color: #1E293B !important;
                border-bottom: 1px solid #E2E8F0 !important;
            }}
            tr:hover td {{
                background-color: #F1F5F9 !important;
            }}
            .tag-type {{
                background: #EFF6FF !important;
                border: 1px solid #BFDBFE !important;
                color: #1D4ED8 !important;
            }}
            pre {{
                background: #F8FAFC !important;
                color: #0284C7 !important;
                border: 1px solid #CBD5E1 !important;
            }}
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: var(--font-body);
            background-color: var(--bg);
            color: var(--text-main);
            padding: 40px 24px;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }}
        .container {{
            max-width: 1240px;
            margin: 0 auto;
        }}
        .header {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-top: 4px solid var(--primary);
            border-radius: 8px;
            padding: 24px 28px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.35);
        }}
        .header-title h1 {{
            font-family: var(--font-head);
            font-size: 24px;
            font-weight: 800;
            color: #FFFFFF;
            letter-spacing: -0.4px;
            text-transform: uppercase;
        }}
        .header-title p {{
            color: var(--text-muted);
            font-size: 12px;
            font-family: var(--font-mono);
            margin-top: 6px;
            letter-spacing: 0.8px;
        }}
        .score-hero {{
            display: flex;
            align-items: center;
            gap: 16px;
            background: var(--surface-card);
            padding: 14px 22px;
            border-radius: 6px;
            border: 1px solid var(--border);
            box-shadow: 0 0 16px rgba(255,85,51,0.12);
        }}
        .score-circle {{
            font-size: 38px;
            font-weight: 900;
            font-family: var(--font-head);
            color: #FFFFFF;
            line-height: 1;
        }}
        .grade-badge {{
            font-size: 14px;
            font-weight: 800;
            font-family: var(--font-mono);
            padding: 6px 14px;
            border-radius: 4px;
            border: 1px solid {hero_grade_color};
            background: #101422;
            color: {hero_grade_color};
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        .grid-kpis {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 14px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 16px 18px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.25);
        }}
        .kpi-val {{
            font-size: 24px;
            font-weight: 800;
            font-family: var(--font-head);
            color: #FFFFFF;
        }}
        .kpi-label {{
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 4px;
            font-family: var(--font-mono);
            font-weight: 700;
        }}
        .section {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 26px;
            margin-bottom: 24px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.25);
        }}
        .section-title {{
            font-size: 15px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 18px;
            color: var(--primary);
            font-family: var(--font-head);
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .section-title::before {{
            content: "//";
            color: var(--primary);
        }}
        .dim-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 12px;
        }}
        .dim-card {{
            background: var(--surface-card);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 16px;
        }}
        .dim-header {{
            display: flex;
            justify-content: space-between;
            font-weight: 600;
            font-size: 13px;
            margin-bottom: 10px;
            color: #FFFFFF;
        }}
        .dim-score {{
            font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace;
            font-weight: 700;
            font-size: 13px;
        }}
        .progress-bar-bg {{
            background: #0A0E17;
            height: 6px;
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 8px;
        }}
        .progress-bar-fill {{
            height: 100%;
            border-radius: 3px;
        }}
        .dim-desc {{
            font-size: 11px;
            color: var(--text-muted);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            text-align: left;
        }}
        th {{
            background: #0E1420;
            padding: 10px 14px;
            border-bottom: 1px solid var(--border);
            color: #94A3B8;
            font-weight: 700;
            font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        td {{
            padding: 12px 14px;
            border-bottom: 1px solid var(--border-subtle);
            color: #E2E8F0;
        }}
        tr:hover td {{
            background-color: #182338;
        }}
        .tag-type {{
            background: #151B2E;
            border: 1px solid var(--border);
            color: #FF5533;
            padding: 2px 7px;
            border-radius: 4px;
            font-size: 11px;
            font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace;
            font-weight: 600;
        }}
        .badge-clean {{
            color: #00F59B;
            font-weight: 700;
            font-size: 11px;
            font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace;
        }}
        .badge-issue {{
            color: #FF2E93;
            font-size: 11px;
            font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace;
        }}
        .alert-clean {{
            background: rgba(0, 245, 155, 0.12);
            border: 1px solid #00F59B;
            color: #00F59B;
            padding: 14px 18px;
            border-radius: 6px;
            font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace;
            font-size: 12px;
            font-weight: 600;
        }}
        .rec-item {{
            background: var(--surface-card);
            border: 1px solid var(--border);
            border-left: 4px solid var(--primary);
            border-radius: 6px;
            padding: 14px 18px;
            margin-bottom: 10px;
        }}
        .rec-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .priority-badge {{
            font-size: 10px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 3px;
            text-transform: uppercase;
            font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace;
        }}
        .badge-crit {{
            background: rgba(255, 46, 147, 0.15);
            color: #FF2E93;
            border: 1px solid #FF2E93;
        }}
        .badge-high {{
            background: rgba(255, 208, 0, 0.15);
            color: #FFD000;
            border: 1px solid #FFD000;
        }}
        .badge-med {{
            background: rgba(0, 200, 255, 0.15);
            color: #00C8FF;
            border: 1px solid #00C8FF;
        }}
        .rec-category {{
            font-weight: 700;
            font-size: 11px;
            color: #FF5533;
            font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace;
        }}
        .rec-msg {{
            font-size: 12px;
            color: #E2E8F0;
        }}
        pre {{
            background: #080A10;
            color: #00C8FF;
            padding: 10px 14px;
            border-radius: 4px;
            font-size: 11px;
            font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace;
            margin-top: 10px;
            border: 1px solid var(--border);
            overflow-x: auto;
        }}
        .footer {{
            text-align: center;
            font-size: 11px;
            color: var(--text-muted);
            font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace;
            margin-top: 36px;
            letter-spacing: 0.5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="header-title">
                <h1>Dataset Quality Audit Ledger</h1>
                <p>SPECIFICATION: DIN-ISO 25012 BENCHMARK // TARGET: <code>{metadata.get('filename', 'dataset.csv')}</code></p>
            </div>
            <div class="score-hero">
                <div class="grade-badge">[GRADE {grade}]</div>
                <div>
                    <div class="score-circle">{score:.1f}<span style="font-size: 16px; color: var(--text-muted); font-weight: 400;"> / 100.0</span></div>
                    <div style="font-size: 10px; color: var(--text-muted); font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace; margin-top: 3px; letter-spacing: 0.5px;">STATUS: {desc.upper()}</div>
                </div>
            </div>
        </div>

        <!-- KPI Grid with Vibrant High-Energy Accents -->
        <div class="grid-kpis">
            <div class="kpi-card" style="border-top: 3px solid #00C8FF;">
                <div class="kpi-val" style="color: #00C8FF;">{overview.get('total_rows', 0):,}</div>
                <div class="kpi-label">Total Records</div>
            </div>
            <div class="kpi-card" style="border-top: 3px solid #A855F7;">
                <div class="kpi-val" style="color: #A855F7;">{overview.get('total_columns', 0):,}</div>
                <div class="kpi-label">Features</div>
            </div>
            <div class="kpi-card" style="border-top: 3px solid #FF2E93;">
                <div class="kpi-val" style="color: #FF2E93;">{overview.get('overall_missing_percentage', 0.0)}%</div>
                <div class="kpi-label">Missing Density</div>
            </div>
            <div class="kpi-card" style="border-top: 3px solid #FFD000;">
                <div class="kpi-val" style="color: #FFD000;">{overview.get('duplicate_rows_count', 0):,}</div>
                <div class="kpi-label">Duplicate Rows</div>
            </div>
            <div class="kpi-card" style="border-top: 3px solid #FF5533;">
                <div class="kpi-val" style="color: #FF5533;">{overview.get('total_outliers_detected', 0):,}</div>
                <div class="kpi-label">IQR Outliers</div>
            </div>
            <div class="kpi-card" style="border-top: 3px solid #00F59B;">
                <div class="kpi-val" style="color: #00F59B;">{overview.get('memory_usage_str', '0 KB')}</div>
                <div class="kpi-label">Memory Footprint</div>
            </div>
        </div>

        <!-- Quality Dimensions -->
        <div class="section">
            <h2 class="section-title">Audited Quality Dimensions</h2>
            <div class="dim-grid">
                {dims_html}
            </div>
        </div>

        <!-- Remediation Recommendations -->
        <div class="section">
            <h2 class="section-title">Automated Remediation Register</h2>
            {recs_html}
        </div>

        <!-- Column Health Table -->
        <div class="section" style="overflow-x: auto;">
            <h2 class="section-title">Feature Diagnostic Matrix</h2>
            <table>
                <thead>
                    <tr>
                        <th>Column Identifier</th>
                        <th>Inferred Logical Type</th>
                        <th>Missing Count (%)</th>
                        <th>Distinct Values</th>
                        <th>Outliers (IQR)</th>
                        <th>Integrity Grade</th>
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
            Automated Dataset Quality & Profiling Engine • Day 2 — 90 Days 90 Projects Challenge • Dark Polychrome Metrology Studio
        </div>
    </div>
</body>
</html>
"""
    return html
