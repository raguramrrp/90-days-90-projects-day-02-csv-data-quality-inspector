"""
Screenshot Capture Script
Generates real, high-resolution visual demonstration screenshots
for the Automated Dataset Quality & Profiling Engine using Headless Chrome & CDP.
"""

import os
import sys
import subprocess
import time
import shutil
import json
import base64
import asyncio
import requests
import websockets
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
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(os.environ.get("LOCALAPPDATA", "C:\\Temp"), "Temp")


def take_static_screenshot(url: str, output_filename: str, width: int = 1400, height: int = 900):
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
    subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    time.sleep(1)

    final_target = os.path.join(SCREENSHOTS_DIR, output_filename)
    if os.path.exists(temp_target):
        shutil.copy2(temp_target, final_target)
        os.remove(temp_target)
        print(f"Captured static screenshot: {final_target} ({os.path.getsize(final_target):,} bytes)")
        return True
    return False


async def capture_cdp_screenshot(url: str, output_path: str, width: int = 1440, height: int = 900, wait_seconds: int = 6):
    chrome_proc = subprocess.Popen(
        [
            CHROME_PATH,
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--remote-debugging-port=9222",
            f"--window-size={width},{height}",
            url,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)

    try:
        targets = requests.get("http://localhost:9222/json").json()
        target = next((t for t in targets if t.get("type") == "page"), targets[0])
        ws_url = target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            # Let Streamlit WebSocket and charts mount completely
            await asyncio.sleep(wait_seconds)

            # Capture screenshot via CDP
            msg = {"id": 1, "method": "Page.captureScreenshot", "params": {"format": "png"}}
            await ws.send(json.dumps(msg))
            resp = await ws.recv()
            data = json.loads(resp)
            img_b64 = data["result"]["data"]
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(img_b64))
            print(f"Captured CDP screenshot: {output_path} ({os.path.getsize(output_path):,} bytes)")
            return True
    finally:
        chrome_proc.terminate()
        chrome_proc.wait()


def main():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

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
    take_static_screenshot(f"file:///{temp_html_path.replace(os.sep, '/')}", "01_html_quality_report.png")

    # 2. Launch Streamlit and capture live dashboard views via CDP
    python_exe = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
    port = 8506
    streamlit_proc = subprocess.Popen(
        [python_exe, "-m", "streamlit", "run", "src/app.py", f"--server.port={port}", "--server.headless=true"],
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"Launched Streamlit on port {port} for screenshot capture...")
    time.sleep(6)

    try:
        overview_path = os.path.join(SCREENSHOTS_DIR, "02_streamlit_overview.png")
        asyncio.run(capture_cdp_screenshot(f"http://localhost:{port}", overview_path, width=1440, height=920, wait_seconds=6))

        # Capture Swiss Light mode
        light_path = os.path.join(SCREENSHOTS_DIR, "03_streamlit_light_mode.png")
        asyncio.run(capture_cdp_screenshot(f"http://localhost:{port}/?theme=light", light_path, width=1440, height=920, wait_seconds=6))
    finally:
        streamlit_proc.terminate()
        streamlit_proc.wait()
        print("Terminated Streamlit process.")

    # Cleanup temp html
    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)


if __name__ == "__main__":
    main()
