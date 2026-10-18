"""
Automated Dataset Quality & Profiling Studio
Day 2 — 90 Days 90 Projects Challenge

Visual Architecture: Dual-Theme Metrology Studio
- Dark Studio: Deep Space Obsidian (#080A10, Electric Sunset Coral, Neon Violet, Acid Mint, Solar Gold)
- Swiss Light: Alpine Editorial Porcelain (#F4F6F9, Crisp White Panels #FFFFFF, Tangerine Coral, Royal Amethyst, Cobalt)
Universal Typography: Unified technical metrology monospace stack matching 'DATA METROLOGY STUDIO // ISO-25012 BENCHMARK CORE'
('IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace) across all brand titles, headers, telemetry, tabs, tables, and UI.
"""

import io
import os
import sys
import textwrap

# Ensure project root is in sys.path
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

# Page Configuration - Collapsed sidebar to emphasize top-nav cockpit layout
st.set_page_config(
    page_title="Data Quality Studio // Metrology Lab",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def render_html(html_str: str):
    """
    Safely renders HTML without markdown converting indented lines into code blocks.
    Uses st.html for native DOM injection.
    """
    if hasattr(st, "html"):
        st.html(html_str)
    else:
        cleaned = textwrap.dedent(html_str).strip()
        cleaned = "\n".join(line.strip() for line in cleaned.splitlines())
        st.markdown(cleaned, unsafe_allow_html=True)


# =============================================================
# THEME DETECTION & STATE RESOLUTION (EXECUTED FIRST)
# =============================================================
if "theme" in st.query_params:
    param_theme = st.query_params["theme"].lower()
    if param_theme in ["light", "swiss"]:
        st.session_state.app_theme_mode = "Swiss Light"
    elif param_theme in ["dark", "studio"]:
        st.session_state.app_theme_mode = "Dark Studio"
elif "app_theme_mode" not in st.session_state:
    st.session_state.app_theme_mode = "Dark Studio"

# If user interacted with the theme selector dropdown
if "theme_mode_selector" in st.session_state:
    sel = st.session_state["theme_mode_selector"]
    st.session_state.app_theme_mode = "Swiss Light" if "Swiss Light" in sel else "Dark Studio"

is_light = (st.session_state.app_theme_mode == "Swiss Light")


# =============================================================
# DYNAMIC DESIGN SYSTEM & CSS (UNIFIED IBM PLEX MONO TYPOGRAPHY)
# =============================================================
if is_light:
    # SWISS LIGHT EDITORIAL PORCELAIN PALETTE
    theme_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400;1,600&display=swap');

    /* Global Body and App Canvas - Swiss Light (Unified Technical Monospace) */
    html, body, [data-testid="stAppViewContainer"], .stApp, [data-testid="stMarkdownContainer"], button, input, select, textarea, p, h1, h2, h3, h4, h5, h6, label {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }

    /* Preserve Icon Font Ligatures */
    [data-testid="stIconMaterial"],
    [data-testid^="stIcon"],
    .material-symbols-rounded,
    .material-icons,
    i.material-icons {
        font-family: 'Material Symbols Rounded' !important;
        font-feature-settings: 'liga' 1 !important;
    }

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #F4F6F9 !important;
        color: #0F172A !important;
    }

    [data-testid="stHeader"] {
        background-color: #F4F6F9 !important;
        height: 2.2rem !important;
    }

    .main .block-container {
        max-width: 1380px !important;
        padding-top: 0.8rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* Completely hide Streamlit sidebar and its toggle button */
    [data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Monospace elements */
    code, pre, .mono, [data-testid="stMarkdownContainer"] code {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        background-color: #F8FAFC !important;
        color: #0284C7 !important;
        border: 1px solid #CBD5E1 !important;
        font-size: 13px !important;
    }

    /* Top Studio Brand Bar */
    .top-brand-spec {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 14.5px !important;
        font-weight: 800 !important;
        letter-spacing: 2.5px !important;
        color: #EA580C !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
    }
    .top-brand-title {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #0F172A !important;
        letter-spacing: -0.5px !important;
        line-height: 1.2 !important;
    }
    .theme-switch-label {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 12px !important;
        font-weight: 800 !important;
        color: #64748B !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
        text-align: right !important;
        letter-spacing: 1.2px !important;
    }

    /* Control Shelf & Headers */
    .shelf-header-label {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 14.5px !important;
        font-weight: 800 !important;
        color: #EA580C !important;
        letter-spacing: 2.2px !important;
        text-transform: uppercase !important;
        margin-bottom: 10px !important;
    }
    .shelf-col-header {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 14.5px !important;
        font-weight: 800 !important;
        color: #1E293B !important;
        letter-spacing: 1.8px !important;
        text-transform: uppercase !important;
        margin-bottom: 8px !important;
    }

    /* Horizontal Stage Navigator - Swiss Light */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 12px !important;
        width: 100% !important;
        margin: 6px 0 16px 0 !important;
        align-items: center !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        flex: 1 1 0px !important;
        min-width: 0 !important;
        height: 54px !important;
        min-height: 54px !important;
        max-height: 54px !important;
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-top: 3px solid #94A3B8 !important;
        border-radius: 8px !important;
        padding: 0 16px !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        box-shadow: 0 2px 8px rgba(15,23,42,0.05) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background: #F8FAFC !important;
        border-color: #EA580C !important;
        border-top-color: #EA580C !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(234, 88, 12, 0.15) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label p {
        color: #334155 !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        letter-spacing: 0.6px !important;
        margin: 0 !important;
        transition: color 0.2s ease !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover p {
        color: #EA580C !important;
    }
    /* Active Stage */
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"],
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
        background: #FFF7ED !important;
        border-color: #EA580C !important;
        border-top: 4px solid #EA580C !important;
        box-shadow: 0 4px 16px rgba(234, 88, 12, 0.22) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] p,
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p {
        color: #EA580C !important;
        font-weight: 900 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label div:first-child {
        display: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] input {
        display: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] div[data-testid="stWidgetSelectionLabel"] {
        display: none !important;
    }

    /* Active File Masthead Strip */
    .file-masthead {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 14px 22px !important;
        margin-bottom: 16px !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        flex-wrap: wrap !important;
        gap: 12px !important;
        box-shadow: 0 3px 12px rgba(15,23,42,0.06) !important;
    }
    .file-meta-strip {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 13.5px !important;
    }
    .status-dot {
        width: 10px !important;
        height: 10px !important;
        border-radius: 50% !important;
        display: inline-block !important;
    }

    /* Executive Scorecard Panel */
    .scorecard-panel {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 26px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 20px rgba(15,23,42,0.06) !important;
    }
    .scorecard-grid {
        display: grid !important;
        grid-template-columns: 290px 1fr !important;
        gap: 32px !important;
        align-items: center !important;
    }
    @media (max-width: 900px) {
        .scorecard-grid { grid-template-columns: 1fr !important; }
    }
    .score-hero-box {
        border-right: 1px solid #E2E8F0 !important;
        padding-right: 24px !important;
    }
    @media (max-width: 900px) {
        .score-hero-box { border-right: none !important; border-bottom: 1px solid #E2E8F0 !important; padding-bottom: 20px !important; padding-right: 0 !important; }
    }
    .score-num {
        font-size: 72px !important;
        font-weight: 900 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        color: #0F172A !important;
        line-height: 1 !important;
        letter-spacing: -1.5px !important;
    }
    .score-denom {
        font-size: 20px !important;
        color: #64748B !important;
        font-weight: 700 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }
    .grade-stamp {
        display: inline-block !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-weight: 800 !important;
        font-size: 14.5px !important;
        padding: 7px 18px !important;
        border-radius: 6px !important;
        color: #FFFFFF !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        margin: 10px 0 !important;
    }
    .score-status-desc {
        font-size: 13.5px !important;
        color: #475569 !important;
        line-height: 1.4 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }

    /* 5 Pillars Audit Table */
    .audit-table {
        width: 100% !important;
        border-collapse: collapse !important;
        font-size: 13.5px !important;
    }
    .audit-table th {
        text-align: left !important;
        padding: 10px 14px !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 12.5px !important;
        font-weight: 800 !important;
        color: #475569 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        border-bottom: 2px solid #E2E8F0 !important;
    }
    .audit-table td {
        padding: 11px 14px !important;
        border-bottom: 1px solid #F1F5F9 !important;
        color: #1E293B !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }
    .audit-table tr:hover td {
        background-color: #F8FAFC !important;
    }
    .dim-name {
        font-weight: 700 !important;
        color: #0F172A !important;
        font-size: 14px !important;
    }
    .dim-weight {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        color: #64748B !important;
        font-size: 12.5px !important;
        font-weight: 600 !important;
    }
    .dim-score-num {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-weight: 800 !important;
        font-size: 14.5px !important;
    }
    .meter-track {
        background: #E2E8F0 !important;
        height: 8px !important;
        border-radius: 4px !important;
        overflow: hidden !important;
    }
    .meter-fill {
        height: 100% !important;
        border-radius: 4px !important;
    }

    /* Telemetry Ribbon with Top Color Accents */
    .telemetry-ribbon {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)) !important;
        gap: 14px !important;
        margin-bottom: 20px !important;
    }
    .ribbon-cell {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 16px 18px !important;
        box-shadow: 0 2px 8px rgba(15,23,42,0.05) !important;
    }
    .ribbon-key {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 12px !important;
        font-weight: 800 !important;
        color: #64748B !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        margin-bottom: 4px !important;
    }
    .ribbon-val {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 22px !important;
        font-weight: 800 !important;
        color: #0F172A !important;
    }

    /* Feature Diagnostic Bar */
    .feature-bar {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 16px 22px !important;
        margin-bottom: 16px !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        flex-wrap: wrap !important;
        gap: 14px !important;
        box-shadow: 0 2px 8px rgba(15,23,42,0.05) !important;
    }
    .feature-name-lg {
        font-size: 22px !important;
        font-weight: 800 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        color: #0F172A !important;
    }
    .feature-tag {
        padding: 5px 12px !important;
        border-radius: 4px !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 13px !important;
        font-weight: 700 !important;
    }

    /* Task Card in Remediation */
    .task-card {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-left: 4px solid #EA580C !important;
        border-radius: 6px !important;
        padding: 16px 20px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 8px rgba(15,23,42,0.04) !important;
    }
    .task-meta {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        margin-bottom: 8px !important;
    }
    .task-priority-crit {
        background: #FEE2E2 !important;
        color: #DC2626 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 11.5px !important;
        font-weight: 800 !important;
        padding: 4px 9px !important;
        border-radius: 4px !important;
        border: 1px solid #FCA5A5 !important;
    }
    .task-priority-high {
        background: #FEF3C7 !important;
        color: #D97706 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 11.5px !important;
        font-weight: 800 !important;
        padding: 4px 9px !important;
        border-radius: 4px !important;
        border: 1px solid #FCD34D !important;
    }
    .task-priority-info {
        background: #E0F2FE !important;
        color: #0284C7 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 11.5px !important;
        font-weight: 800 !important;
        padding: 4px 9px !important;
        border-radius: 4px !important;
        border: 1px solid #BAE6FD !important;
    }
    .task-category {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 13.5px !important;
        font-weight: 800 !important;
        color: #EA580C !important;
    }
    .task-msg {
        font-size: 14px !important;
        color: #1E293B !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }

    /* Complete BaseWeb Dropdown Overrides - Swiss Light (NO DARK BOXES) */
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div,
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div[data-baseweb="select"],
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div[data-baseweb="select"] div,
    html body [data-testid="stAppViewContainer"] div[data-baseweb="select"],
    html body [data-testid="stAppViewContainer"] div[data-baseweb="select"] > div,
    html body [data-testid="stAppViewContainer"] div[data-baseweb="select"] div,
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] div {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        color: #0F172A !important;
    }
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div {
        border: 2px solid #CBD5E1 !important;
        border-radius: 8px !important;
        min-height: 48px !important;
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
    }
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
        border-color: #EA580C !important;
        box-shadow: 0 0 0 3px rgba(234, 88, 12, 0.15) !important;
    }
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] span,
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] p,
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] input,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input {
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] svg,
    div[data-baseweb="select"] svg {
        fill: #475569 !important;
        background-color: transparent !important;
        background: transparent !important;
    }
    [data-baseweb="popover"], [data-baseweb="menu"], ul[role="listbox"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.1) !important;
    }
    li[role="option"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }
    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: #FFF7ED !important;
        color: #EA580C !important;
        font-weight: 700 !important;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 2px solid #CBD5E1 !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 6px rgba(15,23,42,0.04) !important;
    }
    [data-testid="stExpander"] summary {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        cursor: pointer !important;
    }
    [data-testid="stExpander"] summary [data-testid="stIconMaterial"],
    [data-testid="stExpander"] summary span[data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded' !important;
    }
    [data-testid="stExpander"] summary:hover {
        color: #EA580C !important;
    }

    /* Sliders */
    [data-testid="stSlider"] [role="slider"] {
        background-color: #EA580C !important;
        border: 2px solid #FFFFFF !important;
    }
    [data-testid="stSlider"] div[data-baseweb="slider"] div {
        background-color: #E2E8F0 !important;
    }
    [data-testid="stSlider"] div[data-baseweb="slider"] div[style*="background-color"] {
        background-color: #EA580C !important;
    }

    /* File Uploader Dropzone */
    [data-testid="stFileUploader"] section {
        background: #FFFFFF !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 22px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #EA580C !important;
        background: #FFF7ED !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 2px solid #CBD5E1 !important;
        transition: all 0.15s ease-in-out !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }
    .stButton > button:hover {
        background-color: #F8FAFC !important;
        border-color: #EA580C !important;
        color: #EA580C !important;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.15) !important;
    }
    .stDownloadButton > button {
        border-radius: 8px !important;
        font-weight: 800 !important;
        font-size: 13.5px !important;
        border: 2px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        transition: all 0.15s ease-in-out !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }
    .stDownloadButton > button:hover {
        background-color: #F8FAFC !important;
        border-color: #EA580C !important;
        color: #EA580C !important;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.15) !important;
    }
    .stDownloadButton > button[kind="primary"] {
        background: linear-gradient(135deg, #EA580C 0%, #C2410C 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 800 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        box-shadow: 0 4px 14px rgba(234, 88, 12, 0.25) !important;
    }
    .stDownloadButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #F97316 0%, #EA580C 100%) !important;
        box-shadow: 0 6px 18px rgba(234, 88, 12, 0.35) !important;
    }

    /* Native Dataframe styling override */
    [data-testid="stDataFrame"] {
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        background: #FFFFFF !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }

    /* Alerts and Notices */
    [data-testid="stAlert"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        color: #0F172A !important;
        border-radius: 8px !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }
    </style>
    """
else:
    # DARK STUDIO SOLAR HORIZON PALETTE
    theme_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400;1,600&display=swap');

    /* Global Body and App Canvas - Dark Studio (Unified Technical Monospace) */
    html, body, [data-testid="stAppViewContainer"], .stApp, [data-testid="stMarkdownContainer"], button, input, select, textarea, p, h1, h2, h3, h4, h5, h6, label {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }

    /* Preserve Icon Font Ligatures */
    [data-testid="stIconMaterial"],
    [data-testid^="stIcon"],
    .material-symbols-rounded,
    .material-icons,
    i.material-icons {
        font-family: 'Material Symbols Rounded' !important;
        font-feature-settings: 'liga' 1 !important;
    }

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #080A10 !important;
        color: #F8FAFC !important;
    }

    [data-testid="stHeader"] {
        background-color: #080A10 !important;
        height: 2.2rem !important;
    }

    .main .block-container {
        max-width: 1380px !important;
        padding-top: 0.8rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* Completely hide Streamlit sidebar and its toggle button */
    [data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Monospace elements */
    code, pre, .mono, [data-testid="stMarkdownContainer"] code {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        background-color: #151B2E !important;
        color: #00C8FF !important;
        border: 1px solid #202942 !important;
        font-size: 13px !important;
    }

    /* Top Studio Brand Bar */
    .top-brand-spec {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 14.5px !important;
        font-weight: 800 !important;
        letter-spacing: 2.5px !important;
        color: #FF5533 !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
    }
    .top-brand-title {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.5px !important;
        line-height: 1.2 !important;
    }
    .theme-switch-label {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 12px !important;
        font-weight: 800 !important;
        color: #94A3B8 !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
        text-align: right !important;
        letter-spacing: 1.2px !important;
    }

    /* Control Shelf & Headers */
    .shelf-header-label {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 14.5px !important;
        font-weight: 800 !important;
        color: #FF5533 !important;
        letter-spacing: 2.2px !important;
        text-transform: uppercase !important;
        margin-bottom: 10px !important;
    }
    .shelf-col-header {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 14.5px !important;
        font-weight: 800 !important;
        color: #E2E8F0 !important;
        letter-spacing: 1.8px !important;
        text-transform: uppercase !important;
        margin-bottom: 8px !important;
    }

    /* Horizontal Stage Navigator - Dark Studio */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 12px !important;
        width: 100% !important;
        margin: 6px 0 16px 0 !important;
        align-items: center !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        flex: 1 1 0px !important;
        min-width: 0 !important;
        height: 54px !important;
        min-height: 54px !important;
        max-height: 54px !important;
        background: #101422 !important;
        border: 1px solid #1C243B !important;
        border-top: 3px solid #232D48 !important;
        border-radius: 8px !important;
        padding: 0 16px !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background: #151B2E !important;
        border-color: #FF5533 !important;
        border-top-color: #FF5533 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(255, 85, 51, 0.2) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label p {
        color: #94A3B8 !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        letter-spacing: 0.6px !important;
        margin: 0 !important;
        transition: color 0.2s ease !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover p {
        color: #FFFFFF !important;
    }
    /* Active Stage */
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"],
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
        background: #161D32 !important;
        border-color: #FF5533 !important;
        border-top: 4px solid #FF5533 !important;
        box-shadow: 0 4px 18px rgba(255, 85, 51, 0.28) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] p,
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p {
        color: #FF5533 !important;
        font-weight: 900 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label div:first-child {
        display: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] input {
        display: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] div[data-testid="stWidgetSelectionLabel"] {
        display: none !important;
    }

    /* Active File Masthead Strip */
    .file-masthead {
        background: #101422 !important;
        border: 1px solid #202942 !important;
        border-radius: 8px !important;
        padding: 14px 22px !important;
        margin-bottom: 16px !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        flex-wrap: wrap !important;
        gap: 12px !important;
        box-shadow: 0 3px 12px rgba(0,0,0,0.2) !important;
    }
    .file-meta-strip {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 13.5px !important;
    }
    .status-dot {
        width: 10px !important;
        height: 10px !important;
        border-radius: 50% !important;
        display: inline-block !important;
    }

    /* Executive Scorecard Panel */
    .scorecard-panel {
        background: #101422 !important;
        border: 1px solid #202942 !important;
        border-radius: 8px !important;
        padding: 26px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 18px rgba(0,0,0,0.3) !important;
    }
    .scorecard-grid {
        display: grid !important;
        grid-template-columns: 290px 1fr !important;
        gap: 32px !important;
        align-items: center !important;
    }
    @media (max-width: 900px) {
        .scorecard-grid { grid-template-columns: 1fr !important; }
    }
    .score-hero-box {
        border-right: 1px solid #202942 !important;
        padding-right: 24px !important;
    }
    @media (max-width: 900px) {
        .score-hero-box { border-right: none !important; border-bottom: 1px solid #202942 !important; padding-bottom: 20px !important; padding-right: 0 !important; }
    }
    .score-num {
        font-size: 72px !important;
        font-weight: 900 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        color: #FFFFFF !important;
        line-height: 1 !important;
        letter-spacing: -1.5px !important;
    }
    .score-denom {
        font-size: 20px !important;
        color: #94A3B8 !important;
        font-weight: 700 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }
    .grade-stamp {
        display: inline-block !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-weight: 800 !important;
        font-size: 14.5px !important;
        padding: 7px 18px !important;
        border-radius: 6px !important;
        color: #FFFFFF !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        margin: 10px 0 !important;
    }
    .score-status-desc {
        font-size: 13.5px !important;
        color: #94A3B8 !important;
        line-height: 1.4 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }

    /* 5 Pillars Audit Table */
    .audit-table {
        width: 100% !important;
        border-collapse: collapse !important;
        font-size: 13.5px !important;
    }
    .audit-table th {
        text-align: left !important;
        padding: 10px 14px !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 12.5px !important;
        font-weight: 800 !important;
        color: #94A3B8 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        border-bottom: 2px solid #202942 !important;
    }
    .audit-table td {
        padding: 11px 14px !important;
        border-bottom: 1px solid #161D30 !important;
        color: #E2E8F0 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }
    .audit-table tr:hover td {
        background-color: #151B2E !important;
    }
    .dim-name {
        font-weight: 700 !important;
        color: #F8FAFC !important;
        font-size: 14px !important;
    }
    .dim-weight {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        color: #94A3B8 !important;
        font-size: 12.5px !important;
        font-weight: 600 !important;
    }
    .dim-score-num {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-weight: 800 !important;
        font-size: 14.5px !important;
    }
    .meter-track {
        background: #080A10 !important;
        height: 8px !important;
        border-radius: 4px !important;
        overflow: hidden !important;
    }
    .meter-fill {
        height: 100% !important;
        border-radius: 4px !important;
    }

    /* Telemetry Ribbon with Top Color Accents */
    .telemetry-ribbon {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)) !important;
        gap: 14px !important;
        margin-bottom: 20px !important;
    }
    .ribbon-cell {
        background: #101422 !important;
        border: 1px solid #202942 !important;
        border-radius: 8px !important;
        padding: 16px 18px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25) !important;
    }
    .ribbon-key {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 12px !important;
        font-weight: 800 !important;
        color: #94A3B8 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        margin-bottom: 4px !important;
    }
    .ribbon-val {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 22px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
    }

    /* Feature Diagnostic Bar */
    .feature-bar {
        background: #101422 !important;
        border: 1px solid #202942 !important;
        border-radius: 8px !important;
        padding: 16px 22px !important;
        margin-bottom: 16px !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        flex-wrap: wrap !important;
        gap: 14px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25) !important;
    }
    .feature-name-lg {
        font-size: 22px !important;
        font-weight: 800 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        color: #FFFFFF !important;
    }
    .feature-tag {
        padding: 5px 12px !important;
        border-radius: 4px !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 13px !important;
        font-weight: 700 !important;
    }

    /* Task Card in Remediation */
    .task-card {
        background: #101422 !important;
        border: 1px solid #202942 !important;
        border-left: 4px solid #FF5533 !important;
        border-radius: 6px !important;
        padding: 16px 20px !important;
        margin-bottom: 12px !important;
    }
    .task-meta {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        margin-bottom: 8px !important;
    }
    .task-priority-crit {
        background: rgba(255, 46, 147, 0.15) !important;
        color: #FF2E93 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 11.5px !important;
        font-weight: 800 !important;
        padding: 4px 9px !important;
        border-radius: 4px !important;
        border: 1px solid #FF2E93 !important;
    }
    .task-priority-high {
        background: rgba(255, 208, 0, 0.15) !important;
        color: #FFD000 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 11.5px !important;
        font-weight: 800 !important;
        padding: 4px 9px !important;
        border-radius: 4px !important;
        border: 1px solid #FFD000 !important;
    }
    .task-priority-info {
        background: rgba(0, 200, 255, 0.15) !important;
        color: #00C8FF !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 11.5px !important;
        font-weight: 800 !important;
        padding: 4px 9px !important;
        border-radius: 4px !important;
        border: 1px solid #00C8FF !important;
    }
    .task-category {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 13.5px !important;
        font-weight: 800 !important;
        color: #FF5533 !important;
    }
    .task-msg {
        font-size: 14px !important;
        color: #E2E8F0 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }

    /* Complete BaseWeb Dropdown Overrides - Dark Studio */
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div,
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div[data-baseweb="select"],
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div[data-baseweb="select"] div,
    html body [data-testid="stAppViewContainer"] div[data-baseweb="select"],
    html body [data-testid="stAppViewContainer"] div[data-baseweb="select"] > div,
    html body [data-testid="stAppViewContainer"] div[data-baseweb="select"] div,
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] div {
        background-color: #101422 !important;
        background: #101422 !important;
        color: #F8FAFC !important;
    }
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div {
        border: 2px solid #202942 !important;
        border-radius: 8px !important;
        min-height: 48px !important;
        background-color: #101422 !important;
        background: #101422 !important;
    }
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
        border-color: #FF5533 !important;
        box-shadow: 0 0 0 3px rgba(255, 85, 51, 0.2) !important;
    }
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] span,
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] p,
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] input,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input {
        color: #F8FAFC !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }
    html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] svg,
    div[data-baseweb="select"] svg {
        fill: #94A3B8 !important;
        background-color: transparent !important;
        background: transparent !important;
    }
    [data-baseweb="popover"], [data-baseweb="menu"], ul[role="listbox"] {
        background-color: #101422 !important;
        border: 1px solid #202942 !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5) !important;
    }
    li[role="option"] {
        background-color: #101422 !important;
        color: #F8FAFC !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }
    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: #161D32 !important;
        color: #FF5533 !important;
        font-weight: 700 !important;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background: #101422 !important;
        border: 2px solid #202942 !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
    }
    [data-testid="stExpander"] summary {
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        cursor: pointer !important;
    }
    [data-testid="stExpander"] summary [data-testid="stIconMaterial"],
    [data-testid="stExpander"] summary span[data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded' !important;
    }
    [data-testid="stExpander"] summary:hover {
        color: #FF5533 !important;
    }

    /* Sliders */
    [data-testid="stSlider"] [role="slider"] {
        background-color: #FF5533 !important;
        border: 2px solid #FFFFFF !important;
    }
    [data-testid="stSlider"] div[data-baseweb="slider"] div {
        background-color: #202942 !important;
    }
    [data-testid="stSlider"] div[data-baseweb="slider"] div[style*="background-color"] {
        background-color: #FF5533 !important;
    }

    /* File Uploader Dropzone */
    [data-testid="stFileUploader"] section {
        background: #101422 !important;
        border: 2px dashed #2E3854 !important;
        border-radius: 8px !important;
        padding: 22px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #FF5533 !important;
        background: #151B2E !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        background-color: #151B2E !important;
        color: #F8FAFC !important;
        border: 2px solid #2B3552 !important;
        transition: all 0.15s ease-in-out !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }
    .stButton > button:hover {
        background-color: #1C243C !important;
        border-color: #FF5533 !important;
        color: #FF5533 !important;
        box-shadow: 0 4px 12px rgba(255, 85, 51, 0.2) !important;
    }
    .stDownloadButton > button {
        border-radius: 8px !important;
        font-weight: 800 !important;
        font-size: 13.5px !important;
        border: 2px solid #2B3552 !important;
        background-color: #151B2E !important;
        color: #F8FAFC !important;
        transition: all 0.15s ease-in-out !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }
    .stDownloadButton > button:hover {
        background-color: #1C243C !important;
        border-color: #FF5533 !important;
        color: #FF5533 !important;
        box-shadow: 0 4px 12px rgba(255, 85, 51, 0.2) !important;
    }
    .stDownloadButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF5533 0%, #D83B1A 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 800 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
        box-shadow: 0 4px 14px rgba(255, 85, 51, 0.3) !important;
    }
    .stDownloadButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #FF6B4A 0%, #E64522 100%) !important;
        box-shadow: 0 6px 18px rgba(255, 85, 51, 0.45) !important;
    }

    /* Native Dataframe styling override */
    [data-testid="stDataFrame"] {
        border: 1px solid #202942 !important;
        border-radius: 8px !important;
        background: #101422 !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }

    /* Alerts and Notices */
    [data-testid="stAlert"] {
        background-color: #101422 !important;
        border: 1px solid #202942 !important;
        color: #F8FAFC !important;
        border-radius: 8px !important;
        font-family: 'IBM Plex Mono', 'Cascadia Code', 'Consolas', monospace !important;
    }
    </style>
    """

# Inject full CSS rules before ANY widget or HTML is rendered
render_html(theme_css)


# =============================================================
# TOP BRAND BAR & THEME TOGGLE
# =============================================================
col_brand_head, col_theme_toggle = st.columns([4, 1])

with col_brand_head:
    render_html(
        """
        <div style="margin-bottom: 6px;">
            <div class="top-brand-spec">DATA METROLOGY STUDIO // ISO-25012 BENCHMARK CORE</div>
            <div class="top-brand-title">Automated Dataset Quality & Profiling Engine</div>
        </div>
        """
    )

with col_theme_toggle:
    render_html("<div class='theme-switch-label'>INTERFACE THEME</div>")
    selected_theme = st.selectbox(
        "Interface Theme",
        ["🌙 Dark Studio", "☀️ Swiss Light"],
        index=0 if st.session_state.app_theme_mode == "Dark Studio" else 1,
        label_visibility="collapsed",
        key="theme_mode_selector",
    )


# =============================================================
# TOP TELEMETRY SPECIFICATIONS BAR
# =============================================================
if is_light:
    pill_py = "background: #ECFDF5; border: 1px solid #A7F3D0; color: #059669;"
    pill_pd = "background: #EFF6FF; border: 1px solid #BFDBFE; color: #0284C7;"
    pill_dim = "background: #F5F3FF; border: 1px solid #DDD6FE; color: #7C3AED;"
    pill_tuk = "background: #FFFBEB; border: 1px solid #FDE68A; color: #D97706;"
    spec_box = "background: #FFFFFF; border: 1px solid #CBD5E1; box-shadow: 0 4px 12px rgba(15,23,42,0.05);"
    spec_txt = "color: #64748B;"
else:
    pill_py = "background: rgba(0, 245, 155, 0.12); border: 1px solid #00F59B; color: #00F59B;"
    pill_pd = "background: rgba(0, 200, 255, 0.12); border: 1px solid #00C8FF; color: #00C8FF;"
    pill_dim = "background: rgba(168, 85, 247, 0.12); border: 1px solid #A855F7; color: #A855F7;"
    pill_tuk = "background: rgba(255, 208, 0, 0.12); border: 1px solid #FFD000; color: #FFD000;"
    spec_box = "background: #0B0E17; border: 1px solid #1C243B;"
    spec_txt = "color: #94A3B8;"

render_html(
    f"""
    <div style="{spec_box} border-radius: 8px; padding: 10px 18px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; font-family: 'IBM Plex Mono', 'Cascadia Code', monospace;">
        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font-size: 13.5px; font-weight: 800;">
            <span style="{pill_py} padding: 6px 14px; border-radius: 6px;">⚡ PYTHON 3.12</span>
            <span style="{pill_pd} padding: 6px 14px; border-radius: 6px;">📊 PANDAS 3.0</span>
            <span style="{pill_dim} padding: 6px 14px; border-radius: 6px;">🔬 5-PILLAR WEIGHTED</span>
            <span style="{pill_tuk} padding: 6px 14px; border-radius: 6px;">🎯 TUKEY IQR & Z-SCORE</span>
        </div>
        <div style="font-size: 12px; font-weight: 700; {spec_txt}">
            SPEC: DIN-ISO 25012 COMPLIANT
        </div>
    </div>
    """
)


# =============================================================
# TOP FEED CONTROL SHELF (COCKPIT CONFIGURATION)
# =============================================================
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
sample_options = {
    "Benchmark: Dirty E-Commerce": os.path.join(DATA_DIR, "sample_ecommerce_dirty.csv"),
    "Benchmark: Employee Records": os.path.join(DATA_DIR, "sample_employee_records.csv"),
    "Benchmark: Clean Baseline": os.path.join(DATA_DIR, "sample_clean_baseline.csv"),
    "Custom Upload (.csv)": None,
}

render_html("<div class='shelf-header-label'>CONTROL CONSOLE // DATA FEED & PARSER CONFIGURATION</div>")

col_feed_sel, col_feed_param = st.columns([3, 2])

with col_feed_sel:
    render_html("<div class='shelf-col-header'>ACTIVE DATA FEED SOURCE</div>")
    dataset_choice = st.selectbox(
        "Active Data Feed Selection",
        list(sample_options.keys()),
        index=0,
        label_visibility="collapsed",
        help="Select a standard benchmark test suite or upload custom CSV.",
    )

with col_feed_param:
    render_html("<div class='shelf-col-header'>PARSER OVERRIDES</div>")
    with st.expander("Delimiter & Encoding Settings", expanded=False):
        c_del, c_enc = st.columns(2)
        with c_del:
            delim_choice = st.selectbox(
                "Delimiter", ["Auto-Detect", ",", ";", "\\t", "|", ":"], index=0
            )
            actual_delim = "\t" if delim_choice == "\\t" else delim_choice
        with c_enc:
            enc_choice = st.selectbox(
                "Encoding", ["Auto-Detect", "utf-8", "utf-8-sig", "latin-1", "cp1252"], index=0
            )

uploaded_file = None
file_bytes = None
active_filename = "dataset.csv"

if dataset_choice == "Custom Upload (.csv)":
    uploaded_file = st.file_uploader(
        "Upload Custom CSV Dataset",
        type=["csv", "txt"],
        help="Upload any delimited tabular data up to 200MB.",
    )
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        active_filename = uploaded_file.name
else:
    sample_path = sample_options[dataset_choice]
    if sample_path and os.path.exists(sample_path):
        with open(sample_path, "rb") as f:
            file_bytes = f.read()
        active_filename = os.path.basename(sample_path)
    else:
        st.warning("Sample dataset not found on disk.")

# Stop if no data is loaded
if file_bytes is None:
    st.info("Select a benchmark dataset above or upload a CSV file to execute the quality inspection.")
    st.stop()


# =============================================================
# CACHED DATA PIPELINE EXECUTION
# =============================================================
@st.cache_data(show_spinner=False)
def load_and_profile_data(
    file_bytes_input: bytes, filename: str, delimiter: str = None, encoding: str = None
):
    df_res, meta_res = parse_csv(
        source=file_bytes_input,
        delimiter=delimiter if delimiter != "Auto-Detect" else None,
        encoding=encoding if encoding != "Auto-Detect" else None,
        filename=filename,
    )
    validation_res = validate_dataset(df_res, meta_res)
    profile_res = profile_dataset(df_res, meta_res)
    quality_res = calculate_quality_score(profile_res, validation_res)
    return df_res, meta_res, validation_res, profile_res, quality_res


with st.spinner("Executing statistical profiling and quality audit..."):
    df, meta, validation, profile, quality = load_and_profile_data(
        file_bytes_input=file_bytes,
        filename=active_filename,
        delimiter=actual_delim,
        encoding=enc_choice,
    )

if not validation.get("can_profile"):
    st.error("🚨 Ingestion Failure:")
    for err in validation.get("fatal_errors", []):
        st.write(f"- {err}")
    st.stop()


# Dynamic Grade Color Mapping for Vibrant Palette
grade = quality["grade"]
score = quality["overall_score"]
desc = quality["grade_description"]

if is_light:
    vibrant_grade_color = (
        "#059669" if grade == "A"
        else ("#0284C7" if grade == "B"
        else ("#D97706" if grade == "C"
        else ("#EA580C" if grade == "D"
        else "#DC2626")))
    )
    grade_pill_bg = "#FFF7ED" if grade == "D" else ("#F0FDF4" if grade == "A" else "#F8FAFC")
else:
    vibrant_grade_color = (
        "#00F59B" if grade == "A"
        else ("#00C8FF" if grade == "B"
        else ("#FFD000" if grade == "C"
        else ("#FF5533" if grade == "D"
        else "#FF2E93")))
    )
    grade_pill_bg = "#151B2E"

# Active File & Quality Grade Pill Strip
render_html(
    f"""
    <div class="file-masthead">
        <div class="file-meta-strip">
            <span class="status-dot" style="background-color: {vibrant_grade_color};"></span>
            <span style="color: {'#64748B' if is_light else '#94A3B8'}; font-weight: 700;">ACTIVE DATASET:</span>
            <span style="color: {'#0F172A' if is_light else '#FFFFFF'}; font-weight: 800;">{active_filename}</span>
            <span style="color: {'#CBD5E1' if is_light else '#202942'};">|</span>
            <span style="color: {'#64748B' if is_light else '#94A3B8'}; font-weight: 700;">OBSERVATIONS:</span>
            <span style="color: {'#0284C7' if is_light else '#00C8FF'}; font-weight: 800;">{len(df):,} rows × {len(df.columns)} cols</span>
        </div>
        <div style="font-family: 'IBM Plex Mono', 'Cascadia Code', monospace; font-size: 13.5px;">
            <span style="border: 2px solid {vibrant_grade_color}; background: {grade_pill_bg}; color: {vibrant_grade_color}; padding: 5px 14px; border-radius: 6px; font-weight: 800; letter-spacing: 0.5px;">
                GRADE {grade} ({score:.1f}%) — {desc.upper()}
            </span>
        </div>
    </div>
    """
)


# =============================================================
# HORIZONTAL WORKBENCH STAGE NAVIGATOR
# =============================================================
stage_options = [
    "01 · Ingestion & Schema",
    "02 · Quality Scorecard",
    "03 · Feature Diagnostics",
    "04 · Governance & Exports",
]

selected_stage = st.radio(
    "Workbench Stage Navigation",
    stage_options,
    index=1,
    horizontal=True,
    key="workbench_nav_stage",
    label_visibility="collapsed",
)


# =============================================================
# STAGE 01: INGESTION & SCHEMA
# =============================================================
if selected_stage == "01 · Ingestion & Schema":
    c_sep = "#0284C7" if is_light else "#00C8FF"
    c_enc = "#7C3AED" if is_light else "#A855F7"
    c_size = "#DC2626" if is_light else "#FF2E93"
    c_lat = "#D97706" if is_light else "#FFD000"
    c_rows = "#EA580C" if is_light else "#FF5533"
    c_feat = "#059669" if is_light else "#00F59B"

    render_html(
        f"""
        <div class="telemetry-ribbon">
            <div class="ribbon-cell" style="border-top: 4px solid {c_sep};">
                <div class="ribbon-key">Separator</div>
                <div class="ribbon-val" style="color: {c_sep};">'{meta.get('delimiter')}'</div>
            </div>
            <div class="ribbon-cell" style="border-top: 4px solid {c_enc};">
                <div class="ribbon-key">Encoding</div>
                <div class="ribbon-val" style="color: {c_enc};">{meta.get('encoding', 'utf-8').upper()}</div>
            </div>
            <div class="ribbon-cell" style="border-top: 4px solid {c_size};">
                <div class="ribbon-key">File Size</div>
                <div class="ribbon-val" style="color: {c_size};">{meta.get('file_size_bytes', 0):,} B</div>
            </div>
            <div class="ribbon-cell" style="border-top: 4px solid {c_lat};">
                <div class="ribbon-key">Parse Latency</div>
                <div class="ribbon-val" style="color: {c_lat};">{meta.get('parse_time_ms', 0)} ms</div>
            </div>
            <div class="ribbon-cell" style="border-top: 4px solid {c_rows};">
                <div class="ribbon-key">Raw Rows</div>
                <div class="ribbon-val" style="color: {c_rows};">{len(df):,}</div>
            </div>
            <div class="ribbon-cell" style="border-top: 4px solid {c_feat};">
                <div class="ribbon-key">Features</div>
                <div class="ribbon-val" style="color: {c_feat};">{len(df.columns):,}</div>
            </div>
        </div>
        """
    )

    if validation.get("fatal_errors"):
        for err in validation["fatal_errors"]:
            st.error(f"Fatal Schema Defect: {err}")
    if validation.get("warnings"):
        for warn in validation["warnings"]:
            st.warning(f"Ingestion Notice: {warn}")
    if validation.get("info"):
        for inf in validation["info"]:
            st.info(f"Schema Observation: {inf}")
    if not validation.get("warnings") and not validation.get("fatal_errors"):
        st.success("Ingestion Verification Passed: Header structure, delimiters, and row alignments conform to standards.")

    render_html("<div style='height: 8px;'></div>")
    c_left, c_right = st.columns([1, 1])
    with c_left:
        st.markdown("**Sample Data Stream Buffer**")
    with c_right:
        preview_rows = st.slider(
            "Preview Rows",
            min_value=min(5, len(df)),
            max_value=min(50, len(df)),
            value=min(10, len(df)),
            label_visibility="collapsed",
        )

    st.dataframe(df.head(preview_rows), use_container_width=True)

    with st.expander("Technical Ingestion Metadata & Raw Header Registry"):
        st.json(meta)
        st.write("Column Index Listing:", {i: col for i, col in enumerate(df.columns)})


# =============================================================
# STAGE 02: QUALITY SCORECARD
# =============================================================
elif selected_stage == "02 · Quality Scorecard":
    overview = profile["overview"]
    dims = quality["dimensions"]

    if is_light:
        dim_color_map = {
            "completeness": "#7C3AED",       # Royal Amethyst
            "uniqueness": "#D97706",         # Warm Amber
            "validity_consistency": "#0284C7",# Electric Cobalt
            "outlier_health": "#EA580C",     # Tangerine Coral
            "structural_integrity": "#059669"# Vivid Emerald
        }
    else:
        dim_color_map = {
            "completeness": "#A855F7",       # Hyper Neon Violet
            "uniqueness": "#FFD000",         # Radiant Solar Gold
            "validity_consistency": "#00C8FF",# Electric Azure
            "outlier_health": "#FF5533",     # Electric Sunset Coral
            "structural_integrity": "#00F59B"# Acid Cyber Mint
        }

    dim_rows_html = ""
    for dim_key, dim_data in dims.items():
        s = dim_data["score"]
        bar_color = dim_color_map.get(dim_key, "#EA580C" if is_light else "#FF5533")
        dim_rows_html += (
            f"<tr>"
            f"<td class='dim-name'>{dim_data['label']}</td>"
            f"<td class='dim-weight'>{int(dim_data['weight']*100)}%</td>"
            f"<td class='dim-score-num' style='color: {bar_color};'>{s:.1f}</td>"
            f"<td style='width: 140px;'><div class='meter-track'><div class='meter-fill' style='width: {s}%; background-color: {bar_color};'></div></div></td>"
            f"<td style='color: {'#64748B' if is_light else '#94A3B8'}; font-size: 13px;'>{dim_data['description']}</td>"
            f"</tr>"
        )

    grade_bg = vibrant_grade_color
    render_html(
        f"""
        <div class="scorecard-panel">
            <div class="scorecard-grid">
                <div class="score-hero-box">
                    <div style="font-family: 'IBM Plex Mono', 'Cascadia Code', monospace; font-size: 12px; font-weight: 800; color: {'#64748B' if is_light else '#94A3B8'}; letter-spacing: 1.8px; text-transform: uppercase;">DATA QUALITY INDEX</div>
                    <div style="display: flex; align-items: baseline; gap: 6px; margin-top: 4px;">
                        <span class="score-num">{score:.1f}</span>
                        <span class="score-denom">/ 100</span>
                    </div>
                    <div>
                        <span class="grade-stamp" style="background-color: {grade_bg};">GRADE {grade}</span>
                    </div>
                    <div class="score-status-desc">
                        <strong>Evaluation:</strong> {desc}
                    </div>
                </div>
                <div>
                    <div style="font-family: 'IBM Plex Mono', 'Cascadia Code', monospace; font-size: 13.5px; font-weight: 800; color: {'#EA580C' if is_light else '#FF5533'}; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px;">5 PILLARS AUDIT LEDGER</div>
                    <table class="audit-table">
                        <thead>
                            <tr>
                                <th>Dimension</th>
                                <th>Weight</th>
                                <th>Score</th>
                                <th>Fulfillment</th>
                                <th>Audit Scope</th>
                            </tr>
                        </thead>
                        <tbody>
                            {dim_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """
    )

    c_kpi1 = "#0284C7" if is_light else "#00C8FF"
    c_kpi2 = "#7C3AED" if is_light else "#A855F7"
    c_kpi3 = "#DC2626" if is_light else "#FF2E93"
    c_kpi4 = "#D97706" if is_light else "#FFD000"
    c_kpi5 = "#EA580C" if is_light else "#FF5533"
    c_kpi6 = "#059669" if is_light else "#00F59B"

    render_html(
        f"""
        <div class="telemetry-ribbon">
            <div class="ribbon-cell" style="border-top: 4px solid {c_kpi1};">
                <div class="ribbon-key">Total Records</div>
                <div class="ribbon-val" style="color: {c_kpi1};">{overview['total_rows']:,}</div>
            </div>
            <div class="ribbon-cell" style="border-top: 4px solid {c_kpi2};">
                <div class="ribbon-key">Features</div>
                <div class="ribbon-val" style="color: {c_kpi2};">{overview['total_columns']:,}</div>
            </div>
            <div class="ribbon-cell" style="border-top: 4px solid {c_kpi3};">
                <div class="ribbon-key">Missing Cells</div>
                <div class="ribbon-val" style="color: {c_kpi3};">{overview['overall_missing_percentage']}%</div>
            </div>
            <div class="ribbon-cell" style="border-top: 4px solid {c_kpi4};">
                <div class="ribbon-key">Duplicate Rows</div>
                <div class="ribbon-val" style="color: {c_kpi4};">{overview['duplicate_rows_count']:,} <span style="font-size: 12px; color: {'#64748B' if is_light else '#94A3B8'}; font-weight: 500;">({overview['duplicate_rows_percentage']}%)</span></div>
            </div>
            <div class="ribbon-cell" style="border-top: 4px solid {c_kpi5};">
                <div class="ribbon-key">IQR Outliers</div>
                <div class="ribbon-val" style="color: {c_kpi5};">{overview['total_outliers_detected']:,}</div>
            </div>
            <div class="ribbon-cell" style="border-top: 4px solid {c_kpi6};">
                <div class="ribbon-key">Memory Footprint</div>
                <div class="ribbon-val" style="color: {c_kpi6};">{overview['memory_usage_str']}</div>
            </div>
        </div>
        """
    )

    col_rad, col_mis = st.columns([1, 1])

    chart_bg = "#FFFFFF" if is_light else "#101422"
    chart_grid = "#CBD5E1" if is_light else "#202942"
    chart_text = "#0F172A" if is_light else "#F8FAFC"
    chart_axis = "#475569" if is_light else "#94A3B8"

    with col_rad:
        st.markdown("**5 Pillars Quality Radar Profile**")
        dim_names = [d["label"] for d in dims.values()]
        dim_scores = [d["score"] for d in dims.values()]

        radar_line_color = "#EA580C" if is_light else "#FF5533"
        radar_fill_color = "rgba(234, 88, 12, 0.2)" if is_light else "rgba(255, 85, 51, 0.25)"

        fig_radar = go.Figure(
            data=go.Scatterpolar(
                r=dim_scores + [dim_scores[0]],
                theta=dim_names + [dim_names[0]],
                fill="toself",
                fillcolor=radar_fill_color,
                line=dict(color=radar_line_color, width=2.5),
                marker=dict(size=6, color=radar_line_color),
            )
        )
        fig_radar.update_layout(
            font=dict(family="IBM Plex Mono, Cascadia Code, Consolas, monospace"),
            polar=dict(
                bgcolor=chart_bg,
                radialaxis=dict(visible=True, range=[0, 100], gridcolor=chart_grid, color=chart_axis),
                angularaxis=dict(gridcolor=chart_grid, color=chart_text),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(l=35, r=35, t=20, b=20),
            height=300,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_mis:
        st.markdown("**Feature Sparsity & Missing Density**")
        missing_data = [
            {"Feature": c, "Missing %": p["missing_percentage"], "Count": p["missing_count"]}
            for c, p in profile["columns"].items()
        ]
        missing_df = pd.DataFrame(missing_data).sort_values("Missing %", ascending=False)
        colorscale = ["#059669", "#D97706", "#DC2626"] if is_light else ["#00F59B", "#FFD000", "#FF2E93"]
        fig_missing = px.bar(
            missing_df,
            x="Missing %",
            y="Feature",
            orientation="h",
            color="Missing %",
            color_continuous_scale=colorscale,
            text="Missing %",
            height=300,
        )
        fig_missing.update_layout(
            font=dict(family="IBM Plex Mono, Cascadia Code, Consolas, monospace"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=chart_bg,
            margin=dict(l=20, r=20, t=10, b=20),
            yaxis=dict(autorange="reversed", gridcolor=chart_grid, color=chart_text),
            xaxis=dict(gridcolor=chart_grid, color=chart_axis),
            coloraxis_showscale=False,
        )
        fig_missing.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        st.plotly_chart(fig_missing, use_container_width=True)

    render_html("<div style='height: 8px;'></div>")
    st.markdown("**Automated Remediation Action Register**")
    recs = quality.get("recommendations", [])
    if not recs:
        st.success("✓ Zero data hygiene defects detected. Dataset conforms to clean analytical standards.")
    else:
        for r in recs:
            p = r["priority"]
            p_class = "task-priority-crit" if p == "CRITICAL" else ("task-priority-high" if p == "HIGH" else "task-priority-info")
            if is_light:
                border_c = "#DC2626" if p == "CRITICAL" else ("#D97706" if p == "HIGH" else "#0284C7")
            else:
                border_c = "#FF2E93" if p == "CRITICAL" else ("#FFD000" if p == "HIGH" else "#00C8FF")
            with st.expander(f"[{p}] {r['category']} — {r['message']}"):
                render_html(
                    f"""
                    <div class="task-card" style="border-left-color: {border_c};">
                        <div class="task-meta">
                            <span class="{p_class}">PRIORITY: {p}</span>
                            <span class="task-category">CATEGORY: {r['category']}</span>
                        </div>
                        <div class="task-msg">{r['message']}</div>
                    </div>
                    """
                )
                if r.get("action"):
                    st.code(r["action"], language="python")


# =============================================================
# STAGE 03: FEATURE DIAGNOSTICS
# =============================================================
elif selected_stage == "03 · Feature Diagnostics":
    col_names = list(profile["columns"].keys())

    c_sel, _ = st.columns([2, 1])
    with c_sel:
        selected_col = st.selectbox("Select Target Feature to Audit:", col_names)

    c_prof = profile["columns"][selected_col]
    c_health = quality["columns"].get(selected_col, {})

    c_grade = c_health.get("grade", "N/A")
    c_score = c_health.get("score", 0)
    if is_light:
        c_color = (
            "#059669" if c_grade == "A"
            else ("#0284C7" if c_grade == "B"
            else ("#D97706" if c_grade == "C"
            else ("#EA580C" if c_grade == "D"
            else "#DC2626")))
        )
    else:
        c_color = (
            "#00F59B" if c_grade == "A"
            else ("#00C8FF" if c_grade == "B"
            else ("#FFD000" if c_grade == "C"
            else ("#FF5533" if c_grade == "D"
            else "#FF2E93")))
        )

    ltype = c_prof.get('logical_type', 'Unknown')
    if ltype in ["Integer", "Float", "Percentage", "Currency"]:
        tag_style = (
            "border: 1px solid #059669; color: #059669; background: #D1FAE5;"
            if is_light else
            "border: 1px solid #00F59B; color: #00F59B; background: rgba(0, 245, 155, 0.15);"
        )
    elif ltype in ["Date", "DateTime", "Time"]:
        tag_style = (
            "border: 1px solid #7C3AED; color: #7C3AED; background: #EDE9FE;"
            if is_light else
            "border: 1px solid #A855F7; color: #A855F7; background: rgba(168, 85, 247, 0.15);"
        )
    else:
        tag_style = (
            "border: 1px solid #D97706; color: #D97706; background: #FEF3C7;"
            if is_light else
            "border: 1px solid #FFD000; color: #FFD000; background: rgba(255, 208, 0, 0.15);"
        )

    val_col1 = "#DC2626" if is_light else "#FF2E93"
    val_col2 = "#0284C7" if is_light else "#00C8FF"
    val_col3 = "#7C3AED" if is_light else "#A855F7"

    render_html(
        f"""
        <div class="feature-bar">
            <div>
                <span class="feature-name-lg">{selected_col}</span>
                <span class="feature-tag" style="margin-left: 8px; {tag_style}">{ltype}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 14px; font-family: 'IBM Plex Mono', 'Cascadia Code', monospace; font-size: 13.5px;">
                <span>HEALTH: <strong style="color: {c_color}; font-weight: 800;">GRADE {c_grade} ({c_score}%)</strong></span>
                <span>MISSING: <strong style="color: {val_col1}; font-weight: 800;">{c_prof.get('missing_count', 0)} ({c_prof.get('missing_percentage', 0)}%)</strong></span>
                <span>DISTINCT: <strong style="color: {val_col2}; font-weight: 800;">{c_prof.get('distinct_count', 0):,}</strong></span>
                <span>UNIQUENESS: <strong style="color: {val_col3}; font-weight: 800;">{c_prof.get('distinct_ratio', 0):.4f}</strong></span>
            </div>
        </div>
        """
    )

    if c_health.get("issues"):
        for iss in c_health["issues"]:
            st.warning(f"Detected Anomaly: {iss}")

    series = df[selected_col].dropna()
    chart_bg = "#FFFFFF" if is_light else "#101422"
    chart_grid = "#CBD5E1" if is_light else "#202942"
    chart_axis = "#475569" if is_light else "#94A3B8"

    if c_prof.get("numeric_stats"):
        n_stats = c_prof["numeric_stats"]
        v1, v2 = st.columns([1, 1])

        with v1:
            st.markdown("**Empirical Distribution Histogram**")
            fig_hist = px.histogram(
                df,
                x=selected_col,
                nbins=30,
                marginal="box",
                title=None,
                color_discrete_sequence=["#EA580C" if is_light else "#FF5533"],
            )
            fig_hist.update_layout(
                font=dict(family="IBM Plex Mono, Cascadia Code, Consolas, monospace"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor=chart_bg,
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
                xaxis=dict(gridcolor=chart_grid, color=chart_axis),
                yaxis=dict(gridcolor=chart_grid, color=chart_axis),
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with v2:
            st.markdown("**Tukey Outlier Boxplot & Boundary Fences**")
            iqr_data = c_prof.get("outliers_iqr")
            if iqr_data:
                c_fence = "#0284C7" if is_light else "#00C8FF"
                c_out = "#DC2626" if is_light else "#FF2E93"
                render_html(
                    f"<div style='font-family: \"IBM Plex Mono\", \"Cascadia Code\", monospace; font-size: 13px; color: {'#64748B' if is_light else '#94A3B8'}; margin-bottom: 6px;'>"
                    f"FENCES: <span style='color: {c_fence}; font-weight: 800;'>[{iqr_data['lower_bound']}, {iqr_data['upper_bound']}]</span> • "
                    f"OUTLIERS: <span style='color: {c_out}; font-weight: 800;'>{iqr_data['outlier_count']} ({iqr_data['outlier_percentage']}%)</span>"
                    f"</div>"
                )

            fig_box = px.box(
                df,
                y=selected_col,
                points="outliers",
                title=None,
                color_discrete_sequence=["#DC2626" if is_light else "#FF2E93"],
            )
            fig_box.update_layout(
                font=dict(family="IBM Plex Mono, Cascadia Code, Consolas, monospace"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor=chart_bg,
                margin=dict(l=20, r=20, t=10, b=20),
                height=260,
                yaxis=dict(gridcolor=chart_grid, color=chart_axis),
            )
            st.plotly_chart(fig_box, use_container_width=True)

        render_html("<div style='height: 8px;'></div>")
        st.markdown("**Parametric & Non-Parametric Statistical Ledger**")

        stat_rows = [
            {"Metric": "Sample Mean", "Value": f"{n_stats['mean']:,}", "Description": "Arithmetic average"},
            {"Metric": "Standard Deviation", "Value": f"{n_stats['std']:,}", "Description": "Degree of dispersion"},
            {"Metric": "Minimum", "Value": f"{n_stats['min']:,}", "Description": "Observed lower boundary"},
            {"Metric": "25th Percentile (Q1)", "Value": f"{n_stats['q25']:,}", "Description": "Lower quartile"},
            {"Metric": "Median (Q2)", "Value": f"{n_stats['median']:,}", "Description": "50th percentile midpoint"},
            {"Metric": "75th Percentile (Q3)", "Value": f"{n_stats['q75']:,}", "Description": "Upper quartile"},
            {"Metric": "Maximum", "Value": f"{n_stats['max']:,}", "Description": "Observed upper boundary"},
            {"Metric": "Interquartile Range (IQR)", "Value": f"{n_stats['iqr']:,}", "Description": "Spread of middle 50%"},
            {"Metric": "Skewness", "Value": str(n_stats['skewness']), "Description": "Distribution asymmetry"},
            {"Metric": "Kurtosis", "Value": str(n_stats['kurtosis']), "Description": "Tailedness / peakedness"},
            {"Metric": "Zero Values Count", "Value": f"{n_stats['zeros_count']} ({n_stats['zeros_percentage']}%)", "Description": "Zero-entry observations"},
            {"Metric": "Negative Values Count", "Value": f"{n_stats['negative_count']} ({n_stats['negative_percentage']}%)", "Description": "Values strictly < 0"},
        ]
        st.dataframe(pd.DataFrame(stat_rows), use_container_width=True, hide_index=True)

    elif c_prof.get("categorical_stats"):
        c_stats = c_prof["categorical_stats"]
        v1, v2 = st.columns([1, 1])

        with v1:
            st.markdown("**Top Frequent Categories**")
            top_df = pd.DataFrame(c_stats["top_frequent"])
            if not top_df.empty:
                cat_scale = ["#7C3AED", "#A78BFA"] if is_light else ["#A855F7", "#C084FC"]
                fig_cat = px.bar(
                    top_df,
                    x="count",
                    y="value",
                    orientation="h",
                    color="count",
                    color_continuous_scale=cat_scale,
                    text="percentage",
                    title=None,
                )
                fig_cat.update_layout(
                    font=dict(family="IBM Plex Mono, Cascadia Code, Consolas, monospace"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor=chart_bg,
                    yaxis=dict(autorange="reversed", gridcolor=chart_grid, color="#0F172A" if is_light else "#E2E8F0"),
                    xaxis=dict(gridcolor=chart_grid, color=chart_axis),
                    coloraxis_showscale=False,
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=300,
                )
                fig_cat.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                st.plotly_chart(fig_cat, use_container_width=True)

        with v2:
            st.markdown("**Text Hygiene & String Metrics**")
            text_stats = [
                {"Metric": "Modal Category", "Value": str(c_stats['mode'])},
                {"Metric": "Mode Occurrence Frequency", "Value": f"{c_stats['mode_frequency']:,}"},
                {"Metric": "Minimum String Length", "Value": f"{c_stats['min_length']} chars"},
                {"Metric": "Maximum String Length", "Value": f"{c_stats['max_length']} chars"},
                {"Metric": "Average String Length", "Value": f"{c_stats['avg_length']} chars"},
                {"Metric": "Untrimmed Whitespace Errors", "Value": f"{c_stats['whitespace_issues']} rows"},
            ]
            st.dataframe(pd.DataFrame(text_stats), use_container_width=True, hide_index=True)

            if c_stats["whitespace_issues"] > 0:
                st.info("Sanitation Advice: Run `df[col] = df[col].astype(str).str.strip()` to eliminate leading/trailing whitespace.")

    elif c_prof.get("datetime_stats"):
        d_stats = c_prof["datetime_stats"]
        st.markdown("**Temporal Horizon**")
        dt_data = [
            {"Metric": "Earliest Recorded Timestamp", "Value": str(d_stats['min_date'])},
            {"Metric": "Latest Recorded Timestamp", "Value": str(d_stats['max_date'])},
            {"Metric": "Total Elapsed Span", "Value": f"{d_stats['span_days']} days"},
        ]
        st.dataframe(pd.DataFrame(dt_data), use_container_width=True, hide_index=True)


# =============================================================
# STAGE 04: GOVERNANCE & EXPORTS
# =============================================================
elif selected_stage == "04 · Governance & Exports":
    st.markdown("**Comprehensive Feature Governance Audit Matrix**")
    audit_rows = []
    for col_name, c_prof in profile["columns"].items():
        c_health = quality["columns"].get(col_name, {})
        iqr_info = c_prof.get("outliers_iqr")
        outliers_str = (
            f"{iqr_info['outlier_count']} ({iqr_info['outlier_percentage']}%)"
            if iqr_info
            else "—"
        )
        audit_rows.append({
            "Feature": col_name,
            "Logical Type": c_prof["logical_type"],
            "Health Grade": f"{c_health.get('grade')} ({c_health.get('score')}%)",
            "Missing %": f"{c_prof['missing_percentage']}%",
            "Distinct Count": f"{c_prof['distinct_count']:,}",
            "Outliers (IQR)": outliers_str,
            "Audit Notes": "; ".join(c_health.get("issues", [])) or "Clean (Pristine)",
        })
    audit_df = pd.DataFrame(audit_rows)
    st.dataframe(audit_df, use_container_width=True, hide_index=True)

    render_html("<div style='height: 16px;'></div>")
    st.markdown("**Export Artifact Console**")
    st.caption("Generate verifiable audit deliverables for engineering compliance and CI/CD data gates.")

    exp_c1, exp_c2, exp_c3, exp_c4 = st.columns(4)

    # 1. HTML Report
    html_content = generate_html_report(profile, validation, quality)
    with exp_c1:
        st.download_button(
            label="🌐 Download HTML Report",
            data=html_content,
            file_name=f"{active_filename.replace('.csv', '')}_quality_report.html",
            mime="text/html",
            use_container_width=True,
        )

    # 2. JSON Audit Report
    json_content = generate_json_report(profile, validation, quality)
    with exp_c2:
        st.download_button(
            label="📄 Download JSON Schema Audit",
            data=json_content,
            file_name=f"{active_filename.replace('.csv', '')}_audit.json",
            mime="application/json",
            use_container_width=True,
        )

    # 3. Markdown Summary
    md_content = generate_markdown_report(profile, validation, quality)
    with exp_c3:
        st.download_button(
            label="📝 Download Markdown PR Summary",
            data=md_content,
            file_name=f"{active_filename.replace('.csv', '')}_summary.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # 4. Feature Profile CSV
    csv_buffer = io.StringIO()
    audit_df.to_csv(csv_buffer, index=False)
    with exp_c4:
        st.download_button(
            label="📊 Download Feature Profile CSV",
            data=csv_buffer.getvalue(),
            file_name=f"{active_filename.replace('.csv', '')}_features_profile.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # Automated Cleaning Engine
    render_html("<div style='height: 20px;'></div>")
    engine_box_bg = "#ECFDF5" if is_light else "#0B1C14"
    engine_box_border = "#059669" if is_light else "#00F59B"
    engine_box_title = "#065F46" if is_light else "#00F59B"

    render_html(
        f"""
        <div style="background: {engine_box_bg}; border: 1px solid {engine_box_border}; border-left: 4px solid {engine_box_border}; border-radius: 8px; padding: 18px 22px; box-shadow: 0 4px 14px rgba(15,23,42,0.06);">
            <div style="font-family: 'IBM Plex Mono', 'Cascadia Code', monospace; font-size: 12px; font-weight: 800; color: {engine_box_title}; letter-spacing: 1.5px; text-transform: uppercase;">AUTOMATED REMEDIATION ENGINE</div>
            <div style="font-family: 'IBM Plex Mono', 'Cascadia Code', monospace; font-size: 18px; font-weight: 800; color: {'#0F172A' if is_light else '#FFFFFF'}; margin-top: 2px;">One-Click Auto-Cleaned Dataset Export</div>
            <div style="font-size: 13.5px; color: {'#475569' if is_light else '#94A3B8'}; margin-top: 4px; line-height: 1.4; font-family: 'IBM Plex Mono', 'Cascadia Code', monospace;">
                Executes automated baseline hygiene: drops completely empty rows (all-NaN), purges exact duplicate records, and trims whitespace contamination across all text features.
            </div>
        </div>
        """
    )
    render_html("<div style='height: 8px;'></div>")

    clean_df = df.copy()
    initial_rows = len(clean_df)

    clean_df.dropna(how="all", inplace=True)
    clean_df.drop_duplicates(inplace=True)
    for c in clean_df.select_dtypes(include=["object", "string"]).columns:
        clean_df[c] = clean_df[c].apply(lambda x: x.strip() if isinstance(x, str) else x)

    removed_rows = initial_rows - len(clean_df)

    col_cl_l, col_cl_r = st.columns([2, 1])
    with col_cl_l:
        st.write(
            f"**Cleaned Buffer Output:** `{len(clean_df):,} rows` ({removed_rows} redundant or empty rows eliminated)"
        )
    with col_cl_r:
        clean_csv_buf = io.StringIO()
        clean_df.to_csv(clean_csv_buf, index=False)
        st.download_button(
            label="📥 Download Auto-Cleaned CSV",
            data=clean_csv_buf.getvalue(),
            file_name=f"{active_filename.replace('.csv', '')}_cleaned.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True,
        )
