import os
import json
from src.utils import load_prefs, save_prefs

def choose_follow_links(project_data_dir, socials_path):
    follow_path = os.path.join(project_data_dir, "follow_links.json")

    # Load socials.json (the global template)
    with open(socials_path, "r", encoding="utf-8") as f:
        platforms = json.load(f)

    # Load existing follow_links.json (if any)
    if os.path.exists(follow_path):
        follow_links = load_prefs(follow_path)
    else:
        follow_links = {}

    print("\n📌 Existing follow links:")
    for name, handle in follow_links.items():
        url_template = platforms.get(name, {}).get("follow_url")
        if url_template:
            print(f"  • {platforms[name]['label']}: {url_template.replace('{handle}', handle)}")
    if not follow_links:
        print("  (none yet)")

    # Filter out already-added platforms
    remaining = [p for p in platforms if p not in follow_links and "follow_url" in platforms[p]]
    if not remaining:
        print("\n✅ All followable platforms already selected.")
        return

    print("\n➕ Add a platform (or press Enter to finish):")
    for i, name in enumerate(remaining, 1):
        print(f"  {i}. {platforms[name]['label']}")

    while True:
        choice = input("Choose a platform by number (or Enter to finish): ").strip()
        if not choice:
            break
        try:
            index = int(choice) - 1
            key = remaining[index]
            label = platforms[key]["label"]
            handle = input(f"Enter your {label} handle (no @ needed): ").strip()
            if handle:
                follow_links[key] = handle
                save_prefs(follow_path, follow_links)
                print(f"✔️  Added {label}: {handle}")
            else:
                print("⚠️  No handle entered.")
        except (IndexError, ValueError):
            print("❌ Invalid choice.")
