import os
import json
from werkzeug.utils import secure_filename
from flask import current_app

from core.src.importer import import_content, html_to_plain_text
from core.src.utils import load_json, save_json, load_prefs, save_prefs # load_prefs/save_prefs not directly used in CUD, but in ensure_cover_image

ALLOWED_CHAPTER_EXTENSIONS = {'html', 'txt', 'docx'}

def allowed_chapter_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_CHAPTER_EXTENSIONS

def get_chapters_path(project_path):
    return os.path.join(project_path, "data", "chapters.json")

def get_includes_path(project_path):
    return os.path.join(project_path, "includes")

def load_chapters(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_chapters(path, chapters):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chapters, f, indent=4)

def list_chapters(project_path):
    path = get_chapters_path(project_path)
    return sorted(load_chapters(path), key=lambda ch: ch.get("number", 0))

def add_chapter(project_path, number, title, discussion, import_format, uploaded_file):
    chapters_path = get_chapters_path(project_path)
    includes_path = get_includes_path(project_path)
    os.makedirs(includes_path, exist_ok=True)

    chapters = load_chapters(chapters_path)

    if any(ch["number"] == number for ch in chapters):
        return False, "That chapter number already exists."

    filename = f"chapter_{number}.html"
    output_path = os.path.join(includes_path, filename)
    import_source_relative = f"includes/{filename}"

    if uploaded_file:
        try:
            # Save uploaded file temporarily for import_content if it's not HTML
            temp_upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(uploaded_file.filename))
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            uploaded_file.save(temp_upload_path)

            html = import_content(temp_upload_path, import_format)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
            os.remove(temp_upload_path) # Clean up temp file

        except Exception as e:
            return False, f"Import failed: {e}"
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("")  # blank file

    chapters.append({
        "number": number,
        "title": title,
        "discussion": discussion,
        "import_source": import_source_relative,
        "import_format": import_format,
        "exclude_from_epub": False,
        "exclude_from_pdf": False,
        "draft": False
    })

    save_chapters(chapters_path, chapters)
    return True, "Chapter added successfully."

def edit_chapter(project_path, chapter_num, new_title, new_discussion, new_import_format, new_exclude_epub, new_exclude_pdf, new_draft, uploaded_file):
    chapters_path = get_chapters_path(project_path)
    includes_path = get_includes_path(project_path)
    os.makedirs(includes_path, exist_ok=True)

    chapters = load_chapters(chapters_path)
    chapter_found = False
    for i, ch in enumerate(chapters):
        if ch["number"] == chapter_num:
            chapters[i]["title"] = new_title
            chapters[i]["discussion"] = new_discussion
            chapters[i]["import_format"] = new_import_format
            chapters[i]["exclude_from_epub"] = new_exclude_epub
            chapters[i]["exclude_from_pdf"] = new_exclude_pdf
            chapters[i]["draft"] = new_draft

            # Handle file upload if provided
            if uploaded_file:
                filename = f"chapter_{chapter_num}.html" # Assuming we always output to HTML
                output_path = os.path.join(includes_path, filename)
                import_source_relative = f"includes/{filename}"

                try:
                    temp_upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(uploaded_file.filename))
                    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                    uploaded_file.save(temp_upload_path)

                    html = import_content(temp_upload_path, new_import_format)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(html)
                    os.remove(temp_upload_path) # Clean up temp file

                    chapters[i]["import_source"] = import_source_relative
                except Exception as e:
                    return False, f"File upload/import failed: {e}"

            chapter_found = True
            break

    if not chapter_found:
        return False, "Chapter not found."

    save_chapters(chapters_path, chapters)
    return True, "Chapter updated successfully."


def delete_chapter(project_path, chapter_num, delete_file_confirm=False):
    chapters_path = get_chapters_path(project_path)
    chapters = load_chapters(chapters_path)

    chapter_to_delete = None
    for ch in chapters:
        if ch["number"] == chapter_num:
            chapter_to_delete = ch
            break

    if not chapter_to_delete:
        return False, "Chapter not found."

    if delete_file_confirm and "import_source" in chapter_to_delete and chapter_to_delete["import_source"]:
        frag_path = os.path.join(project_path, chapter_to_delete["import_source"])
        if os.path.exists(frag_path):
            try:
                os.remove(frag_path)
                # print("🗑️ Fragment deleted.")
            except Exception as e:
                # Do not fail deletion of chapter entry if file deletion fails
                print(f"Warning: Could not delete fragment file {frag_path}: {e}")

    chapters.remove(chapter_to_delete)
    save_chapters(chapters_path, chapters)
    return True, "Chapter removed successfully."

