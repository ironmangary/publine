import os
import zipfile
import uuid
from datetime import datetime
from pathlib import Path
from src.utils import load_json, load_prefs
import mimetypes
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def build_epub(project_path):
    project_path = Path(project_path)
    try:
        chapters = load_json(project_path / "data" / "chapters.json")
        prefs = load_prefs(project_path)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading project data: {e}")
        return

    slug = chapters[0].get("story_title", "untitled").lower().replace(" ", "_")
    output_dir = project_path / "public" / "downloads"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{slug}.epub"

    try:
        epub = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
        epub.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        epub.writestr("META-INF/container.xml", '''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>''')

        manifest_items = []
        spine_items = []
        toc_navpoints = []

        for i, chapter in enumerate(chapters, start=1):
            if chapter.get("exclude_from_epub"):
                continue

            num = chapter["number"]
            title = chapter["title"]
            filename = f"chapter{i}.html"
            body = chapter["body"]

            html = get_chapter_html(title, body)
            epub.writestr(f"OEBPS/{filename}", html)
            manifest_items.append(f'<item id="chap{i}" href="{filename}" media-type="application/xhtml+xml"/>')
            spine_items.append(f'<itemref idref="chap{i}"/>')
            toc_navpoints.append(f'''
          <navPoint id="navPoint-{i}" playOrder="{i}">
            <navLabel><text>{title}</text></navLabel>
            <content src="{filename}"/>
          </navPoint>''')

        cover_image_path = project_path / "includes" / prefs.get("cover_image")
        if cover_image_path.exists():
            mimetype, _ = mimetypes.guess_type(str(cover_image_path))
            if mimetype:
                image_filename = "cover." + mimetype.split("/")[1]
                epub.write(str(cover_image_path), f"OEBPS/images/{image_filename}")
                manifest_items.append(f'<item id="cover-image" href="images/{image_filename}" media-type="{mimetype}"/>')
                spine_items.insert(0, '<itemref idref="cover-image"/>')
            else:
                logging.error(f"Unsupported cover image type: {cover_image_path}")

        book_id = str(uuid.uuid4())
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        epub.writestr("OEBPS/content.opf", f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>{chapters[0].get("story_title", "Untitled")}</dc:title>
    <dc:creator>{chapters[0].get("story_author", "Anonymous")}</dc:creator>
    <dc:language>en</dc:language>
    <dc:identifier id="BookId">{book_id}</dc:identifier>
    <dc:date>{now}</dc:date>
  </metadata>
  <manifest>
    {''.join(manifest_items)}
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
  </manifest>
  <spine toc="ncx">
    {''.join(spine_items)}
  </spine>
</package>''')

        epub.writestr("OEBPS/toc.ncx", f'''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="{book_id}"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>{chapters[0].get("story_title", "Untitled")}</text></docTitle>
  <navMap>
    {''.join(toc_navpoints)}
  </navMap>
</ncx>''')

        epub.close()
        print(f"✅ EPUB created at {output_path}")
    except Exception as e:
        logging.error(f"Error generating EPUB: {e}")

def get_chapter_html(title, body):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head><title>{title}</title></head>
  <body>
    <h1>{title}</h1>
    <div>{body}</div>
  </body>
</html>'''
