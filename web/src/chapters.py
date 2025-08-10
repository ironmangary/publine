import os
from flask import flash
from core.src.utils import load_prefs
from web.src import chapter_utils # Assuming chapter_utils is in web/src now

PROJECTS_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'projects'))

def get_project_path(slug):
    """Constructs the full path to a project directory."""
    return os.path.join(PROJECTS_BASE_DIR, slug)

def get_project_details(slug):
    """Loads project preferences for display."""
    project_path = get_project_path(slug)
    try:
        prefs = load_prefs(project_path)
        prefs['slug'] = slug # Add slug for URL generation
        return prefs
    except FileNotFoundError:
        return None

def get_chapters_data(slug):
    """Loads and returns sorted chapters for a given project slug."""
    project_path = get_project_path(slug)
    return chapter_utils.list_chapters(project_path)

def process_add_chapter(slug, form_data, uploaded_file):
    """Processes the form submission for adding a chapter."""
    project_path = get_project_path(slug)
    try:
        number = int(form_data.get("number"))
    except (ValueError, TypeError):
        flash("Invalid chapter number.", "error")
        return False

    title = form_data.get("title", "").strip()
    discussion = form_data.get("discussion", "").strip()
    import_format = form_data.get("import_format", "html")

    if not title:
        flash("Chapter title cannot be empty.", "error")
        return False

    success, message = chapter_utils.add_chapter(
        project_path, number, title, discussion, import_format, uploaded_file
    )
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    return success

def process_edit_chapter(slug, chapter_num, form_data, uploaded_file):
    """Processes the form submission for editing a chapter."""
    project_path = get_project_path(slug)

    new_title = form_data.get("title", "").strip()
    new_discussion = form_data.get("discussion", "").strip()
    new_import_format = form_data.get("import_format", "html")
    new_exclude_epub = 'exclude_from_epub' in form_data
    new_exclude_pdf = 'exclude_from_pdf' in form_data
    new_draft = 'draft' in form_data

    if not new_title:
        flash("Chapter title cannot be empty.", "error")
        return False

    success, message = chapter_utils.edit_chapter(
        project_path, chapter_num, new_title, new_discussion, new_import_format,
        new_exclude_epub, new_exclude_pdf, new_draft, uploaded_file
    )
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    return success

def process_delete_chapter(slug, chapter_num):
    """Processes the request for deleting a chapter."""
    project_path = get_project_path(slug)
    # For simplicity, we'll assume confirming 'yes' via the form submission for file deletion.
    # A more robust solution might ask explicitly or have a checkbox on the form.
    delete_file_confirm = True 
    success, message = chapter_utils.delete_chapter(project_path, chapter_num, delete_file_confirm)
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    return success

def get_single_chapter_data(slug, chapter_num):
    """Retrieves data for a single chapter."""
    chapters = get_chapters_data(slug)
    for chapter in chapters:
        if chapter['number'] == chapter_num:
            return chapter
    return None
