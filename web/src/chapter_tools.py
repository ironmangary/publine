import os
import re # Added for slugification
import logging # Added for logging
# Removed LangChain imports as they are now encapsulated within AIProvider classes
# from langchain_core.documents import Document
# from langchain_core.prompts import PromptTemplate

from core.src.ai_utils import get_ai_provider # Changed import to use the factory function
from web.src.chapter_utils import get_chapter_plain_text_content, save_chapter_summary, list_chapters, get_single_chapter_data

# Configure logging for this module
logger = logging.getLogger(__name__)

def _slugify_for_filename(text):
    """Converts text to a filename-safe slug."""
    text = text.lower()
    text = text.replace(' ', '_')
    text = text.replace('(', '')
    text = text.replace(')', '')
    text = text.replace('/', '_')
    text = re.sub(r'[^a-z0-9_.-]', '', text) # Remove any remaining non-alphanumeric characters
    return text

def get_chapter_tools_options():
    """Returns a list of available chapter tools."""
    return [
        {"name": "Summarize Chapter (AI)", "description": "Generate a summary of a specific chapter using AI.", "id": "summarize_ai"},
        {"name": "Generate Social Media Post (AI)", "description": "Create a social media post for a chapter using AI.", "id": "social_media_ai"},
    ]

def generate_social_media_post_with_ai(project_path, chapter_num, tone, length):
    """
    Generates a social media post for a chapter using AI based on specified tone and length.
    Returns (success, post_text or error_message, None)
    """
    try:
        chapter_title, chapter_text = get_chapter_plain_text_content(project_path, chapter_num)

        if not chapter_text.strip():
            return False, "Chapter content is empty, cannot generate social media post.", None

        # Get the AI provider instance
        ai_provider_instance = get_ai_provider()
        
        # Use the abstraction layer to generate the social post
        post_content = ai_provider_instance.generate_social_post(
            chapter_title=chapter_title,
            chapter_text=chapter_text,
            tone=tone,
            length=length
        )

        return True, post_content.strip(), None
    except ValueError as ve:
        logger.error(f"Configuration Error for social post generation: {ve}")
        return False, f"Configuration Error: {ve}", None
    except ConnectionError as ce: # Catch connection errors from local LLM
        logger.error(f"Connection Error for social post generation: {ce}")
        return False, f"Connection Error: {ce}", None
    except Exception as e:
        logger.error(f"AI social media post generation failed: {e}", exc_info=True)
        return False, f"AI social media post generation failed: {e}", None

def save_social_media_post(project_path, project_slug, chapter_num, post_content, post_length, post_tone):
    """
    Saves the generated social media post to a Markdown file within the project's includes directory.
    Filename format: <slug>_chapter_<#>_<length>_<tone>.md
    """
    includes_path = os.path.join(project_path, "includes")
    os.makedirs(includes_path, exist_ok=True)
    
    slugified_length = _slugify_for_filename(post_length)
    slugified_tone = _slugify_for_filename(post_tone)

    file_name = f"{project_slug}_chapter_{chapter_num}_{slugified_length}_{slugified_tone}.md"
    file_path = os.path.join(includes_path, file_name)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(post_content)
    return file_path

def summarize_chapter_with_ai(project_path, chapter_num):
    """
    Loads a chapter, extracts its plain text, and generates a summary using AI.
    Returns (success, summary_text or error_message, saved_file_path)
    """
    try:
        chapter_title, chapter_text = get_chapter_plain_text_content(project_path, chapter_num)

        if not chapter_text.strip():
            return False, "Chapter content is empty, cannot summarize.", None

        # Get the AI provider instance
        ai_provider_instance = get_ai_provider()

        # Use the abstraction layer to summarize the chapter
        summary_text = ai_provider_instance.summarize_chapter(
            chapter_title=chapter_title,
            chapter_text=chapter_text
        )

        return True, summary_text, None # Return None for path initially, save later
    except ValueError as ve:
        logger.error(f"Configuration Error for summarization: {ve}")
        return False, f"Configuration Error: {ve}", None
    except ConnectionError as ce: # Catch connection errors from local LLM
        logger.error(f"Connection Error for summarization: {ce}")
        return False, f"Connection Error: {ce}", None
    except Exception as e:
        logger.error(f"AI summarization failed: {e}", exc_info=True)
        return False, f"AI summarization failed: {e}", None
