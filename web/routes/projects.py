import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from web.src.manage_projects import get_projects_list, delete_project, get_single_project_details, update_project_details
from web.src.new_project import create_project_files
from web.src import chapters as web_chapters

projects_bp = Blueprint('projects_bp', __name__)

@projects_bp.route("/new_project", methods=["GET"])
def new_project():
    return render_template("new_project.html")

@projects_bp.route("/create_project", methods=["POST"])
def create_project():
    title = request.form["title"]
    author = request.form["author"]
    copyright_year = request.form["copyright_year"]

    create_project_files(title, author, copyright_year)

    flash(f"Project '{title}' created successfully!", "success")
    return redirect(url_for("projects_bp.manage_projects"))

@projects_bp.route("/project/<slug>", methods=["GET"])
def project_dashboard(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("projects_bp.manage_projects"))
    return render_template("project.html", project=project)

@projects_bp.route("/manage_projects", methods=["GET"])
def manage_projects():
    projects = get_projects_list()
    return render_template("manage_projects.html", projects=projects)

@projects_bp.route("/delete_project/<slug>", methods=["POST"])
def delete_project_route(slug):
    success, message = delete_project(slug)
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for("projects_bp.manage_projects"))
