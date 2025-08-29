from flask import Blueprint, render_template
from web.src.manage_projects import get_single_project_details
from web.src.project_tools import get_project_tools_options

project_tools_bp = Blueprint('project_tools_bp', __name__)

@project_tools_bp.route("/project/<slug>/project_tools", methods=["GET"])
def project_tools_menu(slug):
    project = get_single_project_details(slug)
    if not project:
        # Handle project not found, e.g., flash message and redirect
        return "Project not found", 404 # Placeholder for now
    
    tools = get_project_tools_options()
    return render_template("project_tools.html", project=project, tools=tools)
