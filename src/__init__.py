"""
Automated Dataset Quality & Profiling Engine
Day 2 — 90 Days 90 Projects Challenge

A robust data profiling and automated quality assessment framework for tabular CSV datasets.
"""

__version__ = "1.0.0"
__author__ = "raguramrrp"

from .parser import parse_csv, detect_encoding, detect_delimiter
from .validator import validate_dataset
from .profiler import profile_dataset
from .quality_engine import calculate_quality_score
from .report_generator import generate_html_report, generate_json_report, generate_markdown_report

__all__ = [
    "parse_csv",
    "detect_encoding",
    "detect_delimiter",
    "validate_dataset",
    "profile_dataset",
    "calculate_quality_score",
    "generate_html_report",
    "generate_json_report",
    "generate_markdown_report",
]
