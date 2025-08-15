from core.src.utils import load_prefs, save_prefs
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def get_html_layout_features(project_path):
    """
    Loads the current HTML layout features from project preferences.
    If no features are set, returns default values.
    """
    project_path = Path(project_path)
    prefs = load_prefs(project_path)
    
    default_features = {
        "use_chapter_titles": True,
        "cover_image": True,
        "chapter_nav_top": True,
        "epub_link": False,
        "pdf_link": False,
        "share_links": True,
        "discuss_link": True,
        "chapter_nav_bottom": True,
        "social_links": True,
        "copyright": True,
        "license": True
    }
    
    # Ensure display_features exists and merge defaults
    features = prefs.setdefault("display_features", default_features.copy())
    
    # Ensure all default features are present if new ones are added later
    for key, value in default_features.items():
        features.setdefault(key, value)
        
    return features

def update_html_layout_features(project_path, form_data):
    """
    Updates the HTML layout features based on form data and saves them to project preferences.
    """
    project_path = Path(project_path)
    prefs = load_prefs(project_path)
    
    features = prefs.setdefault("display_features", {})
    
    # List of all expected HTML layout feature keys
    feature_keys = [
        "use_chapter_titles", "cover_image", "chapter_nav_top", "epub_link", "pdf_link",
        "share_links", "discuss_link", "chapter_nav_bottom", "social_links", "copyright", "license"
    ]

    updated = False
    for key in feature_keys:
        new_value = form_data.get(key) == 'on' # Checkbox value is 'on' if checked, None otherwise
        if features.get(key) != new_value:
            features[key] = new_value
            updated = True
            
    if updated:
        save_prefs(project_path, prefs)
        return True, "HTML layout settings updated successfully!"
    else:
        return False, "No changes detected in HTML layout settings."

def get_epub_layout_features(project_path):
    """
    Loads the current EPUB layout features from project preferences.
    If no features are set, returns default values.
    """
    project_path = Path(project_path)
    prefs = load_prefs(project_path)
    
    default_features = {
        "cover_image": True,
        "embed_fonts": True,
        "generate_toc": True,
        "nav_links": True,
        "license_info": True
    }
    
    # Ensure epub_display_features exists and merge defaults
    features = prefs.setdefault("epub_display_features", default_features.copy())
    
    # Ensure all default features are present if new ones are added later
    for key, value in default_features.items():
        features.setdefault(key, value)
        
    return features

def update_epub_layout_features(project_path, form_data):
    """
    Updates the EPUB layout features based on form data and saves them to project preferences.
    """
    project_path = Path(project_path)
    prefs = load_prefs(project_path)
    
    features = prefs.setdefault("epub_display_features", {})
    
    # List of all expected EPUB layout feature keys
    feature_keys = [
        "cover_image", "embed_fonts", "generate_toc", "nav_links", "license_info"
    ]

    updated = False
    for key in feature_keys:
        new_value = form_data.get(key) == 'on' # Checkbox value is 'on' if checked, None otherwise
        if features.get(key) != new_value:
            features[key] = new_value
            updated = True
            
    if updated:
        save_prefs(project_path, prefs)
        return True, "EPUB layout settings updated successfully!"
    else:
        return False, "No changes detected in EPUB layout settings."

def get_pdf_layout_features(project_path):
    """
    Loads the current PDF layout features from project preferences.
    If no features are set, returns default values.
    """
    project_path = Path(project_path)
    prefs = load_prefs(project_path)

    default_features = {
        "include_title": True,
        "include_author": True,
        "include_cover_image": True,
        "add_page_numbers": True,
        "include_license_block": True,
        "include_copyright": True,
        "embed_fonts": True,
        "page_size": "A4" # Default page size
    }

    # Ensure pdf_display_features exists and merge defaults
    features = prefs.setdefault("pdf_display_features", default_features.copy())

    # Ensure all default features are present if new ones are added later
    for key, value in default_features.items():
        features.setdefault(key, value)

    return features

def update_pdf_layout_features(project_path, form_data):
    """
    Updates the PDF layout features based on form data and saves them to project preferences.
    """
    project_path = Path(project_path)
    prefs = load_prefs(project_path)

    features = prefs.setdefault("pdf_display_features", {})

    # List of all expected PDF layout feature keys (checkboxes)
    checkbox_keys = [
        "include_title", "include_author", "include_cover_image",
        "add_page_numbers", "include_license_block", "include_copyright",
        "embed_fonts"
    ]

    updated = False
    for key in checkbox_keys:
        new_value = form_data.get(key) == 'on'
        if features.get(key) != new_value:
            features[key] = new_value
            updated = True
    
    # Handle page_size separately as it's a select input
    new_page_size = form_data.get("page_size")
    if new_page_size and features.get("page_size") != new_page_size:
        features["page_size"] = new_page_size
        updated = True

    if updated:
        save_prefs(project_path, prefs)
        return True, "PDF layout settings updated successfully!"
    else:
        return False, "No changes detected in PDF layout settings."