def get_single_chapter_data(project_path, chapter_num):
    """
    Retrieves data for a single chapter.
    """
    chapters_path = get_chapters_path(project_path)
    chapters = load_chapters(chapters_path)
    return next((ch for ch in chapters if ch["number"] == chapter_num), None)

def get_chapter_plain_text_content(project_path, chapter_num):
    """
    Retrieves the plain text content of a specific chapter.
    Returns (chapter_title, chapter_plain_text) or raises an error.
    """
    chapters_path = get_chapters_path(project_path)
    chapters = load_chapters(chapters_path)

    chapter_data = next((ch for ch in chapters if ch["number"] == chapter_num), None)

    if not chapter_data:
        raise ValueError(f"Chapter {chapter_num} not found.")

    chapter_title = chapter_data.get("title", f"Chapter {chapter_num}")
    import_source_relative = chapter_data.get("import_source")
    import_format = chapter_data.get("import_format")

    if not import_source_relative:
        return chapter_title, "" # Return empty if no source specified

    full_source_path = os.path.join(project_path, import_source_relative)

    if not os.path.exists(full_source_path):
        raise FileNotFoundError(f"Chapter file not found: {full_source_path}")

    # Use core.src.importer to get HTML content, then convert to plain text
    html_content = import_content(full_source_path, import_format)
    plain_text_content = html_to_plain_text(html_content)

    return chapter_title, plain_text_content

def get_chapter_html_content(project_path, chapter_num):
    """
    Retrieves the raw HTML content of a specific chapter.
    Returns (chapter_title, chapter_html_content) or raises an error.
    """
    chapters_path = get_chapters_path(project_path)
    chapters = load_chapters(chapters_path)

    chapter_data = next((ch for ch in chapters if ch["number"] == chapter_num), None)

    if not chapter_data:
        raise ValueError(f"Chapter {chapter_num} not found.")

    chapter_title = chapter_data.get("title", f"Chapter {chapter_num}")
    import_source_relative = chapter_data.get("import_source")
    import_format = chapter_data.get("import_format")

    if not import_source_relative:
        return chapter_title, "" # Return empty if no source specified

    full_source_path = os.path.join(project_path, import_source_relative)

    if not os.path.exists(full_source_path):
        raise FileNotFoundError(f"Chapter file not found: {full_source_path}")

    # Use core.src.importer to get HTML content (it handles different import formats)
    html_content = import_content(full_source_path, import_format)

    return chapter_title, html_content


def save_chapter_summary(project_path, chapter_num, summary_content):
    """
    Saves the AI-generated summary to a Markdown file within the project's includes directory.
    """
    includes_path = get_includes_path(project_path)
    os.makedirs(includes_path, exist_ok=True)
    summary_filename = f"chapter_{chapter_num}_summary.md"
    summary_file_path = os.path.join(includes_path, summary_filename)

    with open(summary_file_path, "w", encoding="utf-8") as f:
        f.write(summary_content)
    return summary_file_path

def save_character_tracking_data(project_path, chapter_num, character_data):
    """
    Saves the AI-generated character tracking data to a JSON file.
    """
    includes_path = get_includes_path(project_path)
    os.makedirs(includes_path, exist_ok=True)
    character_filename = f"characters_chapter_{chapter_num}.json"
    character_file_path = os.path.join(includes_path, character_filename)

    with open(character_file_path, "w", encoding="utf-8") as f:
        json.dump(character_data, f, indent=4)
    return character_file_path

def load_character_tracking_data(project_path, chapter_num):
    """
    Loads character tracking data from a JSON file if it exists.
    Returns a list of character dicts, or None if the file doesn't exist.
    """
    includes_path = get_includes_path(project_path)
    character_filename = f"characters_chapter_{chapter_num}.json"
    character_file_path = os.path.join(includes_path, character_filename)

    if os.path.exists(character_file_path):
        with open(character_file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# The following functions are from original cli/src/chapter_utils.py but are not directly
# called by the web chapter management logic as it is being built.
# They are included for completeness if they might be used elsewhere later or adapted.

def ensure_cover_image(project_path, includes_path):
    prefs = load_prefs(project_path)
    if not prefs.get("cover_image"):
        # This function as is is interactive and not suitable for web directly
        # It would need a dedicated web form for cover image management
        pass 

def format_chapter_heading(chapter, use_titles=True):
    if use_titles:
        return f"Chapter {chapter['number']}: {chapter['title']}"
    return f"Chapter {chapter['number']}"
