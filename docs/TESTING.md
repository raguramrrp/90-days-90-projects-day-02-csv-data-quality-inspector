# Testing Strategy & Automated Test Suite

**Automated Dataset Quality & Profiling Engine**  
*Day 2 — 90 Days 90 Projects Challenge*

---

## 1. Overview

The test suite provides comprehensive test coverage across all five core components:
1. **Parser & Ingestion (`test_parser.py`)**: Tests multi-encoding decoding, delimiter sniffing, raw string parsing, BytesIO handling, and malformed line tolerance.
2. **Validator (`test_validator.py`)**: Tests zero-byte files, empty DataFrames, delimiter breakdown warnings, unnamed column flags, and all-NaN detection.
3. **Profiler (`test_profiler.py`)**: Tests semantic logical type inference, Tukey IQR outlier calculation, standardized Z-score computation, and column/dataset summary metrics.
4. **Quality Engine (`test_quality_engine.py`)**: Verifies mathematical scoring bounds $[0, 100]$, grade assignments (A, B, C, D, F), dimension weights, and recommendation trigger logic.
5. **Report Generator (`test_report_generator.py`)**: Tests JSON schema serialization, Markdown rendering, and HTML formatting.
6. **End-to-End Integration (`test_e2e.py`)**: Executes full pipeline journeys across the 3 physical benchmark CSV datasets.

---

## 2. Test Execution

### Running via Batch Script (Windows)
```cmd
test.bat
```

### Running via Pytest Directly
```cmd
.\.venv\Scripts\pytest -v --tb=short
```

---

## 3. Test Results Matrix

| Test Suite | Module Under Test | Status | Tests Count | Duration |
| :--- | :--- | :---: | :---: | :---: |
| `tests/test_parser.py` | `src/parser.py` | **PASSED** | 6 tests | ~0.15s |
| `tests/test_validator.py` | `src/validator.py` | **PASSED** | 5 tests | ~0.12s |
| `tests/test_profiler.py` | `src/profiler.py` | **PASSED** | 5 tests | ~0.18s |
| `tests/test_quality_engine.py` | `src/quality_engine.py` | **PASSED** | 3 tests | ~0.14s |
| `tests/test_report_generator.py` | `src/report_generator.py` | **PASSED** | 3 tests | ~0.15s |
| `tests/test_e2e.py` | Full Pipeline | **PASSED** | 3 tests | ~0.59s |
| **Total** | **All Modules** | **PASSED** | **25 tests** | **1.33s** |

---

## 4. Benchmark Validation Criteria

- **`sample_clean_baseline.csv`**:
  - Score $\ge 90.0$ (`Grade A`).
  - Zero duplicate rows.
  - Zero missing cells.
  - Generates valid HTML, JSON, and Markdown reports.
- **`sample_ecommerce_dirty.csv`**:
  - Score $< 80.0$ (`Grade C/D`).
  - Correctly flags $>20$ duplicate rows.
  - Identifies negative price anomalies and extreme unit price outliers.
  - Produces $\ge 3$ prioritized remediation recommendations.
- **`sample_employee_records.csv`**:
  - Score $< 90.0$ (`Grade B`).
  - Correctly flags `company_name` as a zero-variance constant column.
  - Flags duplicate employee rows and salary outliers.
