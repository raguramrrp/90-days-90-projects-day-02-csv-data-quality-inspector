"""
Streamlit Web Application — Cyber-Observability Studio Theme
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
    page_title="CQI // Dataset Quality Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-Tech Cyber-Observability Studio Styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }

    code, pre, .mono-font {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Sidebar Telemetry Console */
    .sidebar-console {
        background: linear-gradient(145deg, #090d16 0%, #111827 100%);
        border: 1px solid rgba(14, 165, 233, 0.25);
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 22px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .console-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    .console-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        color: #38bdf8;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 10px #10b981;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    .console-title {
        font-size: 18px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    .console-subtitle {
        font-size: 11px;
        color: #64748b;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 2px;
    }

    /* Futuristic HUD Cockpit Hero */
    .hud-hero {
        background: radial-gradient(circle at 10% 20%, #171c2b 0%, #0a0e17 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.08);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 20px;
    }
    .hud-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 700;
        color: #818cf8;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .hud-score-display {
        display: flex;
        align-items: baseline;
        gap: 12px;
    }
    .hud-score-val {
        font-size: 54px;
        font-weight: 900;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -2px;
        color: #ffffff;
    }
    .hud-score-max {
        font-size: 20px;
        color: #64748b;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
    }
    .hud-status-desc {
        font-size: 14px;
        color: #cbd5e1;
        font-weight: 500;
        margin-top: 4px;
    }
    .hud-grade-orb {
        width: 90px;
        height: 90px;
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-family: 'JetBrains Mono', monospace;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    .grade-letter {
        font-size: 42px;
        font-weight: 900;
        line-height: 1;
        color: white;
    }
    .grade-caption {
        font-size: 10px;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.85);
        letter-spacing: 1px;
        margin-top: 2px;
    }

    /* High-Tech Telemetry Metric Pods */
    .pod-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 14px;
        margin-bottom: 24px;
    }
    .pod-card {
        background: #0d121f;
        border: 1px solid #1e2638;
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
        position: relative;
        overflow: hidden;
    }
    .pod-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
    }
    .pod-cyan::before { background: #06b6d4; }
    .pod-indigo::before { background: #6366f1; }
    .pod-rose::before { background: #f43f5e; }
    .pod-amber::before { background: #f59e0b; }
    .pod-purple::before { background: #a855f7; }
    .pod-emerald::before { background: #10b981; }

    .pod-val {
        font-size: 22px;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        color: #f8fafc;
        margin-top: 4px;
    }
    .pod-lbl {
        font-size: 11px;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* Terminal Alert Card */
    .terminal-card {
        background: #090e17;
        border: 1px solid #1e293b;
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
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


# Sidebar: High-Tech Telemetry Brand
st.sidebar.markdown(
    """
    <div class="sidebar-console">
        <div class="console-header">
            <span class="console-tag">OBSERVER // CQI</span>
            <span class="pulse-dot"></span>
        </div>
        <div class="console-title">Quality Inspector</div>
        <div class="console-subtitle">v2.0 • PANDAS ENGINE</div>
    </div>
    """,
    unsafe_allow_html=True,
)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
sample_options = {
    "📁 Upload Your Own CSV": None,
    "⚡ Sample: Dirty E-Commerce (Flawed)": os.path.join(DATA_DIR, "sample_ecommerce_dirty.csv"),
    "👥 Sample: Employee Records (HR Issues)": os.path.join(DATA_DIR, "sample_employee_records.csv"),
    "✨ Sample: Clean Baseline (Gold Standard)": os.path.join(DATA_DIR, "sample_clean_baseline.csv"),
}

dataset_choice = st.sidebar.selectbox(
    "Active Data Source:",
    list(sample_options.keys()),
    index=1 if os.path.exists(sample_options["⚡ Sample: Dirty E-Commerce (Flawed)"]) else 0,
)

# Parsing Config in Sidebar Expander
with st.sidebar.expander("⚙️ Ingestion & Parsing Controls", expanded=False):
    delim_choice = st.selectbox(
        "Delimiter Sniffing:", ["Auto-Detect", ",", ";", "\\t", "|", ":"], index=0
    )
    actual_delim = "\t" if delim_choice == "\\t" else delim_choice
    enc_choice = st.selectbox(
        "Character Encoding:", ["Auto-Detect", "utf-8", "utf-8-sig", "latin-1", "cp1252"], index=0
    )

uploaded_file = None
file_bytes = None
active_filename = "dataset.csv"

if "Upload Your Own CSV" in dataset_choice:
    uploaded_file = st.sidebar.file_uploader(
        "Upload Tabular File:", type=["csv", "txt"], help="Upload any standard CSV file up to 200MB."
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
    "Observation Deck:",
    ["📥 [01] Ingestion Console", "📊 [02] Quality Index HUD", "🔍 [03] Feature Inspector", "📑 [04] Governance & Export"],
    index=0 if "Upload Your Own CSV" in dataset_choice and uploaded_file is None else 1,
)

st.sidebar.markdown("---")
st.sidebar.caption("Day 2 of 90 • 90 Days 90 Projects")
st.sidebar.caption("Architecture: Modular Profiling Engine")

# Main Content Guard
if file_bytes is None:
    st.info("👈 Please select a benchmark dataset or upload a CSV in the sidebar to activate the inspection engine.")
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
# SCREEN 1: INGESTION CONSOLE
# -------------------------------------------------------------
if "[01] Ingestion Console" in screen:
    st.title("📥 Data Stream Ingestion Console")
    st.caption(
        f"Active Dataset: `{active_filename}` • Size: `{meta.get('file_size_bytes', 0):,} bytes` • Latency: `{meta.get('parse_time_ms', 0)} ms`"
    )

    # Ingestion Telemetry Pods
    st.markdown(
        f"""
        <div class="pod-grid">
            <div class="pod-card pod-cyan">
                <div class="pod-lbl">Separator</div>
                <div class="pod-val">'{meta.get('delimiter')}'</div>
            </div>
            <div class="pod-card pod-indigo">
                <div class="pod-lbl">Encoding</div>
                <div class="pod-val">{meta.get('encoding', 'utf-8').upper()}</div>
            </div>
            <div class="pod-card pod-emerald">
                <div class="pod-lbl">Raw Rows</div>
                <div class="pod-val">{len(df):,}</div>
            </div>
            <div class="pod-card pod-purple">
                <div class="pod-lbl">Columns</div>
                <div class="pod-val">{len(df.columns):,}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
        st.success("✅ **Clean Schema Ingestion:** Headers, delimiters, and row structures confirmed valid.")

    # Data Preview
    st.subheader("Raw Data Stream Buffer Preview")
    preview_rows = st.slider("Preview Rows:", min_value=5, max_value=50, value=10)
    st.dataframe(df.head(preview_rows), use_container_width=True)

    with st.expander("🔍 Terminal Metadata Inspection"):
        st.json(meta)
        st.write("Column Schema List:", list(df.columns))


