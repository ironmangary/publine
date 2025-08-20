from flask import Blueprint, render_template, request, redirect, url_for, flash
from web.src import chapters as web_chapters
from web.src.chapter_utils import allowed_chapter_file

chapters_bp = Blueprint('chapters_bp', __name__)

@chapters_bp.route("/project/<slug>/chapters", methods=["GET"])
def chapters_list(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("projects_bp.manage_projects"))
    
    chapters = web_chapters.get_chapters_data(slug)
    return render_template("chapters.html", project=project, chapters=chapters)

@chapters_bp.route("/project/<slug>/chapters/add", methods=["GET", "POST"])
def add_chapter(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("projects_bp.manage_projects"))
    
    if request.method == "POST":
        uploaded_file = None
        if 'chapter_file' in request.files:
            file = request.files['chapter_file']
            if file and allowed_chapter_file(file.filename):
                uploaded_file = file
            elif file.filename != '': # If a file was selected but not allowed
                 flash("Invalid file type. Allowed types for chapters: html, txt, docx.", "error")
                 return render_template("add_chapter.html", project=project)
        
        if web_chapters.process_add_chapter(slug, request.form, uploaded_file):
            return redirect(url_for("chapters_bp.chapters_list", slug=slug))
    
    return render_template("add_chapter.html", project=project)

@chapters_bp.route("/project/<slug>/chapters/edit/<int:chapter_num>", methods=["GET", "POST"])
def edit_chapter(slug, chapter_num):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("projects_bp.manage_projects"))

    chapter = web_chapters.get_single_chapter_data(slug, chapter_num)
    if not chapter:
        flash(f"Chapter {chapter_num} not found in project '{slug}'.", "error")
        return redirect(url_for("chapters_bp.chapters_list", slug=slug))

    if request.method == "POST":
        uploaded_file = None
        if 'chapter_file' in request.files:
            file = request.files['chapter_file']
            if file and allowed_chapter_file(file.filename):
                uploaded_file = file
            elif file.filename != '': # If a file was selected but not allowed
                 flash("Invalid file type. Allowed types for chapters: html, txt, docx.", "error")
                 return render_template("edit_chapter.html", project=project, chapter=chapter)
        
        if web_chapters.process_edit_chapter(slug, chapter_num, request.form, uploaded_file):
            return redirect(url_for("chapters_bp.chapters_list", slug=slug))

    return render_template("edit_chapter.html", project=project, chapter=chapter)

@chapters_bp.route("/project/<slug>/chapters/delete/<int:chapter_num>", methods=["POST"])
def delete_chapter(slug, chapter_num):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("projects_bp.manage_projects"))

    if web_chapters.process_delete_chapter(slug, chapter_num):
        # Flash message already handled by process_delete_chapter
        pass
    
    return redirect(url_for("chapters_bp.chapters_list", slug=slug))
