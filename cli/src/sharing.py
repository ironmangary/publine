import os
import json
from core.src.social_utils import load_links, save_links
from urllib.parse import quote_plus

def choose_share_links(project_path, socials_path):
    # Load global socials.json
    try:
        with open(socials_path, "r", encoding="utf-8") as f:
            platforms = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding socials.json: {e}")
        return

    # Filter platforms that have share_url and handle non-string keys
    shareable = {}
    for k, v in platforms.items():
        if isinstance(k, str) and "share_url" in v:
            shareable[k] = v
        else:
            print(f"Warning: Skipping invalid key in socials.json: {k}. Keys must be strings.")

    share_links, follow_links = load_links(project_path) # Unpack the tuple

    print("\n📢 Currently selected sharing platforms:")
    if share_links: # Use share_links instead of selected
        for s in share_links:
            label = shareable.get(s, {}).get('label', s)
            print(f"  • {label}")
    else:
        print("  (none selected)")

    while True:
        remaining = [p for p in shareable if p not in share_links] # Use share_links
        if not remaining:
            print("✅ All available platforms have been selected.")
            break
        print("\n➕ Choose platforms to enable sharing (press Enter to finish):")
        for i, name in enumerate(remaining, 1):
            print(f"  {i}. {shareable[name]['label']}")
        choice = input("Select platform number (or Enter to finish): ").strip()
        if not choice:
            break
        try:
            idx = int(choice) - 1
            key = remaining[idx]
            if key not in share_links: # Use share_links
                share_links.append(key)
                save_links(project_path, share_links, follow_links)
                print(f"✔️ Enabled sharing via {shareable[key]['label']}")
            else:
                print("❗ Platform already selected.")
        except (IndexError, ValueError):
            print("❌ Invalid choice.")

def resolve_share_urls(title, page_url, selected_platforms, socials_data):
    resolved = {}
    for platform in selected_platforms:
        template = socials_data.get(platform, {}).get("share_url")
        if template:
            encoded_title = quote_plus(title)
            encoded_url = quote_plus(page_url)
            resolved[platform] = template.replace("{title}", encoded_title).replace("{url}", encoded_url)
    return resolved
