import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from core.src.ai_utils import load_ai_settings, save_ai_settings, load_ai_providers

ai_settings_bp = Blueprint('ai_settings_bp', __name__)

@ai_settings_bp.route("/ai_settings", methods=["GET", "POST"])
def ai_settings():
    """
    Handles the AI Settings menu for configuring global AI API key, model, and parameters.
    """
    current_settings = load_ai_settings()
    ai_providers_data = load_ai_providers()
    providers = ai_providers_data.get("providers", [])

    # Add 'is_selected' flag to each model for easier template rendering
    for provider in providers:
        for model in provider.get("models", []):
            model["is_selected"] = (
                current_settings.get("AI_PROVIDER") == provider["name"]
                and current_settings.get("AI_MODEL") == model["name"]
            )

    if request.method == "POST":
        api_key = request.form.get("api_key", "").strip()
        selected_model_id = request.form.get("ai_model_select", "")
        custom_provider = request.form.get("custom_ai_provider", "").strip()
        custom_model_name = request.form.get("custom_ai_model", "").strip()

        temperature = float(request.form.get("temperature", 0.7))
        max_tokens = int(request.form.get("max_tokens", 150))

        # Determine the final provider and model to save
        if selected_model_id == "other":
            provider_to_save = custom_provider if custom_provider else "Other"
            model_to_save = custom_model_name if custom_model_name else "Custom Model"
        else:
            provider_to_save = ""
            model_to_save = ""
            # Find the selected provider and model details from the loaded data
            for p in providers:
                for m in p.get("models", []):
                    if m["id"] == selected_model_id:
                        provider_to_save = p["name"]
                        model_to_save = m["name"]
                        break
                if provider_to_save:
                    break
            
            # If a pre-defined model was selected, but its provider wasn't found (shouldn't happen)
            if not provider_to_save and selected_model_id:
                 flash("Error: Selected model not found in predefined list.", "danger")
                 return redirect(url_for("ai_settings_bp.ai_settings"))


        new_settings = {
            "AI_API_KEY": api_key,
            "AI_PROVIDER": provider_to_save,
            "AI_MODEL": model_to_save,
            "AI_TEMPERATURE": temperature,
            "AI_MAX_TOKENS": max_tokens,
        }

        try:
            save_ai_settings(new_settings)
            flash("AI settings updated successfully!", "success")
        except Exception as e:
            flash(f"Error saving AI settings: {e}", "danger")
        
        return redirect(url_for("ai_settings_bp.ai_settings"))

    known_provider_names = [p["name"] for p in providers] if providers else []
    
    # Determine if an "other" model is currently selected
    is_other_model_selected = False
    if current_settings.get("AI_PROVIDER") and current_settings.get("AI_MODEL"):
        if current_settings["AI_PROVIDER"] not in known_provider_names:
            is_other_model_selected = True

    return render_template(
        "ai_settings.html",
        settings=current_settings,
        providers=providers,
        known_provider_names=known_provider_names,
        is_other_model_selected=is_other_model_selected
    )
