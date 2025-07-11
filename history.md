# Publine

## Detaileddevelopment history

## v1.0 Alpha 4 (2025-07-11)

This release marks the final major feature milestone before GUI and AI planning begins.

- **Added EPUB export**: Generates a complete book with TOC to `public/downloads`
- **Added PDF export**: Creates per-chapter PDFs using ReportLab with clean formatting
- **Refactored I/O utilities**: Unified project data access using `load_prefs`, `save_prefs`, `load_json`, and `save_json`
- **Improved file organization**: All output files now save to their project-specific `downloads` directory

## v1.0 Alpha 3 (2025-06-28)
- Added interactive menus to customize static HTML page headers and footers
- Refactored layout preferences into `display_features` for modular control
- Fixed `KeyError` related to missing `use_chapter_titles` in prefs
- Improved `save_prefs()` to handle missing arguments gracefully
- Introduced `reset_prefs.py` for clean project preference resets

## v1.0 Alpha 2 (2025-06-24)
- Implemented license manager for Creative Commons and custom licenses
- Added social media account manager for footer links
- Created sharing links manager for per-chapter discussion and share buttons

### v1.0 Alpha 1 – Initial Commit (2025-06-19)

- Project structure initialized 
- Basic HTML + EPUB generation
- Chapter navigation system
- Style creation + asset copying
