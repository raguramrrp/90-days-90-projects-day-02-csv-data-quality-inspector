"""
Unit tests for the CSV Parser and Ingestion Module.
"""

import io
import pytest
import pandas as pd
from src.parser import detect_encoding, detect_delimiter, parse_csv


def test_detect_encoding():
    utf8_bytes = "order_id,name\n1,Alice\n2,Bob".encode("utf-8")
    assert detect_encoding(utf8_bytes) in ["utf-8", "utf-8-sig"]

    latin1_bytes = "id,name\n1,René\n2,Hélène".encode("latin-1")
    detected = detect_encoding(latin1_bytes)
    assert detected in ["latin-1", "iso-8859-1", "utf-8"]


def test_detect_delimiter():
    csv_comma = "id,name,age\n1,Alice,30\n2,Bob,25\n3,Charlie,35"
    assert detect_delimiter(csv_comma) == ","

    csv_semi = "id;name;age\n1;Alice;30\n2;Bob;25\n3;Charlie;35"
    assert detect_delimiter(csv_semi) == ";"

    csv_tab = "id\tname\tage\n1\tAlice\t30\n2\tBob\t25"
    assert detect_delimiter(csv_tab) == "\t"

    csv_pipe = "id|name|age\n1|Alice|30\n2|Bob|25"
    assert detect_delimiter(csv_pipe) == "|"


def test_parse_csv_string_content():
    content = "col_a,col_b,col_c\n10,foo,1.5\n20,bar,2.5\n30,baz,3.5"
    df, meta = parse_csv(content)
    assert len(df) == 3
    assert len(df.columns) == 3
    assert meta["delimiter"] == ","
    assert meta["row_count"] == 3
    assert meta["column_count"] == 3
    assert meta["parse_time_ms"] >= 0


def test_parse_csv_bytes_io():
    raw = b"id;val\n1;100\n2;200\n3;300"
    bio = io.BytesIO(raw)
    df, meta = parse_csv(bio)
    assert len(df) == 3
    assert meta["delimiter"] == ";"
    assert list(df.columns) == ["id", "val"]


def test_parse_csv_empty_content():
    df, meta = parse_csv(b"")
    assert df.empty
    assert len(meta["warnings"]) > 0
    assert "empty" in meta["warnings"][0].lower()


def test_parse_csv_malformed_lines():
    # Inconsistent column counts
    content = "a,b\n1,2\n3,4,5,6\n7,8"
    df, meta = parse_csv(content)
    assert not df.empty
    assert len(df.columns) == 2
