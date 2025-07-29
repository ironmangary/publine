import os
from pathlib import Path
from src.utils import load_json
from weasyprint import HTML, CSS

def build_pdf(project_path):
    project_path = Path(project_path)
    chapters_path = project_path / "data" / "chapters.json"
    chapters = load_json(chapters_path)

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
        css = CSS(string="body { font-family: sans-serif; }") # Add basic CSS styling
        html.write_pdf(str(output_path), stylesheets=[css])
        print(f"✅ PDF exported: {output_path}")
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")

