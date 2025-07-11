from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
from pathlib import Path
from src.utils import load_prefs, load_json

def build_pdf(project_path):
    project_path = Path(project_path)
    prefs = load_prefs(project_path)
    chapters = load_json(project_path, "chapters.json")

    slug = prefs.get("story_title", "untitled").lower().replace(" ", "_")
    output_dir = project_path / "public" / "downloads"
    output_dir.mkdir(parents=True, exist_ok=True)

    for chapter in chapters:
        if chapter.get("exclude_from_pdf"):
            continue

        num = chapter["number"]
        title = chapter["title"]
        includes_path = project_path / "includes" / f"chapter_{num}.html"
        pdf_path = output_dir / f"{slug}_chapter_{num}.pdf"

        if not includes_path.exists():
            print(f"❌ Missing: {includes_path}")
            continue

        with open(includes_path, encoding="utf-8") as f:
            body = f.read()

        # Strip out HTML tags for now — plain text rendering
        text_content = strip_html_tags(body)

        c = canvas.Canvas(str(pdf_path), pagesize=LETTER)
        width, height = LETTER
        margin = inch
        y = height - margin

        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin, y, title)
        y -= 0.5 * inch

        c.setFont("Helvetica", 12)
        for line in text_content.splitlines():
            line = line.strip()
            if not line: continue
            if y < margin:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", 12)
            c.drawString(margin, y, line)
            y -= 14

        c.save()
        print(f"✅ PDF exported: {pdf_path}")

def strip_html_tags(html):
    import re
    # Basic removal of HTML tags — good enough for initial PDF export
    return re.sub(r"<[^>]+>", "", html)
