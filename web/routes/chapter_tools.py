import os
from flask import Blueprint, render_template, flash, redirect, url_for, request
from web.src.manage_projects import get_single_project_details, get_project_path # Added get_project_path
from web.src.chapter_tools import get_chapter_tools_options, summarize_chapter_with_ai
from web.src.chapter_utils import list_chapters, get_single_chapter_data, save_chapter_summary

chapter_tools_bp = Blueprint('chapter_tools_bp', __name__)

@chapter_tools_bp.route("/project/<slug>/chapter_tools", methods=["GET"])
def chapter_tools_menu(slug):
    project = get_single_project_details(slug)
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for('projects_bp.manage_projects'))

    project_path = get_project_path(slug) # Get the actual project path
    chapters = list_chapters(project_path)
    tools = get_chapter_tools_options()
    return render_template("chapter_tools.html", project=project, tools=tools, chapters=chapters)

@chapter_tools_bp.route("/project/<slug>/chapter_tools/summarize/<int:chapter_num>", methods=["GET", "POST"])
def summarize_chapter(slug, chapter_num):
    project = get_single_project_details(slug)
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for('projects_bp.manage_projects'))

    project_path = get_project_path(slug) # Get the actual project path
    chapter = get_single_chapter_data(project_path, chapter_num)
    if not chapter:
        flash(f"Chapter {chapter_num} not found.", "error")
        return redirect(url_for('chapter_tools_bp.chapter_tools_menu', slug=slug))

    summary_text = ""
    saved_file_name = "" # This will store the relative path for display
    error_message = None

    # Calculate expected summary file path for display purposes
    expected_summary_file_relative = os.path.join("includes", f"chapter_{chapter_num}_summary.md")

    if request.method == "POST":
        if "trigger_summary" in request.form:
            success, result, _ = summarize_chapter_with_ai(project_path, chapter_num) # Use project_path here
            if success:
                summary_text = result
                flash("AI summary generated successfully. Please review and save.", "success")
            else:
                error_message = result
                flash(f"Error generating AI summary: {error_message}", "error")
        elif "save_summary" in request.form:
            edited_summary = request.form.get("edited_summary_content")
            if edited_summary is not None:
                try:
                    full_saved_path = save_chapter_summary(project_path, chapter_num, edited_summary) # Use project_path here
                    flash("Summary saved successfully.", "success")
                    return redirect(url_for('chapter_tools_bp.chapter_tools_menu', slug=slug))
                except Exception as e:
                    error_message = f"Error saving summary: {e}"
                    flash(error_message, "error")
                    summary_text = edited_summary # Keep edited content in the form
            else:
                error_message = "No summary content provided to save."
                flash(error_message, "error")
        
    return render_template(
        "summarize_chapter.html",
        project=project,
        chapter=chapter,
        summary_text=summary_text,
        expected_summary_file_relative=expected_summary_file_relative,
        error_message=error_message
    )
