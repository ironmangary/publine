from flask import Blueprint, render_template, request, redirect, url_for, flash
from web.src.licenses import load_license_definitions, save_license_definitions

licenses_bp = Blueprint('licenses_bp', __name__)

@licenses_bp.route("/licenses", methods=["GET"])
def manage_licenses():
    """Displays a list of available licenses and provides options to manage them."""
    licenses = load_license_definitions()
    return render_template("licenses.html", licenses=licenses)

@licenses_bp.route("/licenses/add", methods=["GET", "POST"])
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
        return redirect(url_for("licenses_bp.manage_licenses"))
    
    return render_template("add_license.html", form_data={})
