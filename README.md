# Muse CSV Cleaner

Production-ready Python tool for cleaning and normalizing MUSE cytometer exports (CSV/Excel) into analysis-ready XLSX files.

## Key features
- Automatic CSV encoding detection with fallback strategy
- Automatic header-line detection for MUSE-formatted files
- MUSE-focused cleaning rules (empty/whitespace columns, index-like first column)
- Column normalization to Python-friendly `snake_case`
- Optional percentage-to-decimal conversion (`98.7` -> `0.987`)
- Robust Windows-safe logging (codepage tolerant)
- CLI mode and optional GUI file picker mode

## Project status
- Stable and ready for GitHub publication
- Stress-tested on 100 generated CSV variants (pass rate: 100/100)

## Validation testing performed
- End-to-end run on a real MUSE export:
  - input: `DRISIPHILA 19-03-2024.ROS.CSV`
  - detected encoding: `ISO-8859-1`
  - result: `143 x 36` -> `143 x 34`, output saved successfully
  - report file generated in `outputs/validation_report_*.txt`
- Stress test on 100 generated CSV variants:
  - mixed encodings (`utf-8`, `utf-16`, `utf-8-sig`, `ISO-8859-1`, `cp1250`, `cp852`)
  - mixed delimiters (`,`, `;`, `tab`, `|`, `space`, `~`)
  - final result: `100/100` successful conversions
- CLI smoke test:
  - verified command entrypoint and argument parsing with `python -m muse_csv_cleaner --help`

## Installation
```bash
pip install -r requirements.txt
```

Optional editable install (adds `muse-csv-cleaner` command):
```bash
pip install -e .
```

## Quick start
### CLI mode
```bash
python -m muse_csv_cleaner "path/to/input.csv"
python -m muse_csv_cleaner "path/to/input.csv" --convert-percent
python -m muse_csv_cleaner "path/to/input.csv" -o "path/to/output.xlsx"
```

### Installed command mode
```bash
muse-csv-cleaner "path/to/input.csv" --convert-percent
```

### GUI mode
```bash
python -m muse_csv_cleaner
```
When no input path is provided, file dialogs are used.

## Output
- Cleaned workbook: `outputs/*_cleaned_YYYYMMDD_HHMMSS.xlsx`
- Validation report: `outputs/validation_report_YYYYMMDD_HHMMSS.txt`

## Column normalization examples
- `Cells/µL` -> `cells_per_ul`
- `% ROS(+) Cells (M2)` -> `percent_ros_positive_cells_m2`
- Duplicate names are deduplicated with suffixes (`_1`, `_2`, ...)

## Scope and limitations
This project is intentionally **MUSE-specific**. It is not designed as a universal CSV cleaner for all cytometry platforms.

Known heuristic limitations:
- Header-line detection is based on MUSE patterns (`Sample No`, high delimiter density)
- Extremely unusual exports may require manual review of generated report

## Repository structure
```text
Muse_CSV_Cleaner/
  .github/
    ISSUE_TEMPLATE/
    workflows/
  docs/
  src/muse_csv_cleaner/
  tests/
  LICENSE
  README.md
  pyproject.toml
  requirements.txt
```

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security
See [SECURITY.md](SECURITY.md).

## License
MIT — see [LICENSE](LICENSE).
