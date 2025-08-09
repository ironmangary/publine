import os
import json
from cli.src.new_project import slugify
from core.src.defaults import DEFAULT_CSS
from core.src.social_utils import initialize_links

def create_project_files(title, author, copyright_year):
    """
    Creates the necessary files and directories for a new project.
    """
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
        "cover_image": ""
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

    return slug
