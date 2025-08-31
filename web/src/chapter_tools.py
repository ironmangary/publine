import os
import re # Added for slugification
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

from core.src.ai_utils import load_ai_settings, get_llm_and_chain
from web.src.chapter_utils import get_chapter_plain_text_content, save_chapter_summary, list_chapters, get_single_chapter_data

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

        # Load AI settings
        ai_settings = load_ai_settings()
        ai_provider = ai_settings.get("AI_PROVIDER")
        ai_model = ai_settings.get("AI_MODEL")
        # For social media posts, we might want a slightly lower temperature for more direct output
        temperature = ai_settings.get("AI_TEMPERATURE", 0.7) 
        max_tokens = ai_settings.get("AI_MAX_TOKENS", 500) # Max tokens for a post

        if not ai_provider or not ai_model:
            return False, "AI provider or model not configured in .env file.", None
        
        template = """
        You are an expert social media manager. Your task is to draft a promotional social media post for a chapter of a book.
        
        Chapter Title: {chapter_title}
        Chapter Content: {chapter_content}
        
        Desired Tone: {tone}
        Desired Length: {length}
        
        Please draft a compelling social media post based on the chapter content, adhering to the specified tone and length. 
        Focus on engaging potential readers and highlighting key aspects or mysteries of the chapter without giving away major spoilers.
        Do not include hashtags or emojis unless explicitly asked for in the tone/length, just the post content itself.
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["chapter_title", "chapter_content", "tone", "length"]
        )

        # Initialize LLM and chain
        llm, _ = get_llm_and_chain(ai_provider, ai_model, temperature, max_tokens)
        llm_chain = prompt | llm

        # Run the generation chain
        post_response = llm_chain.invoke({ # Changed variable name to avoid confusion with post_content string
            "chapter_title": chapter_title,
            "chapter_content": chapter_text,
            "tone": tone,
            "length": length
        })

        # Access the content attribute of the AIMessage object
        post_content = post_response.content

        return True, post_content.strip(), None
    except ValueError as ve:
        return False, f"Configuration Error: {ve}", None
    except FileNotFoundError as fnfe:
        return False, f"File Error: {fnfe}", None
    except Exception as e:
        # Catch any other exceptions from LangChain, API calls, etc.
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
        summary_response = summarize_chain.invoke( # Changed variable name
            {"input_documents": docs, "chapter_title": chapter_title},
            return_only_outputs=True
        )
        summary_text = summary_response["output_text"]

        return True, summary_text, None # Return None for path initially, save later
    except ValueError as ve:
        return False, f"Configuration Error: {ve}", None
    except FileNotFoundError as fnfe:
        return False, f"File Error: {fnfe}", None
    except Exception as e:
        # Catch any other exceptions from LangChain, API calls, etc.
        return False, f"AI summarization failed: {e}", None
