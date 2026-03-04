# Architecture

## Core module
- `src/muse_csv_cleaner/cli.py`
  - Input handling (CLI + optional GUI)
  - Encoding detection and fallback
  - Header detection heuristic
  - Cleaning pipeline
  - Export and validation reporting

## Cleaning pipeline
1. Validate file presence and size
2. Load CSV/Excel
3. Remove empty and whitespace-only columns
4. Remove index-like first column when applicable
5. Normalize column names to snake_case
6. Optional percentage conversion
7. Export to XLSX and write run report

## Design choices
- MUSE-specific scope for predictable behavior
- Fail-fast on invalid input (missing or empty files)
- Reports stored per run for reproducibility
