from flask import Blueprint, render_template
from web.src.manage_projects import get_single_project_details
from web.src.chapter_tools import get_chapter_tools_options
# from web.src.chapters import get_chapters_data # Uncomment if chapter list is needed for tools

chapter_tools_bp = Blueprint('chapter_tools_bp', __name__)

@chapter_tools_bp.route("/project/<slug>/chapter_tools", methods=["GET"])
def chapter_tools_menu(slug):
    project = get_single_project_details(slug)
    if not project:
        # Handle project not found, e.g., flash message and redirect
        return "Project not found", 404 # Placeholder for now

    # Optionally load chapters if chapter-specific tools need to be linked per chapter
    # chapters = get_chapters_data(slug) 

    tools = get_chapter_tools_options()
    return render_template("chapter_tools.html", project=project, tools=tools)
