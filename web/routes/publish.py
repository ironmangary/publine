import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from web.src.chapters import get_project_details, get_project_path, get_chapters_data
from core.src.utils import load_prefs, load_json
from cli.src.chapter_utils import ensure_cover_image
from web.src.html_output import build_html # Updated import path
from cli.src.epub_output import build_epub
from cli.src.pdf_output import build_pdf

publish_bp = Blueprint('publish_bp', __name__)

@publish_bp.route("/project/<slug>/publish", methods=["GET", "POST"])
def publish_output_menu(slug):
    project_path = get_project_path(slug)
    project_details = get_project_details(slug)
    if not project_details:
        flash("Project not found.", "error")
        return redirect(url_for('projects_bp.manage_projects'))

    prefs = load_prefs(project_path)
    chapters_data = get_chapters_data(slug) # Assuming get_chapters_data returns list of chapter dicts

    if request.method == "POST":
        action = request.form.get("action")
        try:
            # Ensure cover image exists if needed by build_html/epub/pdf
            includes_path = os.path.join(project_path, "includes")
            ensure_cover_image(project_path, includes_path)

            if action == "publish_html":
                build_html(project_path, prefs, chapters_data)
                flash("Static HTML Web Site publishing complete.", "success")
            elif action == "publish_epub":
                build_epub(project_path)
                flash("EPUB publishing complete.", "success")
            elif action == "publish_pdf":
                build_pdf(project_path)
                flash("PDF publishing complete.", "success")
            elif action == "publish_all":
                build_html(project_path, prefs, chapters_data)
                build_epub(project_path)
                build_pdf(project_path)
                flash("All formats publishing complete.", "success")
            else:
                flash("Invalid publish action.", "error")
        except Exception as e:
            flash(f"Error during publishing: {e}", "error")

        return redirect(url_for('publish_bp.publish_output_menu', slug=slug))

    return render_template("publish_output.html", project=project_details)
