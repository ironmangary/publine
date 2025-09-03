import os
import json
import re
from core.src.defaults import DEFAULT_CSS
from core.src.social_utils import initialize_links

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s_]+', '-', text).strip('-')

def prompt_bool(prompt):
    while True:
        choice = input(f"{prompt} (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False

def create_project():
    print("📚 Welcome to Publine Project Setup\n")

    title = input("Project title: ").strip()
    author = input("Author name: ").strip()
    copyright_year = input("Copyright year: ").strip()

    slug = slugify(title)
    project_path = os.path.join("projects", slug)
    data_dir = os.path.join(project_path, "data")
    includes_dir = os.path.join(project_path, "includes")
    public_dir = os.path.join(project_path, "public")
    initialize_links(project_path)

    for path in [data_dir, includes_dir, public_dir]:
        os.makedirs(path, exist_ok=True)

    prefs = {
        "story_title": title,
        "story_author": author,
        "copyright": copyright_year,
        "cover_image": "",
        "pdf_enabled": False
    }

    with open(os.path.join(data_dir, "prefs.json"), "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=4)

    with open(os.path.join(data_dir, "chapters.json"), "w", encoding="utf-8") as f:
        json.dump([], f, indent=4)

    with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\nProject scaffolded with Publine.\n\nAuthor: {author}\nCopyright © {copyright_year}")

    with open(os.path.join(includes_dir, "chapter_0.html"), "w", encoding="utf-8") as f:
        f.write("<!-- Begin writing Chapter 0 here -->\n")

    with open(os.path.join(includes_dir, "styles.css"), "w", encoding="utf-8") as f:
        f.write(DEFAULT_CSS)

    print(f"\n✅ Project '{title}' created at: {project_path}")
    print("📄 Includes starter prefs, chapters, styles, and chapter_0.html\n")

if __name__ == "__main__":
    create_project()
