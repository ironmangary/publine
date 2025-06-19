import os
import json
import re
from src.defaults import DEFAULT_CSS

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
    use_titles = prompt_bool("Use chapter titles?")

    slug = slugify(title)
    base_path = os.path.join("projects", slug)
    data_dir = os.path.join(base_path, "data")
    includes_dir = os.path.join(base_path, "includes")
    public_dir = os.path.join(base_path, "public")

    for path in [data_dir, includes_dir, public_dir]:
        os.makedirs(path, exist_ok=True)

    prefs = {
        "story_title": title,
        "story_author": author,
        "copyright": copyright_year,
        "use_chapter_titles": use_titles,
        "cover_image": ""
    }

    with open(os.path.join(data_dir, "prefs.json"), "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=4)

    with open(os.path.join(data_dir, "chapters.json"), "w", encoding="utf-8") as f:
        json.dump([], f, indent=4)

    with open(os.path.join(base_path, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\nProject scaffolded with Publine.\n\nAuthor: {author}\nCopyright © {copyright_year}")

    with open(os.path.join(includes_dir, "chapter_0.html"), "w", encoding="utf-8") as f:
        f.write("<!-- Begin writing Chapter 0 here -->\n")

    with open(os.path.join(includes_dir, "styles.css"), "w", encoding="utf-8") as f:
        f.write(DEFAULT_CSS)

    print(f"\n✅ Project '{title}' created at: {base_path}")
    print("📄 Includes starter prefs, chapters, styles, and chapter_0.html\n")

if __name__ == "__main__":
    create_project()
