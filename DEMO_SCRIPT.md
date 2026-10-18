# 🎙️ Live Demo & Presentation Script (3-5 Minutes)

**Automated Dataset Quality & Profiling Engine**  
*Day 2 of 90 Days 90 Projects Challenge*

---

## Target Audience
- Data Science & Data Engineering Interviewers
- Technical Hiring Managers & Analytics Leads
- Data Governance & Data Quality Stakeholders

---

## Step-by-Step Demonstration Flow

### 0:00 - 0:45 | The Hook & Problem Statement
> *"Hello everyone! In data analytics and machine learning, we've all heard the phrase 'garbage in, garbage out.' In industry, data practitioners spend upwards of 60% of their time writing repetitive Pandas code just to verify basic dataset hygiene—finding nulls, detecting duplicates, spotting outliers, and converting corrupted data types. Today, I built an Automated Dataset Quality & Profiling Engine that solves this completely in seconds."*

---

### 0:45 - 1:45 | Ingestion & In-Flight Validation (Screen 1)
- **Action:** Open `http://localhost:8501`. Show the sidebar with the benchmark dataset choices.
- **Talking Points:**
  - *"Notice the file ingestion layer in Screen 1. When a user uploads a CSV, they don't even have to specify if it's UTF-8 or Latin-1, or whether the separator is a comma, semicolon, or tab. The engine automatically sniffs the encoding and delimiter with fallback heuristics."*
  - *"Here we load our `sample_ecommerce_dirty.csv`. In milliseconds, the validator checks for corrupted headers, index column leakage, and delimiter collapse."*

---

### 1:45 - 2:45 | Executive Overview & 5 Pillars of Quality (Screen 2)
- **Action:** Click **"📊 2. Dataset Overview"**.
- **Talking Points:**
  - *"Instead of burying analysts in hundreds of disparate summary tables, the engine synthesizes dataset health into a transparent, explainable 0 to 100 Quality Score with a letter grade."*
  - *"This e-commerce dataset receives a **70.1 (Grade C)**. But what's truly powerful is the **5 Pillars of Data Quality Radar**: Completeness, Uniqueness, Consistency, Outlier Health, and Structural Integrity."*
  - *"Scroll down to the **Automated Recommendations**: The engine doesn't just diagnose problems; it gives engineers copy-pasteable Python code to drop 100% null columns, deduplicate rows, and handle outliers."*

---

### 2:45 - 3:45 | Column Deep-Dive & Outlier Detection (Screen 3)
- **Action:** Click **"🔍 3. Column Deep-Dive"** and select `unit_price`.
- **Talking Points:**
  - *"In Screen 3, we can drill down into individual features. For numerical columns like `unit_price`, the engine performs Tukey's IQR outlier analysis alongside standardized Z-scores. We immediately see the lower and upper fences, and the boxplot flags severe positive outliers and erroneous negative prices."*
  - *"If we switch to `category`, the engine switches dynamically to categorical mode—showing frequency counts and detecting untrimmed leading or trailing whitespace."*

---

### 3:45 - 4:30 | Report Center & CI/CD Integration (Screen 4)
- **Action:** Click **"📑 4. Quality Report & Export"**.
- **Talking Points:**
  - *"Finally, Screen 4 turns these insights into deliverables. Analysts can download a standalone, responsive HTML report that works completely offline for stakeholders, a CI/CD-compatible JSON audit report for Airflow or dbt pipeline gates, or a GitHub-ready Markdown summary."*
  - *"There's even a **One-Click Auto-Cleaned CSV** that automatically strips whitespace and drops duplicate rows."*

---

### 4:30 - 5:00 | Engineering Rigor & Closing
- **Talking Points:**
  - *"Under the hood, the engine includes a full automated test suite with 25 unit and end-to-end tests passing in under 1.5 seconds. It is designed with pure Python and Pandas without external SaaS dependencies, making it easy to deploy on Streamlit Cloud or containerize into Docker."*
  - *"Thank you! I'd love to answer any questions about the scoring algorithm or architecture."*
