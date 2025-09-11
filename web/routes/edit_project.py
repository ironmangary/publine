from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename # This import is not directly used in the route but good practice if internal functions were to use it

from web.src.manage_projects import get_single_project_details, update_project_details

# Define allowed extensions for file uploads specific to this route's needs
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
ALLOWED_CSS_EXTENSIONS = {'css'}

# Helper functions for file validation
def allowed_image_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def allowed_css_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_CSS_EXTENSIONS

# Create a Blueprint for the edit_project route
edit_project_bp = Blueprint('edit_project_bp', __name__)

@edit_project_bp.route("/edit_project/<slug>", methods=["GET", "POST"])
def edit_project(slug):
    project = get_single_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("manage_projects"))

    if request.method == "POST":
        new_title = request.form["title"]
        new_author = request.form["author"]
        new_copyright_year = request.form["copyright_year"]
        pdf_enabled = request.form.get('pdf_enabled') == 'on'

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
            pdf_enabled, cover_image_file, custom_css_file
        )
        if success:
            flash(message, "success")
            return redirect(url_for("projects_bp.manage_projects"))
        else:
            flash(message, "error")
    
    return render_template("edit_project.html", project=project)
