import os
import markdown # For converting markdown blurb to HTML
from flask import Blueprint, render_template, request, redirect, url_for, flash
from web.src import chapters as web_chapters
from web.src import layout_manager as web_layout_manager
from core.src.utils import load_prefs, save_prefs # For managing blurb preferences and content file
from web.src.chapter_utils import get_includes_path # To get the project's includes path

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
        prefs = load_prefs(project['project_path'])
        display_features = prefs.get('display_features', {})
        
        # Collect all checkbox values
        updated_display_features = {
            "use_chapter_titles": 'use_chapter_titles' in request.form,
            "cover_image": 'cover_image' in request.form,
            "chapter_nav_top": 'chapter_nav_top' in request.form,
            "epub_link": 'epub_link' in request.form,
            "pdf_link": 'pdf_link' in request.form,
            "share_links": 'share_links' in request.form,
            "discuss_link": 'discuss_link' in request.form,
            "chapter_nav_bottom": 'chapter_nav_bottom' in request.form,
            "social_links": 'social_links' in request.form,
            "copyright": 'copyright' in request.form,
            "license": 'license' in request.form,
            "html_include_blurb": 'html_include_blurb' in request.form # New blurb flag
        }

        # Handle blurb content file
        html_include_blurb = updated_display_features['html_include_blurb']
        blurb_content = request.form.get('html_blurb_content', '').strip()
        includes_path = get_includes_path(project['project_path'])
        blurb_filepath = os.path.join(includes_path, "blurb.md")

        if html_include_blurb and blurb_content:
            try:
                with open(blurb_filepath, 'w', encoding='utf-8') as f:
                    f.write(blurb_content)
                updated_display_features['html_blurb_path'] = os.path.basename(blurb_filepath)
            except IOError as e:
                flash(f"Error saving blurb file: {e}", "error")
                return redirect(url_for("layout_bp.html_layout", slug=slug))
        elif not html_include_blurb and os.path.exists(blurb_filepath):
            try:
                os.remove(blurb_filepath)
                updated_display_features.pop('html_blurb_path', None)
            except OSError as e:
                flash(f"Error deleting blurb file: {e}", "error")
                return redirect(url_for("layout_bp.html_layout", slug=slug))
        else:
            updated_display_features.pop('html_blurb_path', None)
            # If blurb is checked but content is empty, ensure the file is removed if it exists
            if html_include_blurb and not blurb_content and os.path.exists(blurb_filepath):
                 try:
                    os.remove(blurb_filepath)
                 except OSError as e:
                    flash(f"Error deleting empty blurb file: {e}", "error")
                    return redirect(url_for("layout_bp.html_layout", slug=slug))


        prefs['display_features'] = updated_display_features
        save_prefs(project['project_path'], prefs)
        flash("HTML layout settings updated successfully!", "success")
        return redirect(url_for("layout_bp.html_layout", slug=slug))

    # For GET request
    display_features = web_layout_manager.get_html_layout_features(project['project_path'])
    blurb_content = ""
    includes_path = get_includes_path(project['project_path'])
    blurb_filepath = os.path.join(includes_path, "blurb.md")

    if display_features.get('html_include_blurb') and os.path.exists(blurb_filepath):
        with open(blurb_filepath, 'r', encoding='utf-8') as f:
            blurb_content = f.read()

    return render_template("html_layout.html", project=project, display_features=display_features, blurb_content=blurb_content)

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
