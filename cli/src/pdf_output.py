import os
from pathlib import Path
from core.src.utils import load_json, load_prefs
import logging
import json

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def build_pdf(project_path):
    project_path = Path(project_path)
    prefs = load_prefs(project_path)

    if not prefs.get("pdf_enabled"):
        print("PDF generation is disabled for this project.")
        print("To enable it, edit the project's data/prefs.json file and set pdf_enabled to true.")
        return

    try:
        from weasyprint import HTML, CSS
    except ImportError:
        logging.error("WeasyPrint is not installed. Please install it with 'pip install weasyprint' to generate PDFs.")
        return

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
        title = chapter.get('title', 'Untitled Chapter') # Handle missing title
        body = chapter.get('body', '') # Handle missing body
        html_content += f"<h2>{title}</h2><div>{body}</div>"

    try:
        html = HTML(string=html_content, base_url=str(project_path))
        css = CSS(string="body { font-family: sans-serif; }")
        html.write_pdf(str(output_path), stylesheets=[css])
        print(f"✅ PDF exported: {output_path}")
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")

