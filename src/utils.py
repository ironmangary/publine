import json

def save_prefs(prefs_path, prefs_obj):
    with open(prefs_path, "w", encoding="utf-8") as f:
        json.dump(prefs_obj, f, indent=4, ensure_ascii=False)

def load_prefs(prefs_path):
    with open(prefs_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
