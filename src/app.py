"""
Streamlit Web Application
Automated Dataset Quality & Profiling Engine
Day 2 — 90 Days 90 Projects Challenge
"""

import io
import os
import sys

# Ensure project root is in sys.path for robust module resolution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

try:
    from src.parser import parse_csv, detect_encoding, detect_delimiter
    from src.validator import validate_dataset
    from src.profiler import profile_dataset
    from src.quality_engine import calculate_quality_score
    from src.report_generator import (
        generate_html_report,
        generate_json_report,
        generate_markdown_report,
    )
except ImportError:
    from parser import parse_csv, detect_encoding, detect_delimiter
    from validator import validate_dataset
    from profiler import profile_dataset
    from quality_engine import calculate_quality_score
    from report_generator import (
        generate_html_report,
        generate_json_report,
        generate_markdown_report,
    )

# Page configuration
st.set_page_config(
    page_title="Data Quality & Profiling Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for polished dashboard presentation
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-val {
        font-size: 26px;
        font-weight: 800;
        color: #1e293b;
    }
    .metric-lbl {
        font-size: 13px;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .hero-score-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .badge-grade {
        font-size: 36px;
        font-weight: 900;
        padding: 8px 24px;
        border-radius: 12px;
        display: inline-block;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_and_profile_data(
    file_bytes: bytes, filename: str, delimiter: str = None, encoding: str = None
):
    """
    Cached data pipeline: Parsing -> Validation -> Profiling -> Quality Engine.
    """
    df, meta = parse_csv(
        source=file_bytes,
        delimiter=delimiter if delimiter != "Auto-Detect" else None,
        encoding=encoding if encoding != "Auto-Detect" else None,
        filename=filename,
    )
    validation = validate_dataset(df, meta)
    profile = profile_dataset(df, meta)
    quality = calculate_quality_score(profile, validation)
    return df, meta, validation, profile, quality


# Sidebar Navigation & Dataset Controls
st.sidebar.title("🛡️ Dataset Inspector")
st.sidebar.caption("Automated Quality & Profiling Engine")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
sample_options = {
    "Upload Your Own CSV": None,
    "Sample: Dirty E-Commerce (Flawed)": os.path.join(DATA_DIR, "sample_ecommerce_dirty.csv"),
    "Sample: Employee Records (HR Issues)": os.path.join(DATA_DIR, "sample_employee_records.csv"),
    "Sample: Clean Baseline (Gold Standard)": os.path.join(DATA_DIR, "sample_clean_baseline.csv"),
}

dataset_choice = st.sidebar.selectbox(
    "Select Dataset Source:",
    list(sample_options.keys()),
    index=1 if os.path.exists(sample_options["Sample: Dirty E-Commerce (Flawed)"]) else 0,
)

# Parsing Config in Sidebar Expander
with st.sidebar.expander("⚙️ Parsing & Ingestion Settings", expanded=False):
    delim_choice = st.selectbox(
        "Delimiter:", ["Auto-Detect", ",", ";", "\\t", "|", ":"], index=0
    )
    actual_delim = "\t" if delim_choice == "\\t" else delim_choice
    enc_choice = st.selectbox(
        "Encoding:", ["Auto-Detect", "utf-8", "utf-8-sig", "latin-1", "cp1252"], index=0
    )

uploaded_file = None
file_bytes = None
active_filename = "dataset.csv"

if dataset_choice == "Upload Your Own CSV":
    uploaded_file = st.sidebar.file_uploader(
        "Upload a CSV file:", type=["csv", "txt"], help="Upload any standard CSV file."
    )
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        active_filename = uploaded_file.name
else:
    sample_path = sample_options[dataset_choice]
    if os.path.exists(sample_path):
        with open(sample_path, "rb") as f:
            file_bytes = f.read()
        active_filename = os.path.basename(sample_path)
    else:
        st.sidebar.warning("Sample dataset not found on disk. Please upload a file.")

# Navigation Screen Choice
screen = st.sidebar.radio(
    "Navigation Menu:",
    ["📥 1. Upload & Ingestion", "📊 2. Dataset Overview", "🔍 3. Column Deep-Dive", "📑 4. Quality Report & Export"],
    index=0 if dataset_choice == "Upload Your Own CSV" and uploaded_file is None else 1,
)

st.sidebar.markdown("---")
st.sidebar.caption("Day 2 of 90 • 90 Days 90 Projects")
st.sidebar.caption("Domain: Data Engineering & Analytics")


# Main Content Processing
if file_bytes is None:
    st.info("👈 Please upload a CSV file or choose one of the built-in benchmark datasets from the sidebar to begin.")
    st.stop()

# Run Cached Profiling Pipeline
with st.spinner("Processing dataset through quality inspection pipeline..."):
    df, meta, validation, profile, quality = load_and_profile_data(
        file_bytes=file_bytes,
        filename=active_filename,
        delimiter=actual_delim,
        encoding=enc_choice,
    )

if not validation.get("can_profile"):
    st.error("🚨 Fatal Parsing or Structural Error:")
    for err in validation.get("fatal_errors", []):
        st.write(f"- {err}")
    st.stop()


# -------------------------------------------------------------
# SCREEN 1: UPLOAD & INGESTION
# -------------------------------------------------------------
if "1. Upload & Ingestion" in screen:
    st.title("📥 Ingestion & In-Flight Validation")
    st.markdown(
        f"Inspecting file: `**{active_filename}**` ({meta.get('file_size_bytes', 0):,} bytes | {meta.get('parse_time_ms', 0)} ms parsing duration)"
    )

    # Ingestion Badges
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Detected Delimiter", f"'{meta.get('delimiter')}'")
    with c2:
        st.metric("Detected Encoding", meta.get("encoding", "utf-8").upper())
    with c3:
        st.metric("Raw Rows Parsed", f"{len(df):,}")
    with c4:
        st.metric("Columns Ingested", f"{len(df.columns):,}")

    st.markdown("---")

    # Ingestion Validation Alerts
    if validation.get("fatal_errors"):
        for err in validation["fatal_errors"]:
            st.error(f"❌ **Fatal Error:** {err}")
    if validation.get("warnings"):
        for warn in validation["warnings"]:
            st.warning(f"⚠️ **Ingestion Warning:** {warn}")
    if validation.get("info"):
        for inf in validation["info"]:
            st.info(f"ℹ️ **Observation:** {inf}")

    if not validation.get("warnings") and not validation.get("fatal_errors"):
        st.success("✅ **Clean Ingestion:** File schema, headers, and delimiters passed structural checks.")

    # Data Preview
    st.subheader("Raw Data Sample Preview")
    preview_rows = st.slider("Preview Rows:", min_value=5, max_value=50, value=10)
    st.dataframe(df.head(preview_rows), use_container_width=True)

    with st.expander("🔍 View Raw Ingestion Metadata & Headers"):
        st.json(meta)
        st.write("Column Headers:", list(df.columns))


# -------------------------------------------------------------
# SCREEN 2: DATASET OVERVIEW
# -------------------------------------------------------------
elif "2. Dataset Overview" in screen:
    st.title("📊 Dataset Quality Overview")

    score = quality["overall_score"]
    grade = quality["grade"]
    color = quality["grade_color"]
    desc = quality["grade_description"]

    # Quality Hero Banner
    st.markdown(
        f"""
        <div class="hero-score-box">
            <div>
                <h3 style="margin: 0; color: #94a3b8; font-size: 16px; text-transform: uppercase; letter-spacing: 1px;">Overall Quality Assessment</h3>
                <h1 style="margin: 4px 0 0 0; font-size: 42px; font-weight: 800; color: #ffffff;">{score:.1f} <span style="font-size: 20px; color: #94a3b8;">/ 100</span></h1>
                <p style="margin: 4px 0 0 0; color: #cbd5e1; font-size: 15px;">Status: <strong>{desc}</strong></p>
            </div>
            <div>
                <div class="badge-grade" style="background-color: {color}; color: white;">Grade {grade}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Core Dataset KPIs
    overview = profile["overview"]
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Rows", f"{overview['total_rows']:,}")
    k2.metric("Total Columns", f"{overview['total_columns']:,}")
    k3.metric("Missing Cells", f"{overview['overall_missing_percentage']}%")
    k4.metric("Duplicate Rows", f"{overview['duplicate_rows_count']:,} ({overview['duplicate_rows_percentage']}%)")
    k5.metric("Outliers (IQR)", f"{overview['total_outliers_detected']:,}")
    k6.metric("Memory Footprint", overview["memory_usage_str"])

    st.markdown("---")

    # Quality Pillars Visual Breakdown
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("🎯 5 Pillars of Data Quality")
        dims = quality["dimensions"]
        dim_names = [d["label"] for d in dims.values()]
        dim_scores = [d["score"] for d in dims.values()]

        fig_radar = go.Figure(
            data=go.Scatterpolar(
                r=dim_scores + [dim_scores[0]],
                theta=dim_names + [dim_names[0]],
                fill="toself",
                fillcolor="rgba(37, 99, 235, 0.2)",
                line=dict(color="#2563eb", width=2),
                marker=dict(size=6, color="#1e40af"),
            )
        )
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=20),
            height=320,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_right:
        st.subheader("⚠️ Missing Values by Column")
        missing_data = [
            {"Column": c, "Missing %": p["missing_percentage"], "Count": p["missing_count"]}
            for c, p in profile["columns"].items()
        ]
        missing_df = pd.DataFrame(missing_data).sort_values("Missing %", ascending=False)
        fig_missing = px.bar(
            missing_df,
            x="Missing %",
            y="Column",
            orientation="h",
            color="Missing %",
            color_continuous_scale="Reds",
            text="Missing %",
            height=320,
        )
        fig_missing.update_layout(
            margin=dict(l=20, r=20, t=10, b=20),
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False,
        )
        fig_missing.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        st.plotly_chart(fig_missing, use_container_width=True)

    # Automated Recommendations
    st.subheader("💡 Automated Remediation Recommendations")
    recs = quality.get("recommendations", [])
    if not recs:
        st.success("🎉 No critical data hygiene issues detected! The dataset is ready for analytics.")
    else:
        for r in recs:
            p_badge = "🚨 CRITICAL" if r["priority"] == "CRITICAL" else ("⚠️ HIGH" if r["priority"] == "HIGH" else "ℹ️ INFO")
            with st.expander(f"{p_badge} [{r['category']}] {r['message']}"):
                st.write(r["message"])
                if r.get("action"):
                    st.code(r["action"], language="python")


# -------------------------------------------------------------
# SCREEN 3: COLUMN DEEP-DIVE
# -------------------------------------------------------------
elif "3. Column Deep-Dive" in screen:
    st.title("🔍 Column Deep-Dive Profiler")

    col_names = list(profile["columns"].keys())
    selected_col = st.selectbox("Select Column to Inspect:", col_names)

    c_prof = profile["columns"][selected_col]
    c_health = quality["columns"].get(selected_col, {})

    # Header Card for Selected Column
    h1, h2, h3, h4, h5 = st.columns(5)
    h1.metric("Health Grade", f"{c_health.get('grade', 'N/A')} ({c_health.get('score', 0)}%)")
    h2.metric("Inferred Type", c_prof.get("logical_type", "Unknown"))
    h3.metric("Missingness", f"{c_prof.get('missing_count', 0)} ({c_prof.get('missing_percentage', 0)}%)")
    h4.metric("Distinct Values", f"{c_prof.get('distinct_count', 0):,}")
    h5.metric("Uniqueness Ratio", f"{c_prof.get('distinct_ratio', 0):.4f}")

    if c_health.get("issues"):
        for iss in c_health["issues"]:
            st.warning(f"⚠️ {iss}")

    st.markdown("---")

    # Column Visualizations & Metrics based on Type
    series = df[selected_col].dropna()

    if c_prof.get("numeric_stats"):
        n_stats = c_prof["numeric_stats"]
        v1, v2 = st.columns([1, 1])

        with v1:
            st.subheader("📊 Distribution Histogram")
            fig_hist = px.histogram(
                df,
                x=selected_col,
                nbins=30,
                marginal="box",
                title=f"Distribution of {selected_col}",
                color_discrete_sequence=["#2563eb"],
            )
            fig_hist.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=320)
            st.plotly_chart(fig_hist, use_container_width=True)

        with v2:
            st.subheader("📦 Outlier & Boxplot Analysis")
            iqr_data = c_prof.get("outliers_iqr")
            if iqr_data:
                st.write(
                    f"**IQR Bounds:** `[{iqr_data['lower_bound']}, {iqr_data['upper_bound']}]` | "
                    f"**Outlier Count:** `{iqr_data['outlier_count']}` ({iqr_data['outlier_percentage']}%)"
                )
                if iqr_data["sample_outliers"]:
                    st.write("Sample Outliers:", iqr_data["sample_outliers"])

            fig_box = px.box(
                df,
                y=selected_col,
                points="outliers",
                title=f"Tukey Outlier Boxplot: {selected_col}",
                color_discrete_sequence=["#e11d48"],
            )
            fig_box.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=280)
            st.plotly_chart(fig_box, use_container_width=True)

        # Statistics Table
        st.subheader("📐 Parametric & Non-Parametric Statistics")
        s_col1, s_col2, s_col3, s_col4 = st.columns(4)
        s_col1.metric("Mean", f"{n_stats['mean']:,}")
        s_col1.metric("Standard Deviation", f"{n_stats['std']:,}")
        s_col2.metric("Min", f"{n_stats['min']:,}")
        s_col2.metric("Max", f"{n_stats['max']:,}")
        s_col3.metric("Median (Q2)", f"{n_stats['median']:,}")
        s_col3.metric("IQR (Q3 - Q1)", f"{n_stats['iqr']:,}")
        s_col4.metric("Skewness", f"{n_stats['skewness']}")
        s_col4.metric("Zeros Count", f"{n_stats['zeros_count']} ({n_stats['zeros_percentage']}%)")

    elif c_prof.get("categorical_stats"):
        c_stats = c_prof["categorical_stats"]
        v1, v2 = st.columns([1, 1])

        with v1:
            st.subheader("🔝 Top Frequent Categories")
            top_df = pd.DataFrame(c_stats["top_frequent"])
            if not top_df.empty:
                fig_cat = px.bar(
                    top_df,
                    x="count",
                    y="value",
                    orientation="h",
                    color="count",
                    color_continuous_scale="Blues",
                    text="percentage",
                    title="Top Frequency Counts",
                )
                fig_cat.update_layout(
                    yaxis=dict(autorange="reversed"),
                    coloraxis_showscale=False,
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=320,
                )
                fig_cat.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                st.plotly_chart(fig_cat, use_container_width=True)

        with v2:
            st.subheader("🔤 Text Hygiene & Cardinality")
            st.write(f"**Mode (Most Common):** `{c_stats['mode']}` ({c_stats['mode_frequency']} occurrences)")
            st.write(f"**String Length Range:** `{c_stats['min_length']}` min to `{c_stats['max_length']}` max characters")
            st.write(f"**Average String Length:** `{c_stats['avg_length']}` chars")
            st.write(f"**Untrimmed Whitespace Issues:** `{c_stats['whitespace_issues']}` rows")

            if c_stats["whitespace_issues"] > 0:
                st.info("💡 Recommendation: Apply `.str.strip()` to eliminate leading/trailing whitespace.")

    elif c_prof.get("datetime_stats"):
        d_stats = c_prof["datetime_stats"]
        st.subheader("📅 Temporal Span")
        st.write(f"**Earliest Date:** `{d_stats['min_date']}`")
        st.write(f"**Latest Date:** `{d_stats['max_date']}`")
        st.write(f"**Total Span:** `{d_stats['span_days']}` days")


# -------------------------------------------------------------
# SCREEN 4: QUALITY REPORT & EXPORT
# -------------------------------------------------------------
elif "4. Quality Report & Export" in screen:
    st.title("📑 Quality Report & Export Center")
    st.markdown("Generate and download audit reports in multiple formats or export cleaned datasets.")

    # High-level audit summary table
    st.subheader("📋 Comprehensive Column Quality Matrix")
    audit_rows = []
    for col_name, c_prof in profile["columns"].items():
        c_health = quality["columns"].get(col_name, {})
        iqr_info = c_prof.get("outliers_iqr")
        outliers_str = (
            f"{iqr_info['outlier_count']} ({iqr_info['outlier_percentage']}%)"
            if iqr_info
            else "N/A"
        )
        audit_rows.append({
            "Column": col_name,
            "Type": c_prof["logical_type"],
            "Health Grade": f"{c_health.get('grade')} ({c_health.get('score')}%)",
            "Missing %": f"{c_prof['missing_percentage']}%",
            "Distinct Count": c_prof["distinct_count"],
            "Outliers (IQR)": outliers_str,
            "Detected Issues": "; ".join(c_health.get("issues", [])) or "Clean",
        })
    audit_df = pd.DataFrame(audit_rows)
    st.dataframe(audit_df, use_container_width=True)

    st.markdown("---")

    # Download Buttons Center
    st.subheader("📦 Exportable Audit Artifacts")

    exp_col1, exp_col2, exp_col3, exp_col4 = st.columns(4)

    # 1. HTML Report
    html_content = generate_html_report(profile, validation, quality)
    with exp_col1:
        st.download_button(
            label="🌐 Download HTML Report",
            data=html_content,
            file_name=f"{active_filename.replace('.csv', '')}_quality_report.html",
            mime="text/html",
            use_container_width=True,
        )

    # 2. JSON Audit Report
    json_content = generate_json_report(profile, validation, quality)
    with exp_col2:
        st.download_button(
            label="📄 Download JSON Audit",
            data=json_content,
            file_name=f"{active_filename.replace('.csv', '')}_audit.json",
            mime="application/json",
            use_container_width=True,
        )

    # 3. Markdown Summary
    md_content = generate_markdown_report(profile, validation, quality)
    with exp_col3:
        st.download_button(
            label="📝 Download Markdown",
            data=md_content,
            file_name=f"{active_filename.replace('.csv', '')}_summary.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # 4. Column CSV Profile
    csv_buffer = io.StringIO()
    audit_df.to_csv(csv_buffer, index=False)
    with exp_col4:
        st.download_button(
            label="📊 Download Column CSV",
            data=csv_buffer.getvalue(),
            file_name=f"{active_filename.replace('.csv', '')}_columns_profile.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("---")

    # Automated Cleaning Feature
    st.subheader("🧹 One-Click Auto-Cleaned Dataset")
    st.caption(
        "Removes exact duplicate rows, drops all-null rows, and strips leading/trailing whitespace from string columns."
    )

    clean_df = df.copy()
    initial_rows = len(clean_df)

    # 1. Drop all-NaN rows
    clean_df.dropna(how="all", inplace=True)
    # 2. Drop duplicates
    clean_df.drop_duplicates(inplace=True)
    # 3. Strip strings
    for c in clean_df.select_dtypes(include="object").columns:
        clean_df[c] = clean_df[c].astype(str).str.strip()

    removed_rows = initial_rows - len(clean_df)
    st.write(
        f"Cleaned dataset preview: **{len(clean_df):,} rows** ({removed_rows} redundant/empty rows removed)."
    )

    clean_csv_buf = io.StringIO()
    clean_df.to_csv(clean_csv_buf, index=False)
    st.download_button(
        label="📥 Download Auto-Cleaned CSV",
        data=clean_csv_buf.getvalue(),
        file_name=f"{active_filename.replace('.csv', '')}_cleaned.csv",
        mime="text/csv",
        type="primary",
    )
