# Contributing

Thank you for your interest in improving Muse CSV Cleaner.

## Development setup
1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Running the tool locally
```bash
python -m muse_csv_cleaner --help
```

## Pull request guidelines
- Keep changes focused and minimal
- Update documentation when behavior changes
- Preserve MUSE-specific scope unless a scope change is discussed first
- Ensure code and user-facing text stay in English

## Commit style (recommended)
- `feat: ...`
- `fix: ...`
- `docs: ...`
- `test: ...`

## Reporting issues
Please use GitHub issue templates and include:
- Input file type (`.csv` / `.xlsx`)
- Operating system
- Python version
- Error output and validation report excerpt
