from langchain_core.documents import Document

from core.src.ai_utils import load_ai_settings, get_llm_and_chain
from web.src.chapter_utils import get_chapter_plain_text_content, save_chapter_summary, list_chapters

def get_chapter_tools_options():
    """Returns a list of available chapter tools."""
    return [
        {"name": "Summarize Chapter (AI)", "description": "Generate a summary of a specific chapter using AI.", "id": "summarize_ai"},
        {"name": "Generate Social Media Post (AI)", "description": "Create a social media post for a chapter using AI.", "id": "social_media_ai"},
    ]

def summarize_chapter_with_ai(project_path, chapter_num):
    """
    Loads a chapter, extracts its plain text, and generates a summary using LangChain.
    Returns (success, summary_text or error_message, saved_file_path)
    """
    try:
        chapter_title, chapter_text = get_chapter_plain_text_content(project_path, chapter_num)

        if not chapter_text.strip():
            return False, "Chapter content is empty, cannot summarize.", None

        # Load AI settings
        ai_settings = load_ai_settings()
        ai_provider = ai_settings.get("AI_PROVIDER")
        ai_model = ai_settings.get("AI_MODEL")
        temperature = ai_settings.get("AI_TEMPERATURE")
        max_tokens = ai_settings.get("AI_MAX_TOKENS")

        if not ai_provider or not ai_model:
            return False, "AI provider or model not configured in .env file.", None

        # Initialize LLM and summarization chain
        llm, summarize_chain = get_llm_and_chain(ai_provider, ai_model, temperature, max_tokens)

        # LangChain expects a list of Document objects
        # The 'stuff' chain type takes the entire text as one document.
        docs = [Document(page_content=chapter_text)]

        # Run the summarization chain
        summary = summarize_chain.invoke(
            {"input_documents": docs, "chapter_title": chapter_title},
            return_only_outputs=True
        )
        summary_text = summary["output_text"]

        return True, summary_text, None # Return None for path initially, save later
    except ValueError as ve:
        return False, f"Configuration Error: {ve}", None
    except FileNotFoundError as fnfe:
        return False, f"File Error: {fnfe}", None
    except Exception as e:
        # Catch any other exceptions from LangChain, API calls, etc.
        return False, f"AI summarization failed: {e}", None
