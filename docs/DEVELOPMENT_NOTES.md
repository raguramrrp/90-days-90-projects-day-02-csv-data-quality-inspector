# Development Notes & Technical Journal

**Automated Dataset Quality & Profiling Engine**  
*Day 2 — 90 Days 90 Projects Challenge*

---

## 1. Engineering Challenges & Solutions

### Challenge 1: Pandas 3.0 StringDtype Migration
- **Problem:** In Pandas 3.0+, default string series created from string literals or read from CSV no longer default to `dtype: object`. Instead, they instantiate as `dtype: str <class 'pandas.StringDtype'>`. Hardcoded checks like `series.dtype == "object"` silently failed, misclassifying string columns as numeric or missing them during whitespace sanitation.
- **Solution:** Replaced legacy `series.dtype == "object"` checks with `pd.api.types.is_string_dtype(series) or series.dtype == "object"`. This guarantees backward compatibility with Pandas 2.x and forward compatibility with Pandas 3.x.

### Challenge 2: NumPy 2.5 Boolean Subtraction Deprecation
- **Problem:** In NumPy 2.0+, the subtraction operator `-` on boolean ndarrays raises `TypeError: numpy boolean subtract, the '-' operator, is not supported`. When Pandas 3.0 calculates quantiles (`series.quantile(0.25)`) on boolean columns (which `pd.api.types.is_numeric_dtype` historically treated as numeric), NumPy attempts an internal linear interpolation (`b - a`), causing fatal execution crashes on clean datasets with boolean fields.
- **Solution:** Explicitly excluded boolean types from numeric quantification:
  ```python
  is_numeric = (
      pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series)
  ) or ("Integer" in logical_type or "Float" in logical_type)
  ```
  Boolean columns are now profiled as discrete categorical distributions rather than parametric continuous variables.

### Challenge 3: Reliable Delimiter Sniffing on Noisy CSVs
- **Problem:** Standard `csv.Sniffer()` frequently crashes on malformed CSV files, quoted multi-line text, or single-character separator variations.
- **Solution:** Implemented a two-tiered delimiter detection strategy:
  1. Attempt `csv.Sniffer().sniff(sample)`.
  2. Fall back to a multi-line consistency heuristic that counts occurrences of common delimiters (`,`, `;`, `\t`, `|`, `:`) across the first 10 non-empty lines, prioritizing delimiters that exhibit uniform column counts across rows.

### Challenge 4: Zero-Variance Feature Identification
- **Problem:** Constant columns (e.g. `company_name = 'Acme Corp'` across all 5,000 rows) add zero informational entropy to analytical queries or machine learning algorithms while consuming RAM and storage bandwidth.
- **Solution:** Automated detection of constant columns (`series.nunique(dropna=True) == 1`) with an automatic penalty applied to Structural Integrity and a high-priority recommendation to drop the feature before warehouse loading.

---

## 2. Performance & Memory Profiling

- **In-Memory Parsing:** Memory consumption is tracked with `df.memory_usage(deep=True).sum()`, ensuring real memory utilization (including heap allocations for string objects) is captured rather than shallow pointer sizes.
- **Streamlit Caching:** Leveraged `@st.cache_data(show_spinner=False)` on the `load_and_profile_data()` pipeline. When users switch between the 4 screens or interact with column dropdowns, the profiling results are retrieved in sub-millisecond time from the hash cache without re-parsing the CSV.

---

## 3. Future Upgrade Path

1. **Automated Cleaning Pipeline:** Expand the one-click auto-cleaner to support custom imputation rules (KNN, median, mode) and winsorization.
2. **REST API & Headless CLI:** Expose the engine as a FastAPI service or CLI tool (`dataset-inspect scan file.csv`) to serve as a pre-commit hook or Airflow quality gate.
3. **ML-Based Anomaly Detection:** Incorporate Isolation Forests or Local Outlier Factor (LOF) for multivariate anomaly detection across non-linear feature combinations.
