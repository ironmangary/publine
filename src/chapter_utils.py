import os
import json
from src.importer import import_content

def get_chapters_path(project_path):
    return os.path.join(project_path, "data", "chapters.json")

def get_includes_path(project_path):
    return os.path.join(project_path, "includes")

def load_chapters(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_chapters(path, chapters):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chapters, f, indent=4)

def list_chapters(project_path):
    path = get_chapters_path(project_path)
    return sorted(load_chapters(path), key=lambda ch: ch.get("number", 0))

def add_chapter(project_path):
    print("\n➕ Add Chapter")
    chapters_path = get_chapters_path(project_path)
    includes_path = get_includes_path(project_path)

    chapters = load_chapters(chapters_path)

    try:
        number = int(input("Chapter number: ").strip())
        if any(ch["number"] == number for ch in chapters):
            print("❌ That chapter number already exists.")
            return
    except ValueError:
        print("❌ Invalid number.")
        return

    title = input("Title: ").strip()
    discussion = input("Discussion link (optional): ").strip()

    print("Choose import format:")
    print("[1] HTML")
    print("[2] Plaintext (.txt)")
    print("[3] Word (.docx)")
    fmt_choice = input("Format: ").strip()
    import_format = {"1": "html", "2": "txt", "3": "docx"}.get(fmt_choice, "html")

    import_source = input("Path to chapter file (leave blank to create empty): ").strip()
    if import_source and not os.path.isabs(import_source):
        import_source = os.path.join(includes_path, import_source)

    filename = f"chapter_{number}.html"
    output_path = os.path.join(includes_path, filename)

    if import_source:
        try:
            html = import_content(import_source, import_format)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("")  # blank file

    chapters.append({
        "number": number,
        "title": title,
        "discussion": discussion,
        "import_source": f"includes/{filename}",
        "import_format": import_format,
        "exclude_from_epub": False,
        "exclude_from_pdf": False,
        "draft": False
    })

    save_chapters(chapters_path, chapters)
    print("✅ Chapter added.")

def edit_chapter(project_path, chapters):
    try:
        chnum = int(input("Enter chapter number to edit: ").strip())
    except ValueError:
        print("❌ Invalid number.")
        return

    chapter = next((c for c in chapters if c["number"] == chnum), None)
    if not chapter:
        print("❌ Chapter not found.")
        return

    print(f"Editing Chapter [{chnum}] {chapter['title']}")
    for field in ["title", "discussion", "import_source", "import_format"]:
        val = input(f"{field} ({chapter.get(field, '')}): ").strip()
        if val: chapter[field] = val

    for flag in ["exclude_from_epub", "exclude_from_pdf", "draft"]:
        val = input(f"{flag}? (y/N): ").lower().strip()
        chapter[flag] = val == "y"

    save_chapters(get_chapters_path(project_path), chapters)
    print("✅ Chapter updated.")

def delete_chapter(project_path, chapters):
    try:
        chnum = int(input("Enter chapter number to delete: ").strip())
    except ValueError:
        print("❌ Invalid number.")
        return

    chapter = next((c for c in chapters if c["number"] == chnum), None)
    if not chapter:
        print("❌ Chapter not found.")
        return

    confirm = input(f"Are you sure you want to delete chapter {chnum} ({chapter['title']})? (y/N): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    # Delete the include file?
    frag = os.path.join(project_path, chapter["import_source"])
    if os.path.exists(frag):
        if input(f"Also delete HTML file ({frag})? (y/N): ").strip().lower() == "y":
            os.remove(frag)
            print("🗑️ Fragment deleted.")

    chapters.remove(chapter)
    save_chapters(get_chapters_path(project_path), chapters)
    print("✅ Chapter removed.")

