import json
import os

def load_prefs(project_path):
    prefs_path = os.path.join(project_path, "data", "prefs.json")
    with open(prefs_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_prefs(project_path, prefs_obj):
    prefs_path = os.path.join(project_path, "data", "prefs.json")
    with open(prefs_path, "w", encoding="utf-8") as f:
        json.dump(prefs_obj, f, indent=4, ensure_ascii=False)

def load_json(project_path, filename):
    path = os.path.join(project_path, "data", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(project_path, filename, data):
    path = os.path.join(project_path, "data", filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_follow_links(project_path):
    path = os.path.join(project_path, "data", "follow_links.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_share_links(project_path):
    path = os.path.join(project_path, "data", "share_links.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
