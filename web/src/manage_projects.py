import os
import json
import shutil
from core.src.utils import load_prefs, save_prefs

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
        prefs['slug'] = slug # Add slug for URL generation
        prefs['project_path'] = project_path # Add project_path
        return prefs
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

def update_project_details(slug, new_title, new_author, new_copyright_year):
    """
    Updates the preferences for a specific project.
    """
    project_path = get_project_path(slug)
    try:
        prefs = load_prefs(project_path)
        prefs["story_title"] = new_title
        prefs["story_author"] = new_author
        prefs["copyright_year"] = new_copyright_year
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
