# ⚡ Quick Start Guide (Under 2 Minutes)

**Automated Dataset Quality & Profiling Engine**  
*Day 2 of 90 Days 90 Projects Challenge*

---

## Prerequisites
- Windows 10/11, macOS, or Linux
- Python 3.10, 3.11, or 3.12 installed on system PATH

---

## 1. Automated Setup (Windows)

Run the included automated setup script:
```cmd
setup.bat
```
This script will:
1. Detect your local Python installation.
2. Create an isolated virtual environment (`.venv`).
3. Install all required dependencies (`streamlit`, `pandas`, `plotly`, `pytest`, `jinja2`).
4. Generate the 3 benchmark datasets (`sample_ecommerce_dirty.csv`, `sample_employee_records.csv`, `sample_clean_baseline.csv`).

---

## 2. Launch the Application

Execute:
```cmd
run.bat
```
Streamlit will launch and open `http://localhost:8501` in your default browser.

---

## 3. Immediate 30-Second Test Drive

1. In the sidebar dropdown, select **"Sample: Dirty E-Commerce (Flawed)"**.
2. Click **"📊 2. Dataset Overview"** to view:
   - The Composite Quality Score (`70.1 / 100`, Grade C).
   - The 5 Pillars of Quality Radar Chart.
   - High-priority automated remediation recommendations (deduplication, dropping empty notes, winsorizing outliers).
3. Click **"🔍 3. Column Deep-Dive"** and inspect `unit_price` to see the Tukey outlier boxplot highlighting negative and extreme price points.
4. Click **"📑 4. Quality Report & Export"** and click **"🌐 Download HTML Report"** to get a self-contained, offline-viewable quality audit report!

---

## 4. Run Automated Tests

To verify all 25 unit and end-to-end tests:
```cmd
test.bat
```
Expected output: `25 passed in ~1.3s`.
