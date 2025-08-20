
"""
loader.py — Robust loader for the 1925 Latvian "messy" meteorological text files.

Features
--------
- Auto-detects separator from the '# fields=' header (supports: TAB, ';', ',', '|').
- Reads arbitrary column order per file, using the header's field list.
- Normalizes:
    * mixed date formats (with/without embedded time),
    * precipitation strings (decimal commas, " mm", Latvian "nulle"),
    * missing tokens (empty, NA, —, -999),
    * present_weather_code to nullable integer (Int64).
- Adds: 'station' (from header), 'timestamp', 'date', 'time' columns.
- Returns one tidy pandas DataFrame or writes a merged CSV via CLI.

Example
-------
>>> import loader
>>> df = loader.load_all("/mnt/data")  # directory containing the 8 messy files
>>> df.head()

CLI
---
$ python loader.py --dir /mnt/data --out /mnt/data/latvia_meteo_1925_all_8_clean.csv
$ python loader.py --paths /mnt/data/riga_university_1925_p1.txt /mnt/data/liepaja_1925.txt
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple, Optional, Union

import numpy as np
import pandas as pd

# --- Constants ---

NA_TOKENS = {"", "NA", "—", "-999"}
WORD_ZERO = {"nulle", "NULLE"}  # Latvian for numeric zero

# Canonical tidy output column order
KEEP_COLS = [
    "station",
    "timestamp",
    "date",
    "time",
    "t_max_c",
    "t_min_c",
    "precip_24h_mm",
    "precip_type",
    "present_weather_code",
    "notes",
]


# --- Header & separator detection ---

def _detect_separator(fields_line: str) -> str:
    """Infer separator by inspecting the '# fields=' header line."""
    payload = fields_line.split("fields=", 1)[1].strip()
    if "\t" in payload:
        return "\t"
    for sep in ("|", ";", ","):
        if sep in payload:
            return sep
    return ","


def _read_header(path: Path) -> Tuple[str, str, List[str]]:
    """Return (station_name, separator, columns) from file header."""
    station_name: Optional[str] = None
    fields_line: Optional[str] = None
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            if "station_name=" in line:
                station_name = line.strip().split("station_name=")[1]
            if line.startswith("# fields="):
                fields_line = line.strip()
                break
    if fields_line is None:
        raise ValueError(f"Missing '# fields=' header in {path}")
    sep = _detect_separator(fields_line)
    cols = [c.strip() for c in fields_line.split("fields=", 1)[1].split(sep)]
    return station_name or path.stem, sep, cols


# --- Parsing helpers ---

_DATE_FORMATS = (
    "%Y-%m-%d",
    "%d.%m.%Y",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%m-%d-%Y",
    "%Y.%m.%d",
    "%m/%d/%Y",
)


def _parse_date_any(s: str) -> pd.Timestamp:
    """Parse messy date strings (optionally with time appended)."""
    if pd.isna(s):
        return pd.NaT
    s = str(s).strip()
    if " " in s:
        date_part, time_part = s.split(" ", 1)
    else:
        date_part, time_part = s, None
    dt = None
    for fmt in _DATE_FORMATS:
        try:
            dt = datetime.strptime(date_part, fmt)
            break
        except ValueError:
            continue
    if dt is None:
        return pd.NaT
    if time_part:
        m = re.search(r"(\d{1,2}):(\d{2})", time_part)
        if m:
            dt = dt.replace(hour=int(m.group(1)), minute=int(m.group(2)))
    return pd.Timestamp(dt)


def _parse_float_messy(x: object) -> float:
    """Handle decimal commas, unit suffix 'mm', and Latvian word zero 'nulle'."""
    if pd.isna(x):
        return np.nan
    s = str(x).strip()
    if s in NA_TOKENS:
        return np.nan
    if s.lower() in WORD_ZERO:
        return 0.0
    s = s.replace(" mm", "").replace("MM", "mm").replace(",", ".")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else np.nan


def _read_rows_raw(path: Path, sep: str, cols: List[str]) -> pd.DataFrame:
    """Read the body robustly; fix decimal commas in CSV rows and fold overflow into last column."""
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            line = line.rstrip("\n")
            if sep == ",":
                # Replace decimal commas only where they would split numbers
                line = re.sub(r"(?<=\d),(?=\d)", ".", line)
            parts = line.split(sep)
            if len(parts) != len(cols):
                if len(parts) > len(cols):
                    head = parts[: len(cols) - 1]
                    tail = sep.join(parts[len(cols) - 1 :])
                    parts = head + [tail]
                else:
                    parts = parts + [""] * (len(cols) - len(parts))
            rows.append(parts)
    return pd.DataFrame(rows, columns=cols, dtype=str)


# --- Public API ---

def load_one(path: Union[str, Path]) -> pd.DataFrame:
    """
    Load a single messy meteo file into a tidy DataFrame.

    Returns columns (nullable where appropriate):
      station, timestamp, date, time, t_max_c, t_min_c,
      precip_24h_mm, precip_type, present_weather_code, notes
    """
    p = Path(path)
    station_label, sep, cols = _read_header(p)
    raw = _read_rows_raw(p, sep, cols)
    df = raw.replace({v: np.nan for v in NA_TOKENS})

    # Coerce numeric-like fields
    for c in ("t_max_c", "t_min_c", "precip_24h_mm", "present_weather_code"):
        if c in df.columns:
            if c == "precip_24h_mm":
                df[c] = df[c].apply(_parse_float_messy)
            else:
                df[c] = pd.to_numeric(df[c].str.replace(",", ".", regex=False), errors="coerce")

    # Timestamp from 'date'
    if "date" in df.columns:
        df["timestamp"] = df["date"].apply(_parse_date_any)
    else:
        df["timestamp"] = pd.NaT

    # Station label
    df["station"] = station_label

    # Assemble consistent output
    out = pd.DataFrame({k: df[k] if k in df.columns else np.nan for k in KEEP_COLS if k not in ("timestamp","date","time")})
    out["timestamp"] = df["timestamp"]
    out["date"] = pd.to_datetime(out["timestamp"]).dt.date
    out["time"] = pd.to_datetime(out["timestamp"]).dt.time

    # Safe integer cast for codes
    codes = pd.to_numeric(df.get("present_weather_code"), errors="coerce").round()
    out["present_weather_code"] = codes.astype("Int64")

    # Reorder columns to KEEP_COLS
    out = out[[c for c in KEEP_COLS if c in out.columns]]

    return out


def load_all(source: Union[str, Path, Iterable[Union[str, Path]]]) -> pd.DataFrame:
    """
    Load multiple files.
    - If 'source' is a directory, loads all '*.txt' files in it.
    - If 'source' is an iterable, loads those paths in order.
    - If 'source' is a single file path, loads just that file.
    """
    if isinstance(source, (str, Path)):
        p = Path(source)
        if p.is_dir():
            paths = sorted(p.glob("*.txt"))
        else:
            paths = [p]
    else:
        paths = [Path(x) for x in source]

    frames = [load_one(p) for p in paths]
    merged = pd.concat(frames, ignore_index=True)
    merged = merged.dropna(subset=["timestamp"]).sort_values(["station", "timestamp"]).reset_index(drop=True)
    return merged


# --- CLI ---

def _cli():
    ap = argparse.ArgumentParser(description="Load messy Latvian meteo 1925 files into a tidy CSV.")
    ap.add_argument("--dir", type=str, help="Directory with messy .txt files")
    ap.add_argument("--paths", nargs="*", help="Explicit list of file paths")
    ap.add_argument("--out", type=str, required=False, help="Output CSV path (optional)")
    args = ap.parse_args()

    if args.paths:
        src = args.paths
    elif args.dir:
        src = Path(args.dir)
    else:
        ap.error("Provide either --dir or --paths")

    df = load_all(src)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, index=False)
        print(f"Wrote {len(df)} rows to {out_path}")
    else:
        # print small sample to stdout
        print(df.head(20).to_string(index=False))


if __name__ == "__main__":
    _cli()
