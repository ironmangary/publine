# Publine TODO

## 🔧 In Progress
- [ ] Build out "Manage Preferences" menu for editing prefs.json interactively
- [ ] Add EPUB file builder module
- [ ] Add PDF file builder module
- [ ] Integrate AI features (e.g. chapter summaries, metadata generation)
- [ ] Begin GUI development using PyWebView

## 🧠 Ideas / Backlog
- [ ] Add `publine reset-prefs` CLI command
- [ ] Implement `publine log` to view project history from CLI
- [ ] Add theme manager for HTML output (light/dark/custom)
- [ ] Support per-chapter license overrides
- [ ] Add CLI wizard for new project setup with optional prompts
- [ ] Allow per-chapter discussion toggle via CLI
- [ ] Add schema validation for prefs.json and chapter.json
- [ ] Add preview server for HTML output (`publine preview`)
- [ ] Enable publishing to platforms like ScribbleHub or personal blogs

## 🐞 Bugs / Fixes
- [ ] Fix inconsistent EPUB/PDF link rendering in HTML output
- [ ] Warn if required keys are missing from prefs.json
- [ ] Improve error handling for malformed or missing JSON files
- [ ] Ensure `display_features` always includes all expected keys

## ✅ Done (Alpha 3)
- [x] Created interactive layout customization menu
- [x] Moved `use_chapter_titles` into `display_features`
- [x] Added `reset_prefs.py` for clean project resets
- [x] Fixed `save_prefs()` argument mismatch
- [x] Cleaned up prefs.json structure and defaults
