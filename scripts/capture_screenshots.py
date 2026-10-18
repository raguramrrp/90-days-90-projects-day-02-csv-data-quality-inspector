"""
Screenshot Capture Script
Generates real, high-resolution visual demonstration screenshots
for the Automated Dataset Quality & Profiling Engine using Headless Chrome.
"""

import os
import sys
import subprocess
import time
import shutil
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.parser import parse_csv
from src.validator import validate_dataset
from src.profiler import profile_dataset
from src.quality_engine import calculate_quality_score
from src.report_generator import generate_html_report

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(os.environ.get("LOCALAPPDATA", "C:\\Temp"), "Temp")


def take_screenshot(url: str, output_filename: str, width: int = 1366, height: int = 860, delay: int = 2):
    temp_target = os.path.join(TEMP_DIR, output_filename)
    if os.path.exists(temp_target):
        os.remove(temp_target)

    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        f"--window-size={width},{height}",
        f"--screenshot={temp_target}",
        url,
    ]
    subprocess.run(cmd, capture_output=True, text=True)
    time.sleep(delay)

    final_target = os.path.join(SCREENSHOTS_DIR, output_filename)
    if os.path.exists(temp_target):
        shutil.copy2(temp_target, final_target)
        os.remove(temp_target)
        print(f"Captured screenshot: {final_target} ({os.path.getsize(final_target):,} bytes)")
        return True
    else:
        print(f"Failed to capture {output_filename}")
        return False


def main():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    # 1. Generate HTML audit report for Dirty E-commerce
    ecom_path = os.path.join(DATA_DIR, "sample_ecommerce_dirty.csv")
    with open(ecom_path, "rb") as f:
        bytes_data = f.read()

    df, meta = parse_csv(bytes_data, filename="sample_ecommerce_dirty.csv")
    val = validate_dataset(df, meta)
    prof = profile_dataset(df, meta)
    qual = calculate_quality_score(prof, val)
    html_report = generate_html_report(prof, val, qual)

    temp_html_path = os.path.join(TEMP_DIR, "ecom_quality_report.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_report)

    # Screenshot HTML report
    take_screenshot(f"file:///{temp_html_path.replace(os.sep, '/')}", "01_html_quality_report.png", width=1400, height=900)

    # 2. Launch Streamlit and capture live dashboard views
    python_exe = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
    streamlit_proc = subprocess.Popen(
        [python_exe, "-m", "streamlit", "run", "src/app.py", "--server.port=8503", "--server.headless=true"],
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print("Launched Streamlit on port 8503 for screenshot capture...")
    time.sleep(4)

    try:
        take_screenshot("http://localhost:8503", "02_streamlit_overview.png", width=1400, height=900, delay=3)
    finally:
        streamlit_proc.terminate()
        streamlit_proc.wait()
        print("Terminated Streamlit process.")

    # Cleanup temp html
    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)


if __name__ == "__main__":
    main()
