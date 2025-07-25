import os
import json
from src.utils import load_json, save_json 

# 🧭 Follow Links

"""Load follow_links.json from the project's data directory."""
def load_follow_links(project_path):
    path = os.path.join(project_path, "data", "links.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_follow_links(project_path, follow_links):
    """Save links.json to the project's data directory."""
    os.makedirs(os.path.join(project_path, "data"), exist_ok=True)
    path = os.path.join(project_path, "data", "links.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(follow_links, f, indent=2, ensure_ascii=False)

# 🔗 Share Links

def load_share_links(project_path):
    """Load the share_links section from links.json."""
    path = os.path.join(project_path, "data", "links.json")
    data = load_json(path)
    return data.get("share_links", [])

def save_share_links(project_path, share_links):
    """Update the share_links section in links.json."""
    path = os.path.join(project_path, "data", "links.json")
    data = load_json(path, "links.json")
    data["share_links"] = share_links
    save_json(path, data)

# 🛠️ Initialization

def initialize_links(project_path):
    """Create a default links.json if it doesn't exist."""
    os.makedirs(os.path.join(project_path, "data"), exist_ok=True)
    path = os.path.join(project_path, "data", "links.json")
    if not os.path.exists(path):
        default_links = {
            "follow_links": {},
            "share_links": []
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_links, f, indent=2, ensure_ascii=False)
