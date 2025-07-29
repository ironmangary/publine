import os
import zipfile
import uuid
from datetime import datetime
from pathlib import Path
from src.utils import load_json, load_prefs

def build_epub(project_path):
    project_path = Path(project_path)
    chapters_path = project_path / "data" / "chapters.json"
    chapters = load_json(chapters_path)
    prefs = load_prefs(project_path)

    slug = chapters[0].get("story_title", "untitled").lower().replace(" ", "_")
    output_dir = project_path / "public" / "downloads"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{slug}.epub"

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
        epub.write(str(cover_image_path), "OEBPS/images/cover.jpg") # Assumes JPG, adjust if needed
        manifest_items.append('<item id="cover-image" href="images/cover.jpg" media-type="image/jpeg"/>')
        # Add cover image to the spine
        spine_items.insert(0, '<itemref idref="cover-image"/>')


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

def get_chapter_html(title, body):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head><title>{title}</title></head>
  <body>
    <h1>{title}</h1>
    <div>{body}</div>
  </body>
</html>'''
