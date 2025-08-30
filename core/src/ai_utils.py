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
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI # Added for Google Gemini
from langchain_core.documents import Document # Added for Document class

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
        "AI_API_KEY": settings.get("AI_API_KEY", ""), # General key, might be overridden by provider-specific
        "OPENAI_API_KEY": settings.get("OPENAI_API_KEY", ""),
        "GOOGLE_API_KEY": settings.get("GOOGLE_API_KEY", ""),
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

def get_llm_and_chain(ai_provider, ai_model, temperature, max_tokens):
    """
    Initializes the appropriate LLM and a summarization chain based on settings.
    Returns (llm, chain) or raises an exception if provider is unsupported or key is missing.
    """
    settings = load_ai_settings()
    llm = None
    
    if ai_provider.lower() == "openai":
        api_key = settings.get("OPENAI_API_KEY") or settings.get("AI_API_KEY")
        if not api_key:
            raise ValueError(f"OpenAI API key not found. Please set OPENAI_API_KEY or AI_API_KEY in your .env file.")
        llm = ChatOpenAI(
            openai_api_key=api_key,
            model_name=ai_model,
            temperature=temperature,
            max_tokens=max_tokens
        )
    elif ai_provider.lower() == "google gemini":
        api_key = settings.get("GOOGLE_API_KEY") or settings.get("AI_API_KEY")
        if not api_key:
            raise ValueError(f"Google API key not found. Please set GOOGLE_API_KEY or AI_API_KEY in your .env file.")
        
        # Resolve the model name to its ID for Google Gemini
        providers_data = load_ai_providers()
        google_models = []
        for provider in providers_data.get("providers", []):
            if provider.get("name").lower() == "google gemini":
                google_models = provider.get("models", [])
                break
        
        model_id = None
        for model_entry in google_models:
            if model_entry.get("name") == ai_model: # Match by name, which is likely stored in .env
                model_id = model_entry.get("id")
                break
        
        if not model_id:
            raise ValueError(f"Google Gemini model '{ai_model}' not found or invalid.")

        llm = ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model_id, # Use the resolved model ID here
            temperature=temperature,
            max_tokens=max_tokens
        )
    # Add other providers here as needed
    else:
        raise ValueError(f"Unsupported AI provider: {ai_provider}")

    # Prompt template for summarization
    summary_template = """You are a professional editor. Your task is to summarize a chapter from a book.
    Provide a concise summary of the chapter, 3-5 sentences long, highlighting key events, important character developments, and the overall tone.
    The summary should capture the essence of the chapter, suitable for a back-cover blurb or an internal review.

    Chapter Title: {chapter_title}

    Chapter Full Text:
    {text}

    CONCISE SUMMARY:"""

    summary_prompt = PromptTemplate(
        template=summary_template,
        input_variables=["chapter_title", "text"]
    )

    # We will use the stuff chain as we are passing the whole chapter text
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=summary_prompt)
    return llm, chain
