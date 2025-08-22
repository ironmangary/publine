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
from web.src.chapter_utils import get_includes_path, ALLOWED_CHAPTER_EXTENSIONS # To get the includes path for file uploads
from web.routes.edit_project import edit_project_bp # Import the new blueprint
from web.routes.choose_license import choose_license_bp # Import the new blueprint
from web.routes.projects import projects_bp # Import the new projects blueprint
from web.routes.layout import layout_bp # Import the new layout blueprint
from web.routes.social_media import social_media_bp # Import the new social media blueprint
from web.routes.chapters import chapters_bp # Import the new chapters blueprint
from web.routes.licenses import licenses_bp # Import the new licenses blueprint
from web.routes.publish import publish_bp # Import the new publish blueprint

UPLOAD_FOLDER = 'uploads' # Temporary folder for uploaded files

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
app.secret_key = 'your_secret_key' # Replace with a strong secret key
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Ensure upload folder exists
app.register_blueprint(edit_project_bp) # Register the new blueprint
app.register_blueprint(choose_license_bp) # Register the new blueprint
app.register_blueprint(projects_bp) # Register the new projects blueprint
app.register_blueprint(layout_bp) # Register the new layout blueprint
app.register_blueprint(social_media_bp) # Register the new social media blueprint
app.register_blueprint(chapters_bp) # Register the new chapters blueprint
app.register_blueprint(licenses_bp) # Register the new licenses blueprint
app.register_blueprint(publish_bp) # Register the new publish blueprint

def allowed_chapter_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_CHAPTER_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/exit", methods=["GET"])
def exit_app():
    return render_template("exit.html")

