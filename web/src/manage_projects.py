import os
import json

def get_projects_list():
    """
    Returns a list of dictionaries for each project,
    containing slug, title, and author.
    """
    projects_dir = "projects"
    projects = []
    if not os.path.exists(projects_dir):
        return projects

    for slug in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, slug)
        prefs_path = os.path.join(project_path, "data", "prefs.json")
        if os.path.isdir(project_path) and os.path.exists(prefs_path):
            try:
                with open(prefs_path, "r", encoding="utf-8") as f:
                    prefs = json.load(f)
                projects.append({
                    "slug": slug,
                    "title": prefs.get("story_title", "Untitled"),
                    "author": prefs.get("story_author", "Unknown Author")
                })
            except json.JSONDecodeError:
                # Handle cases where prefs.json might be malformed
                pass
    return projects

def delete_project(slug):
    """
    Deletes a project directory and its contents.
    """
    project_path = os.path.join("projects", slug)
    if os.path.exists(project_path) and os.path.isdir(project_path):
        try:
            import shutil
            shutil.rmtree(project_path)
            return True
        except OSError as e:
            print(f"Error deleting project {slug}: {e}")
            return False
    return False
