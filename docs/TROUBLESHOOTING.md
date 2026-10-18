# Troubleshooting Guide & FAQ

**Automated Dataset Quality & Profiling Engine**  
*Day 2 — 90 Days 90 Projects Challenge*

---

## 1. Frequently Encountered Issues

### Issue 1: "The dataset parsed as a single column"
- **Cause:** The CSV uses an unusual delimiter (e.g. semicolon `;`, pipe `|`, or tab `\t`) and automatic sniffing was inconclusive due to irregular row lengths or quoted text.
- **Resolution:**
  1. Expand the **"⚙️ Parsing & Ingestion Settings"** expander in the sidebar.
  2. Change the delimiter dropdown from `Auto-Detect` to the specific delimiter used by your file (e.g. `;` or `\t`).
  3. The dataset will instantly re-parse with proper column splits.

---

### Issue 2: "UnicodeDecodeError / Garbled Characters"
- **Cause:** The file was exported with a Windows code page (such as CP1252) or legacy Latin-1, while UTF-8 was assumed.
- **Resolution:**
  - The engine automatically tries UTF-8, Latin-1, and CP1252 in sequence.
  - If characters like accented letters appear distorted, open the sidebar **"⚙️ Parsing & Ingestion Settings"** expander and select `latin-1` or `cp1252` explicitly.

---

### Issue 3: "Streamlit Port 8501 is already in use"
- **Cause:** Another Streamlit app or lingering process is running on the default port.
- **Resolution:**
  - Launch Streamlit on a different port:
    ```cmd
    .\.venv\Scripts\streamlit run src/app.py --server.port=8505
    ```

---

### Issue 4: "Out of Memory on Very Large CSV Files (>500MB)"
- **Cause:** Pandas loads the entire uncompressed tabular file into heap memory.
- **Resolution:**
  - For files exceeding 500MB, pre-sample the dataset or set `max_rows` in `src/parser.py`:
    ```python
    df, meta = parse_csv("huge_file.csv", max_rows=100000)
    ```
  - An exploratory sample of 50,000 to 100,000 rows provides $\ge 99.5\%$ statistical confidence for distributions, outliers, and missingness patterns without exhausting local RAM.

---

## 2. Health Check & Diagnostics

To verify your local installation and dependencies:
```cmd
.\.venv\Scripts\python -c "import pandas, streamlit, plotly, jinja2; print('All core libraries functional.')"
```
To run the automated diagnostic test suite:
```cmd
test.bat
```
