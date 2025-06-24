import os
import json
from src.utils import load_prefs, save_prefs
from urllib.parse import quote_plus

def choose_share_links(project_data_dir, socials_path):
    share_path = os.path.join(project_data_dir, "share_links.json")

    # Load global socials.json
    with open(socials_path, "r", encoding="utf-8") as f:
        platforms = json.load(f)

    # Filter platforms that have share_url
    shareable = {k: v for k, v in platforms.items() if "share_url" in v}
    selected = load_prefs(share_path) if os.path.exists(share_path) else []

    print("\n📢 Currently selected sharing platforms:")
    if selected:
        for s in selected:
            print(f"  • {shareable[s]['label']}")
    else:
        print("  (none selected)")

    print("\n➕ Choose platforms to enable sharing (press Enter to finish):")
    remaining = [p for p in shareable if p not in selected]
    for i, name in enumerate(remaining, 1):
        print(f"  {i}. {shareable[name]['label']}")

    while True:
        choice = input("Select platform number (or Enter to finish): ").strip()
        if not choice:
            break
        try:
            idx = int(choice) - 1
            key = remaining[idx]
            selected.append(key)
            save_prefs(share_path, selected)
            print(f"✔️ Enabled sharing via {shareable[key]['label']}")
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

