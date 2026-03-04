# Usage Guide

## Input formats
- CSV (`.csv`)
- Excel (`.xlsx`, `.xls`)

## Typical command
```bash
python -m muse_csv_cleaner input.csv --convert-percent -o cleaned.xlsx
```

## Processing steps
1. File validation (exists, non-empty)
2. Format detection
3. CSV encoding detection with fallback
4. Header-line detection (MUSE heuristic)
5. Cleaning and column normalization
6. Optional percentage conversion
7. Excel export + validation report

## Validation report
Each run writes a report to `outputs/` with:
- detected format/encoding/header
- columns removed
- normalization preview
- output file path

## Validation tests executed
- Real-file validation on a production MUSE CSV export (successful conversion and report generation)
- Stress validation on 100 generated CSV files across multiple encodings and delimiters (`100/100` pass)
- CLI smoke validation (`--help`) to confirm entrypoint and parameter handling
