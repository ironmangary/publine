import os
import logging
from dotenv import dotenv_values, set_key
from core.src.paths import base_dir
from core.src.ai_providers import OpenAIProvider, LocalLLMProvider, AIProvider
from core.src.utils import load_json # load_json is still used by load_ai_settings
from dotenv import dotenv_values, set_key # Added back dotenv imports

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to the .env file at the project root
DOTENV_PATH = os.path.join(base_dir, "..", ".env")

def load_ai_settings():
    """
    Loads AI settings from the .env file.
    Returns a dictionary of AI settings.
    """
    settings = dotenv_values(DOTENV_PATH)
    # Default values for AI settings
    return {
        "AI_API_KEY": settings.get("AI_API_KEY", ""), # General key, might be overridden by provider-specific
        "OPENAI_API_KEY": settings.get("OPENAI_API_KEY", ""),
        "GOOGLE_API_KEY": settings.get("GOOGLE_API_KEY", ""),
        "AI_PROVIDER": settings.get("AI_PROVIDER", ""),
        "AI_MODEL": settings.get("AI_MODEL", ""),
        "AI_TEMPERATURE": float(settings.get("AI_TEMPERATURE", 0.7)),
        "AI_MAX_TOKENS": int(settings.get("AI_MAX_TOKENS", 150)),
        "LOCAL_AI_ENDPOINT": settings.get("LOCAL_LLM_API_BASE", ""), # Changed from LOCAL_AI_ENDPOINT to LOCAL_LLM_API_BASE
        "LOCAL_AI_MODEL": settings.get("LOCAL_AI_MODEL", "")
    }

def save_ai_settings(settings):
    """
    Saves AI settings to the .env file.
    settings: A dictionary containing AI settings.
    """
    for key, value in settings.items():
        set_key(DOTENV_PATH, key, str(value))

def get_ai_provider() -> AIProvider:
    """
    Reads AI settings from the .env file and returns an instantiated AIProvider.
    Raises ValueError if the provider is unsupported or configuration is missing.
    """
    settings = load_ai_settings()
    provider_name = settings.get("AI_PROVIDER", "").lower()

    if provider_name in ["openai", "google gemini"]:
        logger.info(f"Initializing OpenAIProvider for {provider_name}.")
        return OpenAIProvider(settings)
    elif provider_name == "local":
        logger.info("Initializing LocalLLMProvider.")
        return LocalLLMProvider(settings)
    else:
        raise ValueError(f"Unsupported AI provider specified in .env: {provider_name}. "
                         "Please choose 'openai', 'google gemini', or 'local'.")
