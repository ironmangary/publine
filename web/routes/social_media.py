from flask import Blueprint, render_template, request, redirect, url_for, flash
from web.src import chapters as web_chapters
from web.src import social_media as web_social_media

social_media_bp = Blueprint('social_media_bp', __name__)

@social_media_bp.route("/project/<slug>/social_media", methods=["GET", "POST"])
def social_media_management(slug):
    project = web_chapters.get_project_details(slug)
    if not project:
        flash(f"Project '{slug}' not found.", "error")
        return redirect(url_for("projects_bp.manage_projects"))

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
        return redirect(url_for("social_media_bp.social_media_management", slug=slug))

    # For GET request or after POST redirect
    return render_template(
        "social_media.html",
        project=project,
        all_social_platforms=all_social_platforms,
        project_social_links=project_social_links
    )
