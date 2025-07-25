import os
import json
from src.social_utils import load_links, save_links
from src.utils import load_json, save_json

def choose_follow_links(project_path, socials_path):
    """Allows the user to choose which social media platforms to include follow links for."""
    try:
        share_links, follow_links = load_links(project_path)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading links.json: {e}")
        return

    print("\nChoose which social media platforms to include follow links for.\n")
    print("Press Enter when done.\n")

    while True:
        option_map = {}
        idx = 1
        for platform, handle in follow_links.items():
            print(f"{idx}. {platform.title()} ({handle})")
            option_map[str(idx)] = platform
            idx += 1
        print()

        choice = input("Add or remove platform (or press Enter to finish): ").strip()
        if not choice:
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(follow_links):
            platform = option_map[choice]
            if platform in follow_links:
                del follow_links[platform]
            else:
                handle = input(f"Enter {platform} handle: ").strip()
                follow_links[platform] = handle
        else:
            print("Invalid choice. Try again.\n")

    try:
        save_links(project_path, share_links, follow_links)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error saving links.json: {e}")

