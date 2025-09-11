import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from core.src.ai_utils import load_ai_settings, save_ai_settings
from core.src.utils import load_ai_providers

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
            # Special handling for Local LLM selection
            if provider["name"] == "Local LLM" and current_settings.get("AI_PROVIDER") == "Local LLM":
                model["is_selected"] = True
            else:
                model["is_selected"] = (
                    current_settings.get("AI_PROVIDER") == provider["name"]
                    and current_settings.get("AI_MODEL") == model["name"]
                )

    if request.method == "POST":
        api_key = request.form.get("api_key", "").strip()
        selected_model_id = request.form.get("ai_model_select", "")
        
        # Fields for "Other" provider
        custom_provider = request.form.get("custom_ai_provider", "").strip()
        custom_model_name = request.form.get("custom_ai_model", "").strip()

        # Fields for "Local LLM" provider
        local_llm_api_base = request.form.get("local_llm_api_base", "").strip()
        local_ai_model_name = request.form.get("local_ai_model", "").strip() # Changed name

        temperature = float(request.form.get("temperature", 0.7))
        max_tokens = int(request.form.get("max_tokens", 150))

        provider_to_save = ""
        model_to_save = "" # This will be AI_MODEL in .env for non-local providers
        local_ai_model_to_save = "" # This will be LOCAL_AI_MODEL in .env for local provider
        local_llm_api_base_to_save = "" # This will be LOCAL_LLM_API_BASE in .env for local provider

        if selected_model_id == "local-llm":
            provider_to_save = "local"
            model_to_save = "" # Clear AI_MODEL if local LLM is selected
            local_ai_model_to_save = local_ai_model_name if local_ai_model_name else ""
            local_llm_api_base_to_save = local_llm_api_base
        elif selected_model_id == "other":
            provider_to_save = custom_provider if custom_provider else "Other"
            model_to_save = custom_model_name if custom_model_name else "Custom Model"
            local_ai_model_to_save = "" # Clear LOCAL_AI_MODEL if other is selected
            local_llm_api_base_to_save = "" # Clear LOCAL_LLM_API_BASE if other is selected
        else:
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
            
            local_ai_model_to_save = "" # Clear LOCAL_AI_MODEL if a specific provider model is selected
            local_llm_api_base_to_save = "" # Clear LOCAL_LLM_API_BASE if a specific provider model is selected


        new_settings = {
            "AI_API_KEY": api_key,
            "AI_PROVIDER": provider_to_save,
            "AI_MODEL": model_to_save, # This will store the generic model for non-local providers
            "AI_TEMPERATURE": temperature,
            "AI_MAX_TOKENS": max_tokens,
            "LOCAL_LLM_API_BASE": local_llm_api_base_to_save, # Add this to new_settings
            "LOCAL_AI_MODEL": local_ai_model_to_save, # Add this to new_settings
        }

        try:
            save_ai_settings(new_settings)
            flash("AI settings updated successfully!", "success")
        except Exception as e:
            flash(f"Error saving AI settings: {e}", "danger")
        
        return redirect(url_for("ai_settings_bp.ai_settings"))

    # Determine which special fields should be visible
    is_other_model_selected = False
    is_local_llm_selected = False
    if current_settings.get("AI_PROVIDER") == "local":
        is_local_llm_selected = True
    elif current_settings.get("AI_PROVIDER") and current_settings.get("AI_PROVIDER") not in [p["name"] for p in providers]:
        is_other_model_selected = True
    
    # Pass local LLM specific settings for pre-filling
    local_llm_api_base_value = current_settings.get("LOCAL_LLM_API_BASE", "")
    local_ai_model_value = current_settings.get("LOCAL_AI_MODEL", "") # New value name, from the .env key

    return render_template(
        "ai_settings.html",
        settings=current_settings,
        providers=providers,
        is_other_model_selected=is_other_model_selected,
        is_local_llm_selected=is_local_llm_selected,
        local_llm_api_base_value=local_llm_api_base_value,
        local_ai_model_value=local_ai_model_value # New value to pass
    )
