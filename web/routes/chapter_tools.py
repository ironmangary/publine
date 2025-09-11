import os
from flask import Blueprint, render_template, flash, redirect, url_for, request
from web.src.manage_projects import get_single_project_details, get_project_path
import os
import json # Added for handling JSON data for characters
from flask import Blueprint, render_template, flash, redirect, url_for, request
from web.src.manage_projects import get_single_project_details, get_project_path
from web.src.chapter_tools import get_chapter_tools_options, summarize_chapter_with_ai, generate_social_media_post_with_ai, save_social_media_post, _slugify_for_filename, track_characters_with_ai
from web.src.chapter_utils import list_chapters, get_single_chapter_data, save_chapter_summary, get_chapter_plain_text_content, save_character_tracking_data, load_character_tracking_data

chapter_tools_bp = Blueprint('chapter_tools_bp', __name__)

@chapter_tools_bp.route("/project/<slug>/chapter_tools", methods=["GET"])
def chapter_tools_menu(slug):
    project = get_single_project_details(slug)
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for('projects_bp.manage_projects'))

    project_path = get_project_path(slug)
    chapters = list_chapters(project_path)
    tools = get_chapter_tools_options()
    return render_template("chapter_tools.html", project=project, tools=tools, chapters=chapters)

@chapter_tools_bp.route("/project/<slug>/chapter_tools/summarize/<int:chapter_num>", methods=["GET", "POST"])
def summarize_chapter(slug, chapter_num):
    project = get_single_project_details(slug)
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for('projects_bp.manage_projects'))

    project_path = get_project_path(slug)
    chapter = get_single_chapter_data(project_path, chapter_num)
    if not chapter:
        flash(f"Chapter {chapter_num} not found.", "error")
        return redirect(url_for('chapter_tools_bp.chapter_tools_menu', slug=slug))

    summary_text = ""
    error_message = None

    # Calculate expected summary file path for display purposes
    expected_summary_file_relative = os.path.join("includes", f"chapter_{chapter_num}_summary.md")

    if request.method == "POST":
        if "trigger_summary" in request.form:
            success, result, _ = summarize_chapter_with_ai(project_path, chapter_num)
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
                    save_chapter_summary(project_path, chapter_num, edited_summary)
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

@chapter_tools_bp.route("/project/<slug>/chapter_tools/track_characters/<int:chapter_num>", methods=["GET", "POST"])
def track_characters(slug, chapter_num):
    project = get_single_project_details(slug)
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for('projects_bp.manage_projects'))

    project_path = get_project_path(slug)
    chapter = get_single_chapter_data(project_path, chapter_num)
    if not chapter:
        flash(f"Chapter {chapter_num} not found.", "error")
        return redirect(url_for('chapter_tools_bp.chapter_tools_menu', slug=slug))

    characters_data = []
    error_message = None
    
    # Calculate expected character file path for display purposes
    expected_character_file_relative = os.path.join("includes", f"characters_chapter_{chapter_num}.json")

    if request.method == "POST":
        if "trigger_character_tracking" in request.form:
            success, result, _ = track_characters_with_ai(project_path, chapter_num)
            if success:
                characters_data = result
                flash("AI character tracking generated successfully. Please review and save.", "success")
            else:
                error_message = result
                flash(f"Error generating AI character tracking: {error_message}", "error")
        elif "save_characters" in request.form:
            # The client-side might send the data back as JSON string
            edited_characters_json = request.form.get("edited_characters_data")
            if edited_characters_json:
                try:
                    # Parse the JSON string from the form
                    parsed_characters = json.loads(edited_characters_json)
                    save_character_tracking_data(project_path, chapter_num, parsed_characters)
                    flash("Character data saved successfully.", "success")
                    return redirect(url_for('chapter_tools_bp.chapter_tools_menu', slug=slug))
                except json.JSONDecodeError:
                    error_message = "Invalid JSON data provided for saving characters."
                    flash(error_message, "error")
                    characters_data = json.loads(edited_characters_json) if edited_characters_json else []
                except Exception as e:
                    error_message = f"Error saving character data: {e}"
                    flash(error_message, "error")
                    characters_data = json.loads(edited_characters_json) if edited_characters_json else []
            else:
                error_message = "No character data provided to save."
                flash(error_message, "error")
    else: # GET request
        # Load existing character data if available
        existing_characters = load_character_tracking_data(project_path, chapter_num)
        if existing_characters:
            characters_data = existing_characters
            flash("Existing character data loaded.", "info")

    return render_template(
        "track_characters.html",
        project=project,
        chapter=chapter,
        characters_data=characters_data,
        expected_character_file_relative=expected_character_file_relative,
        error_message=error_message
    )

