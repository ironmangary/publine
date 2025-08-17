import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

from web.src.manage_projects import get_projects_list, delete_project, get_single_project_details, update_project_details
from web.src.new_project import create_project_files
from web.src import chapters as web_chapters # Renamed to avoid conflict with template variable
from web.src import social_media as web_social_media
from web.src import layout_manager as web_layout_manager # For layout features
from core.src.utils import load_prefs, save_prefs # For project preferences
from web.src.licenses import load_license_definitions, save_license_definitions
from web.src.chapter_utils import get_includes_path # To get the includes path for file uploads

UPLOAD_FOLDER = 'uploads' # Temporary folder for uploaded files
ALLOWED_CHAPTER_EXTENSIONS = {'html', 'txt', 'docx'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
ALLOWED_CSS_EXTENSIONS = {'css'}

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
app.secret_key = 'your_secret_key' # Replace with a strong secret key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Ensure upload folder exists

def allowed_chapter_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_CHAPTER_EXTENSIONS

def allowed_image_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def allowed_css_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_CSS_EXTENSIONS

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

        cover_image_file = None
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and allowed_image_file(file.filename):
                cover_image_file = file
            elif file.filename != '':
                flash("Invalid cover image file type. Allowed types: png, jpg, jpeg, gif, svg.", "error")
                # Re-render the form with existing project data and the error
                return render_template("edit_project.html", project=project)

        custom_css_file = None
        if 'custom_css' in request.files:
            file = request.files['custom_css']
            if file and allowed_css_file(file.filename):
                custom_css_file = file
            elif file.filename != '':
                flash("Invalid CSS file type. Allowed types: css.", "error")
                # Re-render the form with existing project data and the error
                return render_template("edit_project.html", project=project)

        success, message = update_project_details(
            slug, new_title, new_author, new_copyright_year,
            cover_image_file, custom_css_file
        )
        if success:
            flash(message, "success")
            return redirect(url_for("manage_projects"))
        else:
            flash(message, "error")
    
    return render_template("edit_project.html", project=project)

@app.route("/project/<slug>/layout", methods=["GET"])
def project_layout(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("manage_projects"))
    return render_template("project_layout.html", project=project)

@app.route("/project/<slug>/layout/html", methods=["GET", "POST"])
def html_layout(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("manage_projects"))

    if request.method == "POST":
        success, message = web_layout_manager.update_html_layout_features(project['project_path'], request.form)
        if success:
            flash(message, "success")
        else:
            flash(message, "info") # Use info for no changes, error for actual errors
        return redirect(url_for("html_layout", slug=slug))

    # For GET request
    display_features = web_layout_manager.get_html_layout_features(project['project_path'])
    return render_template("html_layout.html", project=project, display_features=display_features)

@app.route("/project/<slug>/layout/epub", methods=["GET", "POST"])
def epub_layout(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("manage_projects"))

    if request.method == "POST":
        success, message = web_layout_manager.update_epub_layout_features(project['project_path'], request.form)
        if success:
            flash(message, "success")
        else:
            flash(message, "info")
        return redirect(url_for("epub_layout", slug=slug))

    # For GET request
    display_features = web_layout_manager.get_epub_layout_features(project['project_path'])
    return render_template("epub_layout.html", project=project, display_features=display_features)

@app.route("/project/<slug>/layout/pdf", methods=["GET", "POST"])
def pdf_layout(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("manage_projects"))

    if request.method == "POST":
        success, message = web_layout_manager.update_pdf_layout_features(project['project_path'], request.form)
        if success:
            flash(message, "success")
        else:
            flash(message, "info")
        return redirect(url_for("pdf_layout", slug=slug))

    # For GET request
    display_features = web_layout_manager.get_pdf_layout_features(project['project_path'])
    return render_template("pdf_layout.html", project=project, display_features=display_features)


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
            if file and allowed_chapter_file(file.filename):
                uploaded_file = file
            elif file.filename != '': # If a file was selected but not allowed
                 flash("Invalid file type. Allowed types for chapters: html, txt, docx.", "error")
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
            if file and allowed_chapter_file(file.filename):
                uploaded_file = file
            elif file.filename != '': # If a file was selected but not allowed
                 flash("Invalid file type. Allowed types for chapters: html, txt, docx.", "error")
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

@app.route("/project/<slug>/choose_license", methods=["GET", "POST"])
def choose_project_license(slug):
    """Allows selecting a license for a specific project."""
    project = get_single_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("manage_projects"))

    licenses = load_license_definitions()
    # Initialize project_prefs to an empty dictionary by default
    project_prefs = {}
    
    # Attempt to load project preferences
    project_prefs_loaded_data = load_prefs(project['project_path'])
    
    # If the loaded data is a dictionary, use it. Otherwise, keep project_prefs as an empty dict.
    if isinstance(project_prefs_loaded_data, dict):
        project_prefs = project_prefs_loaded_data
        
    # Safely get the license information, ensuring it's a dictionary
    license_info = project_prefs.get('license')
    if isinstance(license_info, dict):
        current_license_short_name = license_info.get('short_name', '')
    else:
        current_license_short_name = ''

    if request.method == "POST":
        selected_license_short_name = request.form.get("license_short_name")
        
        if not selected_license_short_name:
            flash("Please select a license.", "danger")
            return render_template("choose_project_license.html", project=project, licenses=licenses, current_license_short_name=current_license_short_name)
        
        chosen_license = next((lic for lic in licenses if lic['short_name'] == selected_license_short_name), None)
        
        if chosen_license:
            project_prefs['license'] = {
                'short_name': chosen_license['short_name'],
                'long_name': chosen_license['long_name'],
                'link': chosen_license['link'],
                'description': chosen_license['description']
            }
            save_prefs(project['project_path'], project_prefs)
            flash(f"License '{chosen_license['long_name']}' applied to project '{project['title']}'.", "success")
            return redirect(url_for("project_dashboard", slug=slug))
        else:
            flash("Invalid license selected.", "danger")

    return render_template("choose_project_license.html", project=project, licenses=licenses, current_license_short_name=current_license_short_name)

@app.route("/licenses", methods=["GET"])
def manage_licenses():
    """Displays a list of available licenses and provides options to manage them."""
    licenses = load_license_definitions()
    return render_template("licenses.html", licenses=licenses)

@app.route("/licenses/add", methods=["GET", "POST"])
def add_new_license():
    """Handles adding a new global license definition."""
    if request.method == "POST":
        short = request.form.get("short_name")
        long = request.form.get("long_name")
        link = request.form.get("link")
        desc = request.form.get("description")

        if not all([short, long, link, desc]):
            flash("All fields are required to add a new license.", "danger")
            return render_template("add_license.html", form_data=request.form)

        new_license = {
            "short_name": short,
            "long_name": long,
            "link": link,
            "description": desc
        }

        licenses = load_license_definitions()
        # Check for duplicates
        if any(lic["short_name"] == short for lic in licenses):
            flash(f"A license with short name '{short}' already exists.", "danger")
            return render_template("add_license.html", form_data=request.form)

        licenses.append(new_license)
        save_license_definitions(licenses)
        flash(f"License '{long}' ({short}) added successfully.", "success")
        return redirect(url_for("manage_licenses"))
    
    return render_template("add_license.html")
