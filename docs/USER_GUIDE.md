# User Guide & Operational Walkthrough

**Automated Dataset Quality & Profiling Engine**  
*Day 2 — 90 Days 90 Projects Challenge*

---

## 1. Quick Launch

Launch the engine via the Windows batch launcher:
```cmd
run.bat
```
Or execute through Python:
```cmd
.\.venv\Scripts\streamlit run src/app.py
```
Open `http://localhost:8501` in any modern web browser.

---

## 2. Navigating the 4 Main Application Screens

### Screen 1: 📥 Upload & Ingestion
- **Selecting Data:**
  - Choose one of the 3 pre-loaded benchmark datasets from the sidebar dropdown (*Dirty E-Commerce*, *Employee Records*, or *Clean Baseline*).
  - Or select **"Upload Your Own CSV"** and drag-and-drop any `.csv` or `.txt` file up to 200MB.
- **Parsing Settings (Sidebar Expander):**
  - By default, delimiters and encodings are detected automatically.
  - If ingesting European CSVs formatted with semicolons (`;`) or tab-delimited files (`\t`), manual overrides can be selected.
- **Ingestion Telemetry:**
  - View the detected delimiter, detected character encoding, total raw rows parsed, and total columns.
  - Inspect the Raw Data Sample Preview table with customizable row limits.

---

### Screen 2: 📊 Dataset Overview
- **Executive Quality Hero:**
  - View the composite Data Quality Score (0–100) and letter grade (A, B, C, D, F).
  - Status indicator highlights whether the dataset is production-ready or in need of critical remediation.
- **5 Pillars of Data Quality Radar:**
  - An interactive radar chart mapping:
    1. **Completeness:** Evaluates missing cells, null rows, and empty columns.
    2. **Uniqueness:** Flags duplicate rows and entity redundancy.
    3. **Consistency & Validity:** Evaluates whitespace, invalid negatives, and type mismatches.
    4. **Outlier Health:** Evaluates variance and statistical anomalies.
    5. **Structural Integrity:** Measures column entropy, zero-variance features, and header soundness.
- **Missing Values Heatmap:**
  - Horizontal bar breakdown highlighting high-sparsity columns that risk degrading downstream models.
- **Automated Recommendations:**
  - Prioritized actionable directives (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) accompanied by exact Python code snippets you can copy into your data pipelines.

---

### Screen 3: 🔍 Column Deep-Dive
- **Column Selector:**
  - Select any column from the dropdown to view its dedicated profile.
- **Health Grade & Inferred Semantic Type:**
  - See whether a column was recognized as `Integer`, `Float`, `Datetime`, `Categorical`, `Text`, or `Boolean`.
- **Numerical Distribution:**
  - Interactive histogram with boxplot marginals.
  - Tukey Outlier Boxplot displaying $Q_1$, $Q_3$, IQR fences, and individual sample outliers.
  - Parametric metrics: Mean, standard deviation, skewness, kurtosis, zero value counts, and negative value counts.
- **Categorical & Text Hygiene:**
  - Frequency distribution bar chart of top values.
  - Text length analytics (min, max, average character length).
  - Untrimmed whitespace detection (flags strings containing accidental leading/trailing spaces).

---

### Screen 4: 📑 Quality Report & Export Center
- **Column Quality Matrix:**
  - Tabular overview of all columns, their types, health grades, missing percentages, and detected anomalies.
- **Export Center (One-Click Downloads):**
  - **🌐 Download HTML Report:** Standalone interactive HTML report with embedded CSS styling. Suitable for sharing with non-technical stakeholders or printing as PDF.
  - **📄 Download JSON Audit:** Full machine-readable schema for CI/CD automation, pipeline gates, and automated alerts.
  - **📝 Download Markdown Summary:** GitHub-flavored markdown report ready to paste into GitHub PR descriptions, Jira tickets, or Confluence.
  - **📊 Download Column CSV:** Tabular CSV of column metrics for archival.
  - **🧹 Download Auto-Cleaned CSV:** Automatically drops completely empty rows, deduplicates exact duplicate rows, and trims whitespace from string columns.
