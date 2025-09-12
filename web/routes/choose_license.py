from flask import Blueprint, render_template, request, redirect, url_for, flash

from web.src.manage_projects import get_single_project_details
from web.src.licenses import load_license_definitions
from core.src.utils import load_prefs, save_prefs

# Create a Blueprint for the choose_license route
choose_license_bp = Blueprint('choose_license_bp', __name__)

@choose_license_bp.route("/project/<slug>/choose_license", methods=["GET", "POST"])
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
            return redirect(url_for("projects_bp.project_dashboard", slug=slug))
        else:
            flash("Invalid license selected.", "danger")

    return render_template("choose_project_license.html", project=project, licenses=licenses, current_license_short_name=current_license_short_name)
