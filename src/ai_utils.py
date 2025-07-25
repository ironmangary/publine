import os
from src.utils import load_json, save_json
from src.paths import base_dir

def get_api_config_path(base_dir):
    return os.path.join(base_dir, "data", "api.json")

def load_api_config():
    path = get_api_config_path(base_dir)
    if os.path.exists(path):
        return load_json(path)
    else:
        return {}

def save_api_config(config):
    path = get_api_config_path(base_dir)
    save_json(path, config)
