import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def build_pdf(project_path, prefs, chapters):
    if not prefs.get("pdf_enabled"):
        logging.info("PDF generation is disabled for this project.")
        return None

    try:
        from weasyprint import HTML, CSS
    except ImportError:
        logging.error("WeasyPrint is not installed. Please see documentation for installation instructions.")
        return None

    project_path = Path(project_path)
    pdf_prefs = prefs.get("pdf_layout", {})

    slug = prefs.get("story_title", "untitled").lower().replace(" ", "_")
    output_dir = project_path / "public" / "downloads"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{slug}.pdf"

    html_content = "<html><head><title>{title}</title></head><body>".format(title=prefs.get("story_title", ""))

    # Cover Image
    if pdf_prefs.get("include_cover_image", True):
        cover_image_path_str = prefs.get("cover_image")
        if cover_image_path_str:
            cover_image_path = project_path / "includes" / cover_image_path_str
            if cover_image_path.exists():
                html_content += f'<img src="{cover_image_path.as_uri()}" alt="Cover Image" style="width:100%;height:auto;">'
            else:
                logging.warning(f"Cover image not found at {cover_image_path}")

    # Title and Author
    if pdf_prefs.get("include_title", True):
        html_content += f'<h1>{prefs.get("story_title", "")}</h1>'
    if pdf_prefs.get("include_author", True):
        html_content += f'<h2>{prefs.get("story_author", "")}</h2>'

    # Chapters
    for chapter in chapters:
        if chapter.get("exclude_from_pdf"):
            continue
        
        num = chapter["number"]
        title = chapter.get('title', 'Untitled Chapter')
        chapter_content_path = project_path / "includes" / f"chapter_{num}.html"
        
        if not chapter_content_path.exists():
            logging.warning(f"Chapter content for chapter {num} not found at {chapter_content_path}. Skipping.")
            continue

        body = chapter_content_path.read_text(encoding="utf-8")
        html_content += f"<h2>{title}</h2><div>{body}</div>"

    html_content += "</body></html>"

    try:
        html = HTML(string=html_content, base_url=str(project_path))
        
        # Basic CSS
        css_string = "body { font-family: sans-serif; } h1, h2 { text-align: center; }"
        
        # Page Size
        page_size = pdf_prefs.get("page_size", "A4")
        css_string += f"@page {{ size: {page_size}; }}"

        # Other options can be added here as CSS rules
        if pdf_prefs.get("add_page_numbers"):
            css_string += """@page { @bottom-center { content: "Page " counter(page); } }"""

        css = CSS(string=css_string)
        html.write_pdf(str(output_path), stylesheets=[css])
        logging.info(f"PDF exported: {output_path}")
        return str(output_path)
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        return None
