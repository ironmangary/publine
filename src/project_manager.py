import os
import json
import argparse
from src.paths import socials_path
from src.utils import load_json, save_json, load_prefs, save_prefs
from src.chapter_utils import ensure_cover_image
from src.html_output import choose_html_layout_features, build_html, create_html_chapter_page, create_html_index_page
from src.epub_output import build_epub
from src.pdf_output import build_pdf
from src.chapters import manage_chapters
from src.licenses import load_license_definitions, save_license_definitions, choose_license
from src.social import choose_follow_links
from src.sharing import choose_share_links

def list_projects():
    base = "projects"
    return [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]

def prompt_project(slugs):
    print("\n🗂️ Available Projects:")
    for i, slug in enumerate(slugs):
        prefs_path = os.path.join("projects", slug, "data", "prefs.json")
        title = slug
        if os.path.exists(prefs_path):
            try:
                with open(prefs_path, "r", encoding="utf-8") as f:
                    prefs = json.load(f)
                    title = prefs.get("story_title", slug)
            except:
                pass  # fallback to slug if prefs missing

        print(f"[{i + 1}] {title} ({slug})")

    while True:
        choice = input("Select a project: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(slugs):
            return slugs[int(choice) - 1]
        print("❌ Invalid choice.")

def prompt_formats():
    print("\n📦 What would you like to publish?")
    print("[1] Static HTML")
    print("[2] EPUB (stub)")
    print("[3] PDF (stub)")
    choice = input("Enter numbers separated by commas: ").strip()
    selected = []
    for item in choice.split(','):
        item = item.strip()
        if item == '1': selected.append("html")
        elif item == '2': selected.append("epub")
        elif item == '3': selected.append("pdf")
    return selected

def manage_projects():
    licenses_path = os.path.join(os.path.dirname(__file__), "..", "data", "licenses.json")
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", "-p", help="Project slug name")
    args = parser.parse_args()

    projects = list_projects()
    if not projects:
        print("❌ No projects found in /projects/")
        return

    slug = args.project if args.project in projects else prompt_project(projects)
    project_path = os.path.join("projects", slug)
    includes_path = os.path.join(project_path, "includes")
    prefs = load_prefs(project_path)
    story_title = prefs.get("story_title", slug)
    
    while True:
        print(f"""
🔧 Project: {story_title}
[1] Manage chapters
[2] Manage preferences (coming soon)
[3] Manage Social Media Accounts
[4] Manage Sharing Links
[5] Choose Project License
[6] Customize HTML Layout
[7] Publish output
[8] Back
        """)
        choice = input("Choose an option: ").strip()

        if choice == "1": # Manage Chapters
            manage_chapters(project_path)
        elif choice == "2": # Manage Preferences
            print("🛠️ Preferences UI not implemented yet.")
        elif choice == "3": # Manage Social Media Accounts
            choose_follow_links(project_path, socials_path)
        elif choice == "4": # Manage Social Media Accounts
            choose_share_links(project_path, socials_path)
        elif choice == "5": # Choose License
            chosen = choose_license(licenses_path)
            if chosen:
                prefs["license"] = chosen
                save_prefs(prefs_path, prefs)
                name = chosen["short_name"] if isinstance(chosen, dict) else chosen
                print(f"\n✔️  License updated to: {name}")
            else:
                print("\n⚠️  License update canceled or invalid.")
        elif choice == "6": # Customize HTML Page Layout
            choose_html_layout_features(project_path)
        elif choice == "7": # Publish Output
            prefs = load_prefs(project_path)
            ensure_cover_image(project_path, includes_path)
            chapters = load_json(project_path, "chapters.json")
            formats = prompt_formats()
            if "html" in formats:
                build_html(project_path, prefs, chapters)
            if "epub" in formats:
                build_epub(project_path)
            if "pdf" in formats:
                build_pdf(project_path)
            print("\n✅ Publishing complete.")
        elif choice == "8": # Back
            break
        else:
            print("❌ Invalid choice.")


if __name__ == "__main__":
    manage_projects()
