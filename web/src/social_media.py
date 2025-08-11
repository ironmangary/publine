import os
import json
from urllib.parse import quote_plus
from core.src.social_utils import load_links, save_links

# Define the path to data/socials.json relative to this module
# This module is in web/src, socials.json is in data/
SOCIALS_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'socials.json'))


def get_social_platforms():
    """Loads and returns the global social media platform definitions."""
    try:
        with open(SOCIALS_DATA_PATH, "r", encoding="utf-8") as f:
            platforms = json.load(f)
        # Filter out any non-string keys or malformed entries
        return {k: v for k, v in platforms.items() if isinstance(k, str) and isinstance(v, dict)}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading socials.json: {e}")
        return {}

def get_project_social_links(project_path):
    """Loads project-specific social links and handles."""
    share_links, follow_links, handles = load_links(project_path)
    return {
        "share": share_links,
        "follow": follow_links, # This is a dict of platform_key: empty_string placeholder
        "handles": handles # This is a dict of platform_key: handle_string
    }

def update_follow_link(project_path, platform_key, handle):
    """Adds or updates a follow link with a specific handle."""
    share_links, follow_links, handles = load_links(project_path)
    
    # Ensure the platform exists in global definitions
    all_platforms = get_social_platforms()
    if platform_key not in all_platforms:
        return False, "Platform not recognized."

    # Update follow_links (which are just keys for the UI, handle is in `handles`) and handles
    # follow_links stores keys for platforms that have a follow link, actual handle is in `handles`
    follow_links[platform_key] = ""
    handles[platform_key] = handle.strip()

    save_links(project_path, share_links, follow_links, handles)
    return True, f"Follow link for {all_platforms[platform_key].get('label', platform_key)} updated."

def delete_follow_link(project_path, platform_key):
    """Deletes a follow link."""
    share_links, follow_links, handles = load_links(project_path)
    
    if platform_key in follow_links:
        del follow_links[platform_key]
    if platform_key in handles:
        del handles[platform_key]
    
    save_links(project_path, share_links, follow_links, handles)
    return True, "Follow link deleted."

def update_share_link_status(project_path, platform_key, enable):
    """Enables or disables a share link."""
    share_links, follow_links, handles = load_links(project_path)
    
    all_platforms = get_social_platforms()
    if platform_key not in all_platforms or "share_url" not in all_platforms[platform_key]:
        return False, "Platform not recognized or does not support sharing."

    if enable:
        if platform_key not in share_links:
            share_links.append(platform_key)
            share_links.sort() # Keep consistent order
            message = f"Sharing enabled for {all_platforms[platform_key].get('label', platform_key)}."
        else:
            message = f"Sharing already enabled for {all_platforms[platform_key].get('label', platform_key)}."
    else:
        if platform_key in share_links:
            share_links.remove(platform_key)
            message = f"Sharing disabled for {all_platforms[platform_key].get('label', platform_key)}."
        else:
            message = f"Sharing already disabled for {all_platforms[platform_key].get('label', platform_key)}."
    
    save_links(project_path, share_links, follow_links, handles)
    return True, message

def resolve_share_urls(project_path, chapter_title, page_url):
    """
    Resolves actual share URLs for enabled platforms.
    This function expects project_path to load enabled share links.
    """
    share_links, _, _ = load_links(project_path)
    socials_data = get_social_platforms()

    resolved = {}
    for platform in share_links:
        template = socials_data.get(platform, {}).get("share_url")
        if template:
            encoded_title = quote_plus(chapter_title)
            encoded_url = quote_plus(page_url)
            resolved[platform] = template.replace("{title}", encoded_title).replace("{url}", encoded_url)
    return resolved
