# Project Overview

**Automated Dataset Quality & Profiling Engine**  
*Day 2 — 90 Days 90 Projects Challenge*

---

## 1. Executive Summary

Data scientists, data engineers, and BI analysts spend an estimated **60% to 80% of their project time** performing manual exploratory data analysis (EDA), writing repetitive Pandas queries, and hunting down missing, corrupted, or duplicate data. 

The **Automated Dataset Quality & Profiling Engine** solves this problem by providing an instant, automated inspection suite for any CSV file. Within milliseconds of ingestion, the engine parses, validates, profiles, and scores the dataset across five core pillars of data health, generating actionable remediation advice and downloadable audit reports.

---

## 2. Key Problem Statement

When ingesting tabular data from third-party APIs, legacy databases, web scraping pipelines, or customer uploads:
- **Encoding & Delimiter Inconsistencies:** Files fail silently or parse into garbage single-column frames.
- **Hidden Outliers & Impossible Values:** Negative ages, negative prices, or executive salary outliers distort statistical models.
- **Silent Duplicates & Sparsity:** Webhook retries create duplicate rows, while high-sparsity columns pollute memory.
- **Formatting Contamination:** Trailing whitespace, inconsistent date formats, and numeric values wrapped in quotes break downstream SQL and machine learning pipelines.

---

## 3. The Solution

A lightweight, high-performance web dashboard and CLI-accessible Python engine that:
1. **Auto-sniffs** file encoding and delimiters.
2. **Performs deep profiling** of every column's distribution, cardinality, and entropy.
3. **Applies dual outlier detection** using Tukey's IQR and standardized Z-scores.
4. **Computes an explainable 0–100 Data Quality Score** with letter grades (A through F).
5. **Generates prioritized Python remediation actions** for immediate copy-pasting.
6. **Exports multi-format audit deliverables** (HTML, JSON, Markdown, CSV, and Auto-Cleaned data).

---

## 4. Key Specifications

| Specification | Detail |
| :--- | :--- |
| **Domain** | Data Engineering / Analytics / Data Governance |
| **Frontend Framework** | Streamlit (Python) |
| **Backend & Compute** | Python 3.12, Pandas 3.0, NumPy 2.5 |
| **Visualizations** | Plotly Express & Plotly Graph Objects |
| **Database** | None required (In-memory streaming) |
| **Auditing Exports** | HTML (Standalone CSS), JSON (CI/CD Schema), Markdown, CSV |
| **License** | MIT License |

---

## 5. Resume & Interview Value

- **Keywords:** Exploratory Data Analysis (EDA), Data Quality Assurance, Data Governance, Pandas Optimization, Data Cleaning Pipelines, Anomaly Detection.
- **Talking Points:**
  - Designed a transparent, multi-dimensional data quality scoring algorithm covering Completeness, Uniqueness, Consistency, Outlier Health, and Structural Integrity.
  - Implemented dual-method statistical outlier detection (IQR and Z-score) with automated fence computation.
  - Solved cross-version compatibility hurdles between Pandas 3.0 `StringDtype` and NumPy 2.5 boolean subtraction deprecation.
  - Delivered multi-format reports ready for CI/CD data gates and executive presentations.
