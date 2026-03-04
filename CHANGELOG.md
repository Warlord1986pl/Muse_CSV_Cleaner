# Changelog

All notable changes to this project are documented in this file.

## [1.0.0] - 2026-03-04
### Added
- Initial public repository structure ready for GitHub
- English production CLI for MUSE CSV/Excel cleaning
- Encoding detection + fallback chain (`ISO-8859-1`, `cp1250`, `cp852`, `latin-1`, `utf-8`)
- Snake_case column normalization with duplicate handling
- Empty/whitespace-only column cleanup
- Optional percentage conversion to decimal range
- Validation report generation
- CI workflow and community/project templates

### Validated
- Stress test run on 100 generated CSV variants with 100/100 pass result
