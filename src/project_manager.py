import os
import json
import argparse
import shutil
from src.builder import create_chapter_page, create_index_page
from src.chapter_utils import list_chapters, add_chapter, edit_chapter, delete_chapter
from src.defaults import DEFAULT_CSS

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

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def ensure_cover_image(prefs_path, prefs, includes_path):
    if not prefs.get("cover_image"):
        print("\n📷 No cover image specified.")
        available = [f for f in os.listdir(includes_path) if f.lower().endswith(('.jpg', '.png'))]
        if available:
            print("Available image files:")
            for img in available:
                print(f"- {img}")
        chosen = input("Enter cover image filename (or leave blank for none): ").strip()
        prefs["cover_image"] = chosen or ""
        save_json(prefs_path, prefs)

def build_html(project_path, prefs, chapters):
    print("\n🛠️ Generating HTML...")
    for ch in chapters:
        create_chapter_page(ch, chapters, prefs, project_path)
    create_index_page(chapters, prefs, project_path)
    public_dir = os.path.join(project_path, "public")
    os.makedirs(public_dir, exist_ok=True)

# Check for styles.css
    style_src = os.path.join(project_path, "includes", "styles.css")
    if not os.path.isfile(style_src):
        print("⚠️  styles.css not found in /includes/")
        choice = input("Create default stylesheet now? [Y/n] ").strip().lower()
        if choice in ("", "y", "yes"):
            with open(style_src, "w", encoding="utf-8") as f:
                f.write(DEFAULT_CSS)  # Make sure DEFAULT_CSS is in scope
            print("✅ Default stylesheet created.")
        else:
            print("🚫 Skipping stylesheet generation.")

# Copy styles.css
    style_dst = os.path.join(public_dir, "styles.css")
    if os.path.isfile(style_src) and not os.path.exists(style_dst):
        shutil.copyfile(style_src, style_dst)

# Copy cover image
    cover_src = os.path.join(project_path, "includes", prefs.get("cover_image", ""))
    cover_dst = os.path.join(public_dir, os.path.basename(cover_src))
    if os.path.isfile(cover_src) and not os.path.exists(cover_dst):
        shutil.copyfile(cover_src, cover_dst)


def build_epub(project_path, prefs, chapters):
    print("📚 EPUB build not implemented yet (stub).\n")

def build_pdf(project_path, prefs, chapters):
    print("🖨️ PDF build not implemented yet (stub).\n")

def manage_projects():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", "-p", help="Project slug name")
    args = parser.parse_args()

    projects = list_projects()
    if not projects:
        print("❌ No projects found in /projects/")
        return

    slug = args.project if args.project in projects else prompt_project(projects)
    project_path = os.path.join("projects", slug)
    prefs_path = os.path.join(project_path, "data", "prefs.json")
    chapters_path = os.path.join(project_path, "data", "chapters.json")
    includes_path = os.path.join(project_path, "includes")
    prefs = load_json(prefs_path)
    story_title = prefs.get("story_title", slug)
    
    while True:
        print(f"\n🔧 Project: {story_title}")
        print("[1] Manage chapters")
        print("[2] Manage preferences (coming soon)")
        print("[3] Publish output")
        print("[4] Back")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            manage_chapters(project_path)
        elif choice == "2":
            print("🛠️ Preferences UI not implemented yet.")
        elif choice == "3":
            prefs = load_json(prefs_path)
            ensure_cover_image(prefs_path, prefs, includes_path)
            chapters = load_json(chapters_path)
            formats = prompt_formats()
            if "html" in formats:
                build_html(project_path, prefs, chapters)
            if "epub" in formats:
                build_epub(project_path, prefs, chapters)
            if "pdf" in formats:
                build_pdf(project_path, prefs, chapters)
            print("\n✅ Publishing complete.")
        elif choice == "4":
            break
        else:
            print("❌ Invalid choice.")

def manage_chapters(project_path):
    while True:
        print("\n📚 Chapter Management")

        chapters = list_chapters(project_path)
        if chapters:
            print("Existing chapters:")
            for ch in chapters:
                num = ch.get("number")
                title = ch.get("title", "<Untitled>")
                print(f"  [{num}] {title}")
        else:
            print("No chapters yet.")

        print("\nOptions:")
        print("[1] Add a new chapter")
        print("[2] Edit a chapter entry")
        print("[3] Delete a chapter")
        print("[4] Back")

        choice = input("Select an option: ").strip()

        if choice == "1":
            add_chapter(project_path)
        elif choice == "2":
            edit_chapter(project_path, chapters)
        elif choice == "3":
            delete_chapter(project_path, chapters)
        elif choice == "4":
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
