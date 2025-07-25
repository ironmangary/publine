import os
import json
from src.utils import load_json, save_json

# 🧭 Follow Links

def load_follow_links(project_path):
    path = os.path.join(project_path, "data", "follow_links.json")
    return load_json(path)

def save_follow_links(project_path, follow_links):
    path = os.path.join(project_path, "data", "follow_links.json")
    save_json(path, follow_links)

# 🔗 Share Links

def load_share_links(project_path):
    path = os.path.join(project_path, "data", "share_links.json")
    return load_json(path)

def save_share_links(project_path, share_links):
    path = os.path.join(project_path, "data", "share_links.json")
    save_json(path, share_links)

# 🛠️ Initialization

def initialize_links(project_path):
    path = os.path.join(project_path, "data")
    os.makedirs(path, exist_ok=True)
    save_follow_links(project_path, {})
    save_share_links(project_path, [])
