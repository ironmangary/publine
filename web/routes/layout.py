from flask import Blueprint, render_template, request, redirect, url_for, flash
from web.src import chapters as web_chapters
from web.src import layout_manager as web_layout_manager

layout_bp = Blueprint('layout_bp', __name__)

@layout_bp.route("/project/<slug>/layout", methods=["GET"])
def project_layout(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("projects_bp.manage_projects"))
    return render_template("project_layout.html", project=project)

@layout_bp.route("/project/<slug>/layout/html", methods=["GET", "POST"])
def html_layout(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("projects_bp.manage_projects"))

    if request.method == "POST":
        success, message = web_layout_manager.update_html_layout_features(project['project_path'], request.form)
        if success:
            flash(message, "success")
        else:
            flash(message, "info") # Use info for no changes, error for actual errors
        return redirect(url_for("layout_bp.html_layout", slug=slug))

    # For GET request
    display_features = web_layout_manager.get_html_layout_features(project['project_path'])
    return render_template("html_layout.html", project=project, display_features=display_features)

@layout_bp.route("/project/<slug>/layout/epub", methods=["GET", "POST"])
def epub_layout(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("projects_bp.manage_projects"))

    if request.method == "POST":
        success, message = web_layout_manager.update_epub_layout_features(project['project_path'], request.form)
        if success:
            flash(message, "success")
        else:
            flash(message, "info")
        return redirect(url_for("layout_bp.epub_layout", slug=slug))

    # For GET request
    display_features = web_layout_manager.get_epub_layout_features(project['project_path'])
    return render_template("epub_layout.html", project=project, display_features=display_features)

@layout_bp.route("/project/<slug>/layout/pdf", methods=["GET", "POST"])
def pdf_layout(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("projects_bp.manage_projects"))

    if request.method == "POST":
        success, message = web_layout_manager.update_pdf_layout_features(project['project_path'], request.form)
        if success:
            flash(message, "success")
        else:
            flash(message, "info")
        return redirect(url_for("layout_bp.pdf_layout", slug=slug))

    # For GET request
    display_features = web_layout_manager.get_pdf_layout_features(project['project_path'])
    return render_template("pdf_layout.html", project=project, display_features=display_features)
