import os
from dotenv import dotenv_values, set_key
from core.src.utils import load_json
from core.src.paths import base_dir

# Path to the .env file at the project root
DOTENV_PATH = os.path.join(base_dir, "..", ".env")
# Path to api_providers.json at the project root's 'data' directory
API_PROVIDERS_PATH = os.path.join(base_dir, "..", "data", "api_providers.json")

def load_ai_settings():
    """
    Loads AI settings from the .env file.
    Returns a dictionary of AI settings.
    """
    settings = dotenv_values(DOTENV_PATH)
    # Default values for AI settings
    return {
        "AI_API_KEY": settings.get("AI_API_KEY", ""),
        "AI_PROVIDER": settings.get("AI_PROVIDER", ""),
        "AI_MODEL": settings.get("AI_MODEL", ""),
        "AI_TEMPERATURE": float(settings.get("AI_TEMPERATURE", 0.7)),
        "AI_MAX_TOKENS": int(settings.get("AI_MAX_TOKENS", 150))
    }

def save_ai_settings(settings):
    """
    Saves AI settings to the .env file.
    settings: A dictionary containing AI settings.
    """
    for key, value in settings.items():
        set_key(DOTENV_PATH, key, str(value))

def load_ai_providers():
    """
    Loads available AI providers and models from data/api_providers.json.
    """
    if os.path.exists(API_PROVIDERS_PATH):
        return load_json(API_PROVIDERS_PATH)
    else:
        return {"providers": []}
