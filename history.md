# Publine

## Detaileddevelopment history

## v1.0 Alpha 5 (2025-07-29)

This release marks the end of Publine CLI development. I will start development of a web UI and AI integrated features starting with v1.0 Alpha 6.

Moving forward, I will be switching to using multiple branches.

- main (the latest stable code)
- dev (The version under development)
- v1_alpha5 (An archive of this release, just in case)\

- Finished the processes to build PDF and EPUB files.
- Replaced *follow_links.json* and *share_links.json* with unified **links.json** structure at the project level.
- Created **social_utils.py** to encapsulate access and modification:
  - *load_follow_links()* / *save_follow_links()*
  - *load_share_links()* / *save_share_links()*
  - *initialize_links()* to scaffold `links.json` during project creation
- Updated *html_footer()* to load link data internally via *project_path*
- Adjusted *create_project()* to call *initialize_links()*
- Fixed a bug in **chapter_utils.py** that was preventing the importing of Word files

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
