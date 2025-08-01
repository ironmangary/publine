import os
import json
from core.src.utils import load_json, save_json

def load_links(project_path):
    path = os.path.join(project_path, "data", "links.json")
    try:
        links = load_json(path)
        return links.get("share", []), links.get("follow", {}), links.get("handles", {})
    except FileNotFoundError:
        return [], {}, {}


def save_links(project_path, share_links, follow_links, handles):
    path = os.path.join(project_path, "data", "links.json")
    data = {"share": share_links, "follow": follow_links, "handles": handles}
    save_json(path, data)


def initialize_links(project_path):
    path = os.path.join(project_path, "data")
    os.makedirs(path, exist_ok=True)
    save_links(project_path, [], {}, {})

