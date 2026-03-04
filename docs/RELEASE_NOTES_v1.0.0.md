# Muse CSV Cleaner v1.0.0

Initial public release of **Muse CSV Cleaner**.

## Highlights
- Production-ready English CLI for cleaning MUSE cytometer exports (`.csv`, `.xlsx`, `.xls`)
- Automatic encoding detection with fallback strategy
- Automatic MUSE header-line detection
- Column normalization to Python-friendly `snake_case`
- Cleanup of empty and whitespace-only columns
- Optional percentage conversion to decimal range (`--convert-percent`)
- Validation report generation for each run

## Reliability and validation
- Real-file validation completed on MUSE export:
  - `DRISIPHILA 19-03-2024.ROS.CSV`
  - Successful conversion and report generation
- Stress validation completed on 100 generated CSV variants:
  - Mixed encodings and delimiters
  - Final pass rate: **100/100**
- CLI smoke test completed (`python -m muse_csv_cleaner --help`)

## Project assets included
- Full GitHub-ready repository layout
- CI workflow (`.github/workflows/python-ci.yml`)
- Issue templates and PR template
- `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `LICENSE`

## Install
```bash
pip install -r requirements.txt
pip install -e .
```

## Run
```bash
python -m muse_csv_cleaner "input.csv" --convert-percent
```