# -------------------------------------------------------------
# SCREEN 2: QUALITY INDEX HUD
# -------------------------------------------------------------
elif "[02] Quality Index HUD" in screen:
    st.title("📊 Cyber Quality Index (CQI) Dashboard")

    score = quality["overall_score"]
    grade = quality["grade"]
    color = quality["grade_color"]
    desc = quality["grade_description"]

    # Futuristic HUD Hero Card
    glow_style = f"background: {color}; box-shadow: 0 0 25px {color}88;"
    st.markdown(
        f"""
        <div class="hud-hero">
            <div>
                <div class="hud-label">CYBERNETIC QUALITY INDEX // CQI-v1</div>
                <div class="hud-score-display">
                    <span class="hud-score-val">{score:.1f}</span>
                    <span class="hud-score-max">/ 100</span>
                </div>
                <div class="hud-status-desc">Evaluation Status: <strong>{desc}</strong></div>
            </div>
            <div class="hud-grade-orb" style="{glow_style}">
                <span class="grade-letter">{grade}</span>
                <span class="grade-caption">GRADE</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Core Telemetry KPI Pods
    overview = profile["overview"]
    st.markdown(
        f"""
        <div class="pod-grid">
            <div class="pod-card pod-cyan">
                <div class="pod-lbl">Total Records</div>
                <div class="pod-val">{overview['total_rows']:,}</div>
            </div>
            <div class="pod-card pod-indigo">
                <div class="pod-lbl">Features</div>
                <div class="pod-val">{overview['total_columns']:,}</div>
            </div>
            <div class="pod-card pod-rose">
                <div class="pod-lbl">Missing Cells</div>
                <div class="pod-val">{overview['overall_missing_percentage']}%</div>
            </div>
            <div class="pod-card pod-amber">
                <div class="pod-lbl">Duplicate Rows</div>
                <div class="pod-val">{overview['duplicate_rows_count']:,} <span style="font-size: 13px; color: #94a3b8;">({overview['duplicate_rows_percentage']}%)</span></div>
            </div>
            <div class="pod-card pod-purple">
                <div class="pod-lbl">IQR Outliers</div>
                <div class="pod-val">{overview['total_outliers_detected']:,}</div>
            </div>
            <div class="pod-card pod-emerald">
                <div class="pod-lbl">Memory Size</div>
                <div class="pod-val">{overview['memory_usage_str']}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Quality Pillars & Missing Matrix
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("🎯 5 Pillars of Dataset Quality")
        dims = quality["dimensions"]
        dim_names = [d["label"] for d in dims.values()]
        dim_scores = [d["score"] for d in dims.values()]

        fig_radar = go.Figure(
            data=go.Scatterpolar(
                r=dim_scores + [dim_scores[0]],
                theta=dim_names + [dim_names[0]],
                fill="toself",
                fillcolor="rgba(6, 182, 212, 0.22)",
                line=dict(color="#06b6d4", width=2.5),
                marker=dict(size=7, color="#38bdf8"),
            )
        )
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(13, 18, 31, 0.8)",
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255, 255, 255, 0.08)"),
                angularaxis=dict(gridcolor="rgba(255, 255, 255, 0.08)"),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=20),
            height=320,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_right:
        st.subheader("⚠️ Sparsity & Missing Density by Feature")
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
            color_continuous_scale=["#10b981", "#f59e0b", "#f43f5e"],
            text="Missing %",
            height=320,
        )
        fig_missing.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13, 18, 31, 0.8)",
            margin=dict(l=20, r=20, t=10, b=20),
            yaxis=dict(autorange="reversed", gridcolor="rgba(255, 255, 255, 0.05)"),
            xaxis=dict(gridcolor="rgba(255, 255, 255, 0.05)"),
            coloraxis_showscale=False,
        )
        fig_missing.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        st.plotly_chart(fig_missing, use_container_width=True)

    # Automated Recommendations
    st.subheader("💡 Automated Remediation Directives")
    recs = quality.get("recommendations", [])
    if not recs:
        st.success("🎉 No critical data hygiene issues detected! The dataset is ready for analytics.")
    else:
        for r in recs:
            p_badge = "🚨 CRITICAL" if r["priority"] == "CRITICAL" else ("⚠️ HIGH" if r["priority"] == "HIGH" else "ℹ️ INFO")
            border_color = "#f43f5e" if r["priority"] == "CRITICAL" else ("#f59e0b" if r["priority"] == "HIGH" else "#06b6d4")
            with st.expander(f"{p_badge} [{r['category']}] {r['message']}"):
                st.markdown(
                    f"""
                    <div class="terminal-card" style="border-left-color: {border_color};">
                        <strong>Category:</strong> {r['category']}<br>
                        <strong>Directive:</strong> {r['message']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if r.get("action"):
                    st.code(r["action"], language="python")


# -------------------------------------------------------------
# SCREEN 3: FEATURE INSPECTOR
# -------------------------------------------------------------
elif "[03] Feature Inspector" in screen:
    st.title("🔍 Analytical Feature Deep-Dive")

    col_names = list(profile["columns"].keys())
    selected_col = st.selectbox("Select Target Feature to Inspect:", col_names)

    c_prof = profile["columns"][selected_col]
    c_health = quality["columns"].get(selected_col, {})

    # Feature Header Pod
    st.markdown(
        f"""
        <div class="pod-grid">
            <div class="pod-card pod-indigo">
                <div class="pod-lbl">Health Grade</div>
                <div class="pod-val">{c_health.get('grade', 'N/A')} <span style="font-size: 14px; color: #94a3b8;">({c_health.get('score', 0)}%)</span></div>
            </div>
            <div class="pod-card pod-cyan">
                <div class="pod-lbl">Logical Type</div>
                <div class="pod-val">{c_prof.get('logical_type', 'Unknown')}</div>
            </div>
            <div class="pod-card pod-rose">
                <div class="pod-lbl">Missingness</div>
                <div class="pod-val">{c_prof.get('missing_count', 0)} <span style="font-size: 13px; color: #94a3b8;">({c_prof.get('missing_percentage', 0)}%)</span></div>
            </div>
            <div class="pod-card pod-purple">
                <div class="pod-lbl">Distinct Count</div>
                <div class="pod-val">{c_prof.get('distinct_count', 0):,}</div>
            </div>
            <div class="pod-card pod-emerald">
                <div class="pod-lbl">Uniqueness Ratio</div>
                <div class="pod-val">{c_prof.get('distinct_ratio', 0):.4f}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
            st.subheader("📊 Distribution Density")
            fig_hist = px.histogram(
                df,
                x=selected_col,
                nbins=30,
                marginal="box",
                title=f"Distribution Profile: {selected_col}",
                color_discrete_sequence=["#06b6d4"],
            )
            fig_hist.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(13, 18, 31, 0.8)",
                margin=dict(l=20, r=20, t=40, b=20),
                height=320,
                xaxis=dict(gridcolor="rgba(255, 255, 255, 0.05)"),
                yaxis=dict(gridcolor="rgba(255, 255, 255, 0.05)"),
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with v2:
            st.subheader("📦 Tukey Outlier & Fence Inspection")
            iqr_data = c_prof.get("outliers_iqr")
            if iqr_data:
                st.markdown(
                    f"**IQR Bounds:** `[{iqr_data['lower_bound']}, {iqr_data['upper_bound']}]` • "
                    f"**Outlier Count:** `{iqr_data['outlier_count']}` ({iqr_data['outlier_percentage']}%)"
                )
                if iqr_data["sample_outliers"]:
                    st.write("Extreme Observations:", iqr_data["sample_outliers"])

            fig_box = px.box(
                df,
                y=selected_col,
                points="outliers",
                title=f"Boxplot: {selected_col}",
                color_discrete_sequence=["#f43f5e"],
            )
            fig_box.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(13, 18, 31, 0.8)",
                margin=dict(l=20, r=20, t=40, b=20),
                height=280,
                yaxis=dict(gridcolor="rgba(255, 255, 255, 0.05)"),
            )
            st.plotly_chart(fig_box, use_container_width=True)

        # Statistics Table
        st.subheader("📐 Parametric & Non-Parametric Metrics")
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
            st.subheader("🔝 High-Frequency Categories")
            top_df = pd.DataFrame(c_stats["top_frequent"])
            if not top_df.empty:
                fig_cat = px.bar(
                    top_df,
                    x="count",
                    y="value",
                    orientation="h",
                    color="count",
                    color_continuous_scale=["#38bdf8", "#0284c7"],
                    text="percentage",
                    title="Top Frequency Counts",
                )
                fig_cat.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(13, 18, 31, 0.8)",
                    yaxis=dict(autorange="reversed", gridcolor="rgba(255, 255, 255, 0.05)"),
                    xaxis=dict(gridcolor="rgba(255, 255, 255, 0.05)"),
                    coloraxis_showscale=False,
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=320,
                )
                fig_cat.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                st.plotly_chart(fig_cat, use_container_width=True)

        with v2:
            st.subheader("🔤 Text Hygiene & Cardinality")
            st.write(f"**Mode Value:** `{c_stats['mode']}` ({c_stats['mode_frequency']} occurrences)")
            st.write(f"**String Length Range:** `{c_stats['min_length']}` min to `{c_stats['max_length']}` max characters")
            st.write(f"**Average String Length:** `{c_stats['avg_length']}` chars")
            st.write(f"**Untrimmed Whitespace Issues:** `{c_stats['whitespace_issues']}` rows")

            if c_stats["whitespace_issues"] > 0:
                st.info("💡 Recommendation: Apply `.str.strip()` to eliminate leading/trailing whitespace.")

    elif c_prof.get("datetime_stats"):
        d_stats = c_prof["datetime_stats"]
        st.subheader("📅 Temporal Horizon")
        st.write(f"**Earliest Timestamp:** `{d_stats['min_date']}`")
        st.write(f"**Latest Timestamp:** `{d_stats['max_date']}`")
        st.write(f"**Temporal Span:** `{d_stats['span_days']}` days")


