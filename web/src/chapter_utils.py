import os
import json
from werkzeug.utils import secure_filename
from flask import current_app

from core.src.importer import import_content
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
