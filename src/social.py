import os
import json
from src.social_utils import load_follow_links, save_follow_links

def choose_follow_links(project_path, socials_path):
    # Load socials.json (the global template)
    with open(socials_path, "r", encoding="utf-8") as f:
        platforms = json.load(f)

    # Load existing follow_links from links.json
    follow_links = load_follow_links(project_path)

    print("\n📌 Existing follow links:")
    for name, handle in follow_links.items():
        url_template = platforms.get(name, {}).get("follow_url")
        label = platforms.get(name, {}).get("label", name)
        if url_template:
            print(f"  • {label}: {url_template.replace('{handle}', handle)}")
    if not follow_links:
        print("  (none yet)")

    # Filter out already-added platforms
    remaining = [p for p in platforms if p not in follow_links and "follow_url" in platforms[p]]
    if not remaining:
        print("\n✅ All followable platforms already selected.")
        return

    while remaining:
        print("\n➕ Add a platform (or press Enter to finish):")
        for i, name in enumerate(remaining, 1):
            print(f"  {i}. {platforms[name].get('label', name)}")

        choice = input("Choose a platform by number (or Enter to finish): ").strip()
        if not choice:
            break
        try:
            index = int(choice) - 1
            key = remaining[index]
            label = platforms[key].get("label", key)
            handle = input(f"Enter your {label} handle (no @ needed): ").strip()
            if handle:
                follow_links[key] = handle
                save_follow_links(project_path, follow_links)  # Saves to links.json
                print(f"✔️  Added {label}: {handle}")
                remaining.pop(index)  # Remove selected platform from remaining
            else:
                print("⚠️  No handle entered.")
        except (IndexError, ValueError):
            print("❌ Invalid choice.")
