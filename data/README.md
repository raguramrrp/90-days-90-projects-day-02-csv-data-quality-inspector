# Sample Datasets & Benchmarks

This directory contains benchmark CSV datasets crafted to evaluate and demonstrate the automated profiling and quality assessment capabilities of the **Automated Dataset Quality & Profiling Engine**.

---

## 1. `sample_ecommerce_dirty.csv` (Real-World Flawed Ingestion)
- **Domain:** E-Commerce / Retail Operations
- **Row Count:** 527 rows
- **Column Count:** 11 columns
- **Expected Quality Grade:** `D` / `F` (~55% - 65%)
- **Embedded Data Quality Defects:**
  - **Severe Missingness:** Column `notes` has >90% missing values; `discount`, `rating`, and `status` have 10-25% missing cells.
  - **Duplicate Records:** ~25 duplicate order records injected via duplicate webhook delivery simulation.
  - **Empty Records:** 2 completely all-NaN rows.
  - **Statistical Outliers:**
    - Extreme high unit prices (e.g. `$24,500.00` on general merchandise).
    - Bulk order quantity outliers (`quantity = 500`).
    - Negative unit price anomalies (`-$25.50`).
  - **Formatting & Whitespace Contamination:**
    - Inconsistent date formats (`YYYY-MM-DD` vs `MM/DD/YYYY`).
    - Leading/trailing whitespace in `category` and `country` values (e.g. `"  Electronics  "`).

---

## 2. `sample_employee_records.csv` (HR & People Analytics)
- **Domain:** Human Resources & Payroll
- **Row Count:** 360 rows
- **Column Count:** 10 columns
- **Expected Quality Grade:** `C` (~72% - 78%)
- **Embedded Data Quality Defects:**
  - **Constant Column (Zero Variance):** `company_name` is identical across all rows.
  - **Duplicate Entities:** 10 duplicate employee rows.
  - **Extreme Outliers:** Executive salaries exceeding `$1,200,000` against a median of `$75,000`.
  - **Invalid Domain Values:** Negative years of experience (`years_experience = -2`).
  - **Type & Representation Inconsistency:** `is_remote` contains mixed truthy representations (`"Yes"`, `"yes"`, `"NO"`, `"True"`).

---

## 3. `sample_clean_baseline.csv` (Gold Standard)
- **Domain:** Real Estate Listings & Valuation
- **Row Count:** 400 rows
- **Column Count:** 9 columns
- **Expected Quality Grade:** `A` (95% - 100%)
- **Characteristics:**
  - Zero missing cells (100% completeness).
  - Zero duplicate rows (100% uniqueness).
  - Well-bounded, plausible real estate distributions.
  - Valid primary key candidate (`property_id`).
  - Proper data typing and clean column naming.

---

## Generating Datasets
To regenerate or modify these benchmarks reproducibly:
```cmd
python scripts/generate_sample_data.py
```