# -------------------------------------------------------------
# SCREEN 4: GOVERNANCE & EXPORT
# -------------------------------------------------------------
elif "[04] Governance & Export" in screen:
    st.title("📑 Governance Audit & Export Hub")
    st.caption("Generate downloadable audit artifacts or export auto-cleaned datasets.")

    # High-level audit summary table
    st.subheader("📋 Feature Health & Governance Audit Matrix")
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
            "Feature Name": col_name,
            "Inferred Type": c_prof["logical_type"],
            "Health Grade": f"{c_health.get('grade')} ({c_health.get('score')}%)",
            "Missing %": f"{c_prof['missing_percentage']}%",
            "Distinct Count": c_prof["distinct_count"],
            "Outliers (IQR)": outliers_str,
            "Flagged Anomalies": "; ".join(c_health.get("issues", [])) or "Clean (Pristine)",
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
            label="📄 Download JSON Schema",
            data=json_content,
            file_name=f"{active_filename.replace('.csv', '')}_audit.json",
            mime="application/json",
            use_container_width=True,
        )

    # 3. Markdown Summary
    md_content = generate_markdown_report(profile, validation, quality)
    with exp_col3:
        st.download_button(
            label="📝 Download Markdown PR",
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
            label="📊 Download Feature CSV",
            data=csv_buffer.getvalue(),
            file_name=f"{active_filename.replace('.csv', '')}_features_profile.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("---")

    # Automated Cleaning Feature
    st.subheader("🧹 One-Click Auto-Cleaned Dataset Engine")
    st.caption(
        "Automatically purges exact duplicate rows, drops all-null records, and trims whitespace contamination from string fields."
    )

    clean_df = df.copy()
    initial_rows = len(clean_df)

    # 1. Drop all-NaN rows
    clean_df.dropna(how="all", inplace=True)
    # 2. Drop duplicates
    clean_df.drop_duplicates(inplace=True)
    # 3. Strip strings
    for c in clean_df.select_dtypes(include=["object", "string"]).columns:
        clean_df[c] = clean_df[c].astype(str).str.strip()

    removed_rows = initial_rows - len(clean_df)
    st.write(
        f"Auto-Cleaned Buffer: **{len(clean_df):,} rows** ({removed_rows} redundant/empty rows removed)."
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
