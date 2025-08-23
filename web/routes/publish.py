import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from web.src.chapters import get_project_details, get_project_path, get_chapters_data
from core.src.utils import load_prefs
from cli.src.chapter_utils import ensure_cover_image
from web.src.html_output import build_html
from web.src.epub_output import build_epub
from web.src.pdf_output import build_pdf

publish_bp = Blueprint('publish_bp', __name__)

@publish_bp.route("/project/<slug>/publish", methods=["GET", "POST"])
def publish_output_menu(slug):
    project_path = get_project_path(slug)
    project_details = get_project_details(slug)
    if not project_details:
        flash("Project not found.", "error")
        return redirect(url_for('projects_bp.manage_projects'))

    if request.method == "POST":
        action = request.form.get("action")
        prefs = load_prefs(project_path)
        chapters_data = get_chapters_data(slug)
        try:
            ensure_cover_image(project_path, os.path.join(project_path, "includes"))
            if action == "publish_html":
                build_html(project_path, prefs, chapters_data)
                flash("HTML publishing complete.", "success")
            elif action == "publish_epub":
                build_epub(project_path, prefs, chapters_data)
                flash("EPUB publishing complete.", "success")
            elif action == "publish_pdf":
                build_pdf(project_path, prefs, chapters_data)
                flash("PDF publishing complete.", "success")
            elif action == "publish_all":
                build_html(project_path, prefs, chapters_data)
                build_epub(project_path, prefs, chapters_data)
                build_pdf(project_path, prefs, chapters_data)
                flash("All formats publishing complete.", "success")
            else:
                flash("Invalid action.", "error")
        except Exception as e:
            flash(f"Error during publishing: {e}", "error")
        return redirect(url_for('projects_bp.project_dashboard', slug=slug))

    return render_template("publish_output.html", project=project_details)

@publish_bp.route("/project/<slug>/publish/html", methods=["GET", "POST"])
def publish_html(slug):
    project_path = get_project_path(slug)
    project_details = get_project_details(slug)
    if not project_details:
        flash("Project not found.", "error")
        return redirect(url_for('projects_bp.manage_projects'))

    if request.method == "POST":
        prefs = load_prefs(project_path)
        chapters_data = get_chapters_data(slug)
        try:
            ensure_cover_image(project_path, os.path.join(project_path, "includes"))
            build_html(project_path, prefs, chapters_data)
            flash("Static HTML Web Site publishing complete.", "success")
        except Exception as e:
            flash(f"Error during HTML publishing: {e}", "error")
        return redirect(url_for('publish_bp.publish_html', slug=slug))

    return render_template("publish_html.html", project=project_details)

@publish_bp.route("/project/<slug>/publish/epub", methods=["GET", "POST"])
def publish_epub(slug):
    project_path = get_project_path(slug)
    project_details = get_project_details(slug)
    if not project_details:
        flash("Project not found.", "error")
        return redirect(url_for('projects_bp.manage_projects'))

    if request.method == "POST":
        prefs = load_prefs(project_path)
        chapters_data = get_chapters_data(slug)
        try:
            ensure_cover_image(project_path, os.path.join(project_path, "includes"))
            build_epub(project_path, prefs, chapters_data)
            flash("EPUB publishing complete.", "success")
        except Exception as e:
            flash(f"Error during EPUB publishing: {e}", "error")
        return redirect(url_for('publish_bp.publish_epub', slug=slug))

    return render_template("publish_epub.html", project=project_details)

@publish_bp.route("/project/<slug>/publish/pdf", methods=["GET", "POST"])
def publish_pdf(slug):
    project_path = get_project_path(slug)
    project_details = get_project_details(slug)
    if not project_details:
        flash("Project not found.", "error")
        return redirect(url_for('projects_bp.manage_projects'))

    if request.method == "POST":
        prefs = load_prefs(project_path)
        chapters_data = get_chapters_data(slug)
        try:
            ensure_cover_image(project_path, os.path.join(project_path, "includes"))
            build_pdf(project_path, prefs, chapters_data)
            flash("PDF publishing complete.", "success")
        except Exception as e:
            flash(f"Error during PDF publishing: {e}", "error")
        return redirect(url_for('publish_bp.publish_pdf', slug=slug))

    return render_template("publish_pdf.html", project=project_details)
