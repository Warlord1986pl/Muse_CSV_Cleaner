# GitHub Release Copy (v1.0.0)

## Release title
`Muse CSV Cleaner v1.0.0`

## Release notes (copy-paste)
Initial public release of **Muse CSV Cleaner** — a production-ready Python CLI for cleaning and normalizing MUSE cytometer exports.

### Highlights
- English CLI for MUSE `.csv`, `.xlsx`, `.xls`
- Automatic encoding detection + fallback strategy
- MUSE header-line auto-detection
- Column normalization to `snake_case`
- Empty/whitespace-only column cleanup
- Optional percent-to-decimal conversion (`--convert-percent`)
- Validation report generated for each run

### Validation
- Real MUSE file conversion validated end-to-end:
  - `DRISIPHILA 19-03-2024.ROS.CSV`
- Stress-tested on 100 generated CSV variants:
  - mixed encodings and delimiters
  - final pass rate: **100/100**
- CLI smoke test passed:
  - `python -m muse_csv_cleaner --help`

### Project assets
- CI workflow
- Issue templates and PR template
- Contributing, Security, Changelog, License

### Install
```bash
pip install -r requirements.txt
pip install -e .
```

### Run
```bash
python -m muse_csv_cleaner "input.csv" --convert-percent
```
