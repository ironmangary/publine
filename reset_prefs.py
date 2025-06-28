import json
from pathlib import Path
import shutil
import sys

def reset_prefs(project_dir):
    project_path = Path(project_dir)
    prefs_path = project_path / "prefs.json"

    if not project_path.exists():
        print(f"Error: Project directory '{project_dir}' does not exist.")
        return

    # Backup existing prefs
    if prefs_path.exists():
        backup_path = prefs_path.with_suffix(".bak.json")
        shutil.copy(prefs_path, backup_path)
        print(f"Backed up existing prefs to {backup_path}")

    # Load existing prefs if available
    existing = {}
    if prefs_path.exists():
        try:
            with open(prefs_path) as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            print("Warning: prefs.json is invalid. Starting fresh.")

    # Define clean defaults
    clean_prefs = {
        "story_title": existing.get("story_title", "Untitled Story"),
        "story_author": existing.get("story_author", "Anonymous"),
        "copyright": existing.get("copyright", "2025"),
        "license": existing.get("license", "CC-BY-NC-SA-4.0"),
        "display_features": {
            "use_chapter_titles": True,
            "cover_image": True,
            "chapter_nav_top": True,
            "epub_link": False,
            "pdf_link": False,
            "share_links": True,
            "discuss_link": True,
            "chapter_nav_bottom": True,
            "social_links": True,
            "copyright": True,
            "license": True
        }
    }

    # Save clean prefs
    with open(prefs_path, "w") as f:
        json.dump(clean_prefs, f, indent=2)
    print(f"Clean prefs.json written to {prefs_path}")

# Example usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reset_prefs.py /path/to/project")
    else:
        reset_prefs(sys.argv[1])
