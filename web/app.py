import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

from web.src.manage_projects import get_projects_list, delete_project, get_single_project_details, update_project_details
from web.src.new_project import create_project_files
from web.src import chapters as web_chapters # Renamed to avoid conflict with template variable
from web.src import social_media as web_social_media

UPLOAD_FOLDER = 'uploads' # Temporary folder for uploaded files
ALLOWED_EXTENSIONS = {'html', 'txt', 'docx'}

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
app.secret_key = 'your_secret_key' # Replace with a strong secret key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Ensure upload folder exists

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/new_project", methods=["GET"])
def new_project():
    return render_template("new_project.html")

@app.route("/create_project", methods=["POST"])
def create_project():
    title = request.form["title"]
    author = request.form["author"]
    copyright_year = request.form["copyright_year"]

    create_project_files(title, author, copyright_year)

    flash(f"Project '{title}' created successfully!", "success")
    return redirect(url_for("manage_projects"))

@app.route("/manage_projects", methods=["GET"])
def manage_projects():
    projects = get_projects_list()
    return render_template("manage_projects.html", projects=projects)

@app.route("/delete_project/<slug>", methods=["POST"])
def delete_project_route(slug):
    success, message = delete_project(slug)
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for("manage_projects"))

@app.route("/edit_project/<slug>", methods=["GET", "POST"])
def edit_project(slug):
    project = get_single_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("manage_projects"))

    if request.method == "POST":
        new_title = request.form["title"]
        new_author = request.form["author"]
        new_copyright_year = request.form["copyright_year"]

        success, message = update_project_details(
            slug, new_title, new_author, new_copyright_year
        )
        if success:
            flash(message, "success")
            return redirect(url_for("manage_projects"))
        else:
            flash(message, "error")
    
    return render_template("edit_project.html", project=project)

@app.route("/project/<slug>", methods=["GET"])
def project_dashboard(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("manage_projects"))
    return render_template("project.html", project=project)

@app.route("/project/<slug>/social_media", methods=["GET", "POST"])
def social_media_management(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("manage_projects"))

    all_social_platforms = web_social_media.get_social_platforms()
    project_social_links = web_social_media.get_project_social_links(project['project_path']) # Use project_path from prefs

    if request.method == "POST":
        action = request.form.get('action')
        platform_key = request.form.get('platform_key')

        if action == 'update_follow':
            handle = request.form.get('handle')
            if handle:
                success, message = web_social_media.update_follow_link(project['project_path'], platform_key, handle)
            else:
                success, message = False, "Handle cannot be empty."
            if success:
                flash(message, "success")
            else:
                flash(message, "error")
        elif action == 'delete_follow':
            success, message = web_social_media.delete_follow_link(project['project_path'], platform_key)
            if success:
                flash(message, "success")
            else:
                flash(message, "error")
        elif action == 'update_share':
            # Checkbox value is 'on' if checked, None if unchecked (not sent in form data)
            enable = request.form.get('enable_share') == 'on' 
            success, message = web_social_media.update_share_link_status(project['project_path'], platform_key, enable)
            if success:
                flash(message, "success")
            else:
                flash(message, "error")
        
        # Redirect back to the same page after POST to see updates
        return redirect(url_for("social_media_management", slug=slug))

    # For GET request or after POST redirect
    return render_template(
        "social_media.html",
        project=project,
        all_social_platforms=all_social_platforms,
        project_social_links=project_social_links
    )


@app.route("/project/<slug>/chapters", methods=["GET"])
def chapters_list(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("manage_projects"))
    
    chapters = web_chapters.get_chapters_data(slug)
    return render_template("chapters.html", project=project, chapters=chapters)

@app.route("/project/<slug>/chapters/add", methods=["GET", "POST"])
def add_chapter(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("manage_projects"))
    
    if request.method == "POST":
        uploaded_file = None
        if 'chapter_file' in request.files:
            file = request.files['chapter_file']
            if file and allowed_file(file.filename):
                uploaded_file = file
            elif file.filename != '': # If a file was selected but not allowed
                 flash("Invalid file type. Allowed types: html, txt, docx.", "error")
                 return render_template("add_chapter.html", project=project)
        
        if web_chapters.process_add_chapter(slug, request.form, uploaded_file):
            return redirect(url_for("chapters_list", slug=slug))
    
    return render_template("add_chapter.html", project=project)

@app.route("/project/<slug>/chapters/edit/<int:chapter_num>", methods=["GET", "POST"])
def edit_chapter(slug, chapter_num):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("manage_projects"))

    chapter = web_chapters.get_single_chapter_data(slug, chapter_num)
    if not chapter:
        flash(f"Chapter {chapter_num} not found in project '{slug}'.", "error")
        return redirect(url_for("chapters_list", slug=slug))

    if request.method == "POST":
        uploaded_file = None
        if 'chapter_file' in request.files:
            file = request.files['chapter_file']
            if file and allowed_file(file.filename):
                uploaded_file = file
            elif file.filename != '': # If a file was selected but not allowed
                 flash("Invalid file type. Allowed types: html, txt, docx.", "error")
                 return render_template("edit_chapter.html", project=project, chapter=chapter)
        
        if web_chapters.process_edit_chapter(slug, chapter_num, request.form, uploaded_file):
            return redirect(url_for("chapters_list", slug=slug))

    return render_template("edit_chapter.html", project=project, chapter=chapter)

@app.route("/project/<slug>/chapters/delete/<int:chapter_num>", methods=["POST"])
def delete_chapter(slug, chapter_num):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("manage_projects"))

    if web_chapters.process_delete_chapter(slug, chapter_num):
        # Flash message already handled by process_delete_chapter
        pass
    
    return redirect(url_for("chapters_list", slug=slug))
