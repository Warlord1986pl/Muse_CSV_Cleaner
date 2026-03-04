from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

import chardet
import pandas as pd
import tkinter as tk
from tkinter import filedialog


def detect_encoding(file_path: str | Path) -> str:
    """Detect file encoding using chardet."""
    try:
        with open(file_path, "rb") as handle:
            sample = handle.read(10_000)
        detected = chardet.detect(sample)
        return detected.get("encoding", "utf-8") or "utf-8"
    except Exception:
        return "utf-8"


def find_header_line(file_path: str | Path, encoding: str) -> int:
    """
    Find the most likely header line for MUSE CSV files.

    MUSE exports often include a group-header row before the actual
    data-header row. If one of the target keywords is found, the function
    returns the previous line index when possible.
    """
    keywords = ["Sample No", "Sample ID", "Sample Name"]
    try:
        with open(file_path, "r", encoding=encoding, errors="replace") as handle:
            lines = handle.readlines()

        for index, line in enumerate(lines):
            if any(keyword in line for keyword in keywords):
                return index - 1 if index > 0 else index

        for index, line in enumerate(lines):
            if line.count(",") > 15:
                return index
    except Exception:
        pass

    return 0


def _to_snake_case(column_name: str) -> str:
    name = str(column_name).strip()

    name = name.replace("Cells/µL", "cells_per_ul")
    name = name.replace("cells/µL", "cells_per_ul")
    name = re.sub(r"([a-zA-Z0-9])\(", r"\1_", name)

    replacements = [
        ("(+)", "positive"),
        ("(-)", "negative"),
        (" % ", "_percent_"),
        ("% ", "percent_"),
        (" %", "percent"),
        ("%", "percent"),
        (" / ", "_per_"),
        ("/", "_per_"),
        ("(", ""),
        (")", ""),
        ("mL", "_ml"),
        ("µL", "_ul"),
        ("µ", "u"),
        ("+", "plus"),
        (" - ", "_minus_"),
        ("-", "_"),
        (",", ""),
    ]

    for old, new in replacements:
        name = name.replace(old, new)

    name = name.lower().replace(" ", "_")
    name = re.sub(r"[^\w]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name


def normalize_column_names(df: pd.DataFrame, report_lines: list[str]) -> tuple[pd.DataFrame, list[str]]:
    """Normalize column names to snake_case and deduplicate collisions."""
    original_columns = list(df.columns)
    normalized = [_to_snake_case(column) for column in df.columns]

    deduplicated: list[str] = []
    counts: dict[str, int] = {}
    for column in normalized:
        if column in counts:
            counts[column] += 1
            deduplicated.append(f"{column}_{counts[column]}")
        else:
            counts[column] = 0
            deduplicated.append(column)

    df.columns = deduplicated

    report_lines.append("Normalized column names to snake_case.")
    preview_count = min(5, len(original_columns))
    for old, new in zip(original_columns[:preview_count], deduplicated[:preview_count]):
        report_lines.append(f"  {old!r} -> {new!r}")
    if len(original_columns) > preview_count:
        report_lines.append(f"  ... and {len(original_columns) - preview_count} more columns")

    return df, report_lines


def clean_muse_file(df: pd.DataFrame, report_lines: list[str]) -> tuple[pd.DataFrame, list[str]]:
    """Apply MUSE-specific cleaning rules."""
    df = df.dropna(axis=1, how="all")

    empty_columns = [
        column
        for column in df.columns
        if df[column].isna().all() or (df[column] == "").all()
    ]
    if empty_columns:
        df = df.drop(columns=empty_columns)
        report_lines.append(f"Removed {len(empty_columns)} fully empty column(s): {empty_columns}")

    whitespace_only_columns = [
        column
        for column in df.columns
        if all(pd.isna(value) or str(value).strip() == "" for value in df[column])
    ]
    if whitespace_only_columns:
        df = df.drop(columns=whitespace_only_columns)
        report_lines.append(
            f"Removed {len(whitespace_only_columns)} whitespace-only column(s): {whitespace_only_columns}"
        )

    if len(df.columns) > 0:
        first_column = df.columns[0]
        try:
            is_numeric = pd.to_numeric(df[first_column], errors="coerce").notna().all()
            is_empty = df[first_column].isna().all() or (df[first_column] == "").all()
            if is_numeric or is_empty:
                df = df.drop(columns=[first_column])
                report_lines.append(f"Removed first column {first_column!r} (index/empty).")
            else:
                report_lines.append(f"Kept first column {first_column!r}.")
        except Exception as exc:
            report_lines.append(f"Warning: could not evaluate first column {first_column!r}: {exc}")

    df.columns = df.columns.str.strip()
    report_lines.append("Trimmed whitespace from column headers.")

    df, report_lines = normalize_column_names(df, report_lines)

    sample_columns = [column for column in df.columns if "sample" in column.lower()]
    for column in sample_columns:
        df[column] = df[column].astype(str).str.rstrip()
        report_lines.append(f"Trimmed trailing whitespace in sample column {column!r}.")

    return df, report_lines


def convert_percent_to_decimal(df: pd.DataFrame, report_lines: list[str]) -> tuple[pd.DataFrame, list[str]]:
    """Convert percentage columns to decimal values in the 0-1 range."""
    converted: list[str] = []

    for column in df.columns:
        if ("%" in column) or column.startswith("percent_") or ("_percent_" in column):
            try:
                numeric_series = pd.to_numeric(df[column].astype(str).str.strip(), errors="coerce")
                if numeric_series.notna().any() and numeric_series.max() > 1:
                    df[column] = numeric_series / 100
                    converted.append(column)
            except Exception:
                continue

    if converted:
        report_lines.append(f"Converted {len(converted)} percentage column(s): {converted[:5]}")
    else:
        report_lines.append("No percentage conversion needed (already in 0-1 or no matching columns).")

    return df, report_lines


def _select_files_with_gui() -> tuple[str | None, str | None]:
    root = tk.Tk()
    root.withdraw()

    input_path = filedialog.askopenfilename(
        title="Select MUSE input file",
        filetypes=[
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx *.xls"),
            ("All files", "*.*"),
        ],
    )

    if not input_path:
        root.destroy()
        return None, None

    output_path = filedialog.asksaveasfilename(
        title="Save cleaned file as",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        initialfile=f"{Path(input_path).stem}_cleaned.xlsx",
    )

    root.destroy()
    return input_path, output_path or None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean and normalize MUSE cytometer files (CSV/Excel).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  muse-csv-cleaner\n"
            "  muse-csv-cleaner sample.csv\n"
            "  muse-csv-cleaner sample.csv --convert-percent\n"
            "  muse-csv-cleaner sample.csv -o cleaned.xlsx"
        ),
    )
    parser.add_argument("input", nargs="?", help="Input CSV/Excel file path. If omitted, GUI mode is used.")
    parser.add_argument("--output", "-o", help="Output .xlsx path")
    parser.add_argument("--convert-percent", action="store_true", help="Convert percentage columns to decimal values")

    args = parser.parse_args()

    if not args.input:
        selected_input, selected_output = _select_files_with_gui()
        if not selected_input:
            print("No file selected. Exiting.")
            sys.exit(1)
        args.input = selected_input
        if selected_output:
            args.output = selected_output

    script_dir = Path(__file__).resolve().parent.parent.parent
    outputs_dir = script_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = outputs_dir / f"validation_report_{timestamp}.txt"
    report_lines: list[str] = []

    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(errors="replace")
    except Exception:
        pass

    def log(message: str) -> None:
        text = str(message)
        try:
            print(text)
        except UnicodeEncodeError:
            encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
            safe_text = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
            print(safe_text)
        report_lines.append(text)

    file_path = Path(args.input)
    if not file_path.is_file():
        log(f"ERROR: File does not exist: {file_path}")
        sys.exit(1)

    file_size = file_path.stat().st_size
    if file_size == 0:
        log("ERROR: Input file is empty (0 bytes).")
        sys.exit(1)

    log("=" * 70)
    log("MUSE CSV CLEANER")
    log("=" * 70)
    log(f"Input file: {file_path}")
    log(f"File size: {file_size / 1024 / 1024:.2f} MB")

    extension = file_path.suffix.lower()

    try:
        if extension in {".xlsx", ".xls"}:
            log("Detected format: Excel")
            df = pd.read_excel(file_path, dtype=str)
            report_lines.append("Format: Excel")
        elif extension == ".csv":
            log("Detected format: CSV")
            encoding = detect_encoding(file_path)
            header_line = find_header_line(file_path, encoding)
            log(f"Detected encoding: {encoding}")
            log(f"Detected header line: {header_line + 1}")

            fallback_encodings = ["ISO-8859-1", "cp1250", "cp852", "latin-1", "utf-8"]
            tried = [encoding]
            df = None

            try:
                df = pd.read_csv(file_path, dtype=str, encoding=encoding, header=header_line)
                report_lines.append(f"Format: CSV | Encoding: {encoding} | Header line: {header_line + 1}")
            except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as exc:
                log(f"Primary read failed ({encoding}): {exc}")
                for fallback in fallback_encodings:
                    if fallback.lower() == encoding.lower():
                        continue
                    tried.append(fallback)
                    try:
                        fallback_header_line = find_header_line(file_path, fallback)
                        df = pd.read_csv(file_path, dtype=str, encoding=fallback, header=fallback_header_line)
                        log(f"Recovered with fallback encoding: {fallback}")
                        report_lines.append(
                            f"Format: CSV | Encoding: {fallback} (fallback) | Header line: {fallback_header_line + 1}"
                        )
                        break
                    except Exception:
                        continue

                if df is None:
                    raise RuntimeError(f"Could not parse CSV with any encoding. Tried: {', '.join(tried)}")
        else:
            log(f"ERROR: Unsupported file extension: {extension}")
            sys.exit(1)
    except Exception as exc:
        log(f"ERROR while reading file: {exc}")
        sys.exit(1)

    log(f"Original shape: {df.shape[0]} rows x {df.shape[1]} columns")

    df, report_lines = clean_muse_file(df, report_lines)

    if args.convert_percent:
        df, report_lines = convert_percent_to_decimal(df, report_lines)

    log(f"Cleaned shape: {df.shape[0]} rows x {df.shape[1]} columns")

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = outputs_dir / f"{file_path.stem}_cleaned_{timestamp}.xlsx"

    try:
        df.to_excel(output_path, index=False, engine="openpyxl")
        log(f"Output saved: {output_path}")
    except Exception as exc:
        log(f"ERROR while saving output: {exc}")
        sys.exit(1)

    try:
        report_path.write_text("\n".join(report_lines), encoding="utf-8")
        log(f"Validation report saved: {report_path}")
    except Exception as exc:
        log(f"WARNING: Could not write report file: {exc}")


if __name__ == "__main__":
    main()