@chapter_tools_bp.route("/project/<slug>/chapter_tools/generate_social_post/<int:chapter_num>", methods=["GET", "POST"])
def generate_social_post(slug, chapter_num):
    project = get_single_project_details(slug)
    if not project:
        flash("Project not found.", "error")
        return redirect(url_for('projects_bp.manage_projects'))

    project_path = get_project_path(slug)
    chapter = get_single_chapter_data(project_path, chapter_num)
    if not chapter:
        flash(f"Chapter {chapter_num} not found.", "error")
        return redirect(url_for('chapter_tools_bp.chapter_tools_menu', slug=slug))

    generated_post_content = ""
    error_message = None

    tones = ["Professional", "Casual", "Mysterious", "Enthusiastic", "Reflective", "Dramatic"]
    lengths = ["Short (Under 280 characters, X/Bluesky)", "Medium (1-2 paragraphs, Instagram/Threads)", "Long (3-5 paragraphs, Facebook/LinkedIn)"]
    
    # Initialize selected_tone and selected_length for GET requests or form redisplays
    selected_tone = request.form.get("tone", tones[0])
    selected_length = request.form.get("length", lengths[0])

    # Calculate expected post file path for display purposes
    slugified_length_display = _slugify_for_filename(selected_length)
    slugified_tone_display = _slugify_for_filename(selected_tone)
    expected_post_file_relative = os.path.join("includes", f"{slug}_chapter_{chapter_num}_{slugified_length_display}_{slugified_tone_display}.md")


    if request.method == "POST":
        if "trigger_post" in request.form:
            selected_tone = request.form.get("tone")
            selected_length = request.form.get("length")

            success, result, _ = generate_social_media_post_with_ai(project_path, chapter_num, selected_tone, selected_length)
            if success:
                generated_post_content = result
                flash("AI social media post generated successfully. Please review and save.", "success")
            else:
                error_message = result
                flash(f"Error generating AI social media post: {error_message}", "error")
            
            # Recalculate expected filename based on newly selected tone/length for display
            slugified_length_display = _slugify_for_filename(selected_length)
            slugified_tone_display = _slugify_for_filename(selected_tone)
            expected_post_file_relative = os.path.join("includes", f"{slug}_chapter_{chapter_num}_{slugified_length_display}_{slugified_tone_display}.md")

        elif "save_post" in request.form:
            edited_post = request.form.get("edited_post_content")
            # Retrieve selected tone and length, as they are needed for saving the file with the correct name
            selected_tone_for_save = request.form.get("selected_tone_hidden") # Use hidden fields for values from generation step
            selected_length_for_save = request.form.get("selected_length_hidden") # Use hidden fields for values from generation step
            
            if edited_post is not None and selected_tone_for_save and selected_length_for_save:
                try:
                    # Pass slug, length, and tone to save_social_media_post
                    save_social_media_post(project_path, slug, chapter_num, edited_post, selected_length_for_save, selected_tone_for_save)
                    flash("Social media post saved successfully.", "success")
                    return redirect(url_for('chapter_tools_bp.chapter_tools_menu', slug=slug))
                except Exception as e:
                    error_message = f"Error saving post: {e}"
                    flash(error_message, "error")
                    generated_post_content = edited_post # Keep edited content in the form
                    # Re-set selected_tone and selected_length for rendering if save fails
                    selected_tone = selected_tone_for_save
                    selected_length = selected_length_for_save
            else:
                error_message = "No post content, tone, or length provided to save."
                flash(error_message, "error")
                # Re-set selected_tone and selected_length for rendering if save fails due to missing data
                selected_tone = selected_tone_for_save if selected_tone_for_save else tones[0]
                selected_length = selected_length_for_save if selected_length_for_save else lengths[0]

    return render_template(
        "generate_social_post.html",
        project=project,
        chapter=chapter,
        generated_post_content=generated_post_content,
        # Recalculate expected filename based on potentially updated selected_tone/length after a failed save
        expected_post_file_relative=os.path.join("includes", f"{slug}_chapter_{chapter_num}_{_slugify_for_filename(selected_length)}_{_slugify_for_filename(selected_tone)}.md"),
        error_message=error_message,
        tones=tones,
        lengths=lengths,
        selected_tone=selected_tone,
        selected_length=selected_length
    )
