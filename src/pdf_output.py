import os
from pathlib import Path
from src.utils import load_json
from weasyprint import HTML, CSS
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def build_pdf(project_path):
    project_path = Path(project_path)
    try:
        chapters = load_json(project_path / "data" / "chapters.json")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading chapter data: {e}")
        return

    output_dir = project_path / "public" / "downloads"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "book.pdf"

    html_content = ""
    for chapter in chapters:
        if chapter.get("exclude_from_pdf"):
            continue
        html_content += f"<h2>{chapter['title']}</h2><div>{chapter['body']}</div>"

    try:
        html = HTML(string=html_content, base_url=str(project_path))
        css = CSS(string="body { font-family: sans-serif; }")
        html.write_pdf(str(output_path), stylesheets=[css])
        print(f"✅ PDF exported: {output_path}")
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")

