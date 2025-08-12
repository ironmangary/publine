import os
import json

LICENSES_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'licenses.json'))

def load_license_definitions():
    """Loads license definitions from the global licenses.json file."""
    try:
        with open(LICENSES_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # If licenses.json doesn't exist, return an empty list
        return []
    except json.JSONDecodeError:
        # Handle malformed JSON
        return []

def save_license_definitions(licenses):
    """Saves license definitions to the global licenses.json file."""
    with open(LICENSES_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(licenses, f, indent=4, ensure_ascii=False)
