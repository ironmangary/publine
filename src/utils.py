import json
import os

def load_prefs(project_path):
    prefs_path = os.path.join(project_path, "data", "prefs.json")
    try:
        with open(prefs_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_prefs(project_path, prefs_obj):
    prefs_path = os.path.join(project_path, "data", "prefs.json")
    os.makedirs(os.path.dirname(prefs_path), exist_ok=True)
    with open(prefs_path, "w", encoding="utf-8") as f:
        json.dump(prefs_obj, f, indent=4, ensure_ascii=False)

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_follow_links(project_path):
    path = os.path.join(project_path, "data", "follow_links.json")
    return load_json(path)

def load_share_links(project_path):
    path = os.path.join(project_path, "data", "share_links.json")
    return load_json(path)
