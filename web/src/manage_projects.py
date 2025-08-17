import os
import json
import shutil
from werkzeug.utils import secure_filename # Import secure_filename
from core.src.utils import load_prefs, save_prefs
from web.src.chapter_utils import get_includes_path # Import get_includes_path

# Base directory for projects, assuming this module is in web/src
PROJECTS_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'projects'))

def get_project_path(slug):
    """Constructs the full path to a project directory."""
    return os.path.join(PROJECTS_BASE_DIR, slug)

def get_projects_list():
    """
    Returns a list of dictionaries for each project,
    containing slug, title, and author.
    """
    projects = []
    if not os.path.exists(PROJECTS_BASE_DIR):
        return projects

    for slug in os.listdir(PROJECTS_BASE_DIR):
        project_path = get_project_path(slug)
        if os.path.isdir(project_path):
            try:
                prefs = load_prefs(project_path)
                projects.append({
                    "slug": slug,
                    "title": prefs.get("story_title", "Untitled"),
                    "author": prefs.get("story_author", "Unknown Author"),
                    "copyright_year": prefs.get("copyright_year", "")
                })
            except FileNotFoundError:
                # If prefs.json doesn't exist, skip this directory
                pass
            except json.JSONDecodeError:
                # Handle cases where prefs.json might be malformed
                pass
    return projects

def get_single_project_details(slug):
    """
    Loads and returns project preferences for a single project.
    """
    project_path = get_project_path(slug)
    try:
        prefs = load_prefs(project_path)
        # Ensure that prefs is a dictionary; if not, initialize as empty dict
        if not isinstance(prefs, dict):
            prefs = {}

        return {
            "slug": slug,
            "project_path": project_path,
            "title": prefs.get("story_title", "Untitled"),
            "author": prefs.get("story_author", "Unknown Author"),
            "copyright_year": prefs.get("copyright_year", ""),
            # Include other preferences from the loaded file
            **prefs
        }
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

def update_project_details(slug, new_title, new_author, new_copyright_year, cover_image_file=None, custom_css_file=None):
    """
    Updates the preferences for a specific project, including optional cover image and custom CSS.
    """
    project_path = get_project_path(slug)
    includes_path = get_includes_path(project_path)
    os.makedirs(includes_path, exist_ok=True) # Ensure includes directory exists

    try:
        prefs = load_prefs(project_path)
        prefs["story_title"] = new_title
        prefs["story_author"] = new_author
        prefs["copyright_year"] = new_copyright_year

        # Handle cover image upload
        if cover_image_file:
            filename_to_save = secure_filename(cover_image_file.filename)
            # Delete old cover image if it exists and is different from the new secured filename
            if 'cover_image' in prefs and prefs['cover_image'] and prefs['cover_image'] != filename_to_save:
                old_cover_path = os.path.join(includes_path, prefs['cover_image'])
                if os.path.exists(old_cover_path):
                    os.remove(old_cover_path)
            
            cover_image_file.save(os.path.join(includes_path, filename_to_save))
            prefs['cover_image'] = filename_to_save
        # If no new file is uploaded, retain the existing one, do nothing.

        # Handle custom CSS upload
        if custom_css_file:
            filename_to_save = secure_filename(custom_css_file.filename)
            # Delete old custom CSS if it exists and is different from the new secured filename
            if 'custom_css' in prefs and prefs['custom_css'] and prefs['custom_css'] != filename_to_save:
                old_css_path = os.path.join(includes_path, prefs['custom_css'])
                if os.path.exists(old_css_path):
                    os.remove(old_css_path)

            custom_css_file.save(os.path.join(includes_path, filename_to_save))
            prefs['custom_css'] = filename_to_save
        # If no new file is uploaded, retain the existing one, do nothing.

        save_prefs(project_path, prefs)
        return True, "Project updated successfully."
    except Exception as e:
        return False, f"Error updating project: {e}"

def delete_project(slug):
    """
    Deletes a project directory and its contents.
    """
    project_path = get_project_path(slug)
    if os.path.exists(project_path) and os.path.isdir(project_path):
        try:
            shutil.rmtree(project_path)
            return True, "Project deleted successfully."
        except OSError as e:
            return False, f"Error deleting project {slug}: {e}"
    return False, "Project not found."
