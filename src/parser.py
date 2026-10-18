"""
CSV Parser & Ingestion Module
Handles file loading, encoding detection, delimiter sniffing, and robust parsing.
"""

import csv
import io
import time
from typing import BinaryIO, Dict, Optional, Tuple, Union
import pandas as pd


COMMON_ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
COMMON_DELIMITERS = [",", ";", "\t", "|", ":"]


def detect_encoding(file_bytes: bytes) -> str:
    """
    Detects the character encoding of raw bytes by attempting to decode
    with common business and tabular data encodings.
    """
    for enc in COMMON_ENCODINGS:
        try:
            file_bytes.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue
    return "latin-1"  # Fallback: latin-1 can decode any byte sequence


def detect_delimiter(sample_text: str, default: str = ",") -> str:
    """
    Sniffs the delimiter from a text sample using csv.Sniffer,
    with a robust count-based heuristic fallback.
    """
    if not sample_text or not sample_text.strip():
        return default

    # 1. Try Python's built-in csv.Sniffer
    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample_text, delimiters=",;\t|:")
        if dialect and dialect.delimiter:
            return dialect.delimiter
    except Exception:
        pass

    # 2. Count-based fallback on non-empty lines
    lines = [line for line in sample_text.splitlines() if line.strip()][:10]
    if not lines:
        return default

    delimiter_scores = {}
    for delim in COMMON_DELIMITERS:
        counts = [line.count(delim) for line in lines]
        # High count and consistent count across rows
        if counts and min(counts) > 0:
            avg_count = sum(counts) / len(counts)
            consistency = 1.0 if len(set(counts)) == 1 else 0.8
            delimiter_scores[delim] = avg_count * consistency
        elif counts and sum(counts) > 0:
            delimiter_scores[delim] = sum(counts) / len(counts) * 0.5
        else:
            delimiter_scores[delim] = 0

    best_delim = max(delimiter_scores, key=delimiter_scores.get)
    if delimiter_scores[best_delim] > 0:
        return best_delim
    return default


def parse_csv(
    source: Union[str, bytes, io.BytesIO, io.StringIO, BinaryIO],
    delimiter: Optional[str] = None,
    encoding: Optional[str] = None,
    filename: Optional[str] = None,
    max_rows: Optional[int] = None,
) -> Tuple[pd.DataFrame, Dict]:
    """
    Parses a CSV file from various input types with automatic encoding
    and delimiter detection.

    Returns:
        (df, metadata_dict)
    """
    start_time = time.perf_counter()
    metadata: Dict = {
        "filename": filename or "dataset.csv",
        "file_size_bytes": 0,
        "encoding": encoding,
        "delimiter": delimiter,
        "warnings": [],
        "parse_time_ms": 0.0,
    }

    raw_bytes: bytes = b""

    # Step 1: Read raw bytes
    if isinstance(source, str):
        # Could be a file path or raw string
        try:
            with open(source, "rb") as f:
                raw_bytes = f.read()
                if not filename:
                    metadata["filename"] = source.split("/")[-1].split("\\")[-1]
        except (OSError, FileNotFoundError):
            # Treat as raw string content
            raw_bytes = source.encode("utf-8")
    elif isinstance(source, bytes):
        raw_bytes = source
    elif hasattr(source, "read"):
        raw_bytes = source.read()
        if hasattr(source, "seek"):
            source.seek(0)
    else:
        raise ValueError(f"Unsupported source type for CSV parsing: {type(source)}")

    metadata["file_size_bytes"] = len(raw_bytes)

    if len(raw_bytes) == 0:
        elapsed = (time.perf_counter() - start_time) * 1000
        metadata["parse_time_ms"] = round(elapsed, 2)
        metadata["warnings"].append("Input source is empty (0 bytes).")
        return pd.DataFrame(), metadata

    # Step 2: Detect encoding
    if not metadata["encoding"]:
        metadata["encoding"] = detect_encoding(raw_bytes[:65536])

    # Decode text sample for delimiter sniffing
    try:
        sample_text = raw_bytes[:32768].decode(metadata["encoding"], errors="replace")
    except Exception:
        sample_text = raw_bytes[:32768].decode("latin-1", errors="replace")
        metadata["encoding"] = "latin-1"

    # Step 3: Detect delimiter
    if not metadata["delimiter"]:
        metadata["delimiter"] = detect_delimiter(sample_text)

    # Step 4: Parse DataFrame
    buffer = io.BytesIO(raw_bytes)
    try:
        df = pd.read_csv(
            buffer,
            sep=metadata["delimiter"],
            encoding=metadata["encoding"],
            nrows=max_rows,
            on_bad_lines="warn",
            low_memory=False,
        )
    except Exception as e:
        # Fallback with python engine if C engine fails on irregular delimiters
        buffer.seek(0)
        try:
            df = pd.read_csv(
                buffer,
                sep=metadata["delimiter"],
                encoding=metadata["encoding"],
                engine="python",
                nrows=max_rows,
                on_bad_lines="skip",
            )
            metadata["warnings"].append(
                f"Parsed with Python fallback engine due to engine error: {str(e)}"
            )
        except Exception as e2:
            elapsed = (time.perf_counter() - start_time) * 1000
            metadata["parse_time_ms"] = round(elapsed, 2)
            metadata["warnings"].append(f"Fatal parsing failure: {str(e2)}")
            return pd.DataFrame(), metadata

    elapsed = (time.perf_counter() - start_time) * 1000
    metadata["parse_time_ms"] = round(elapsed, 2)
    metadata["row_count"] = len(df)
    metadata["column_count"] = len(df.columns)

    return df, metadata
