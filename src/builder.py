# builder.py

import os
import json

def page_header(prefs):
    cover = prefs.get('cover_image', 'cover.jpg')  # fallback image
    return f"""
    <header>
        <center>
            <img class="cover" src="../includes/{cover}" alt="{prefs['story_title']} Cover">
            <h1>{prefs['story_title'].upper()}</h1><br><br>
            <h2>By {prefs['story_author']}</h2>
        </center>
    </header>
    """

def format_chapter_heading(chapter, use_titles=True):
    if use_titles:
        return f"Chapter {chapter['number']}: {chapter['title']}"
    return f"Chapter {chapter['number']}"

def create_chapter_page(chapter, chapters, prefs, project_path):
    import os

    num = chapter["number"]
    slug = prefs["story_title"].lower().replace(" ", "_")
    includes_path = os.path.join(project_path, "includes", f"chapter_{num}.html")
    output_path = os.path.join(project_path, "public", "chapter", f"{num}.html")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(includes_path, "r", encoding="utf-8") as f:
        body = f.read()

    # Heading
    chapter_heading = format_chapter_heading(chapter, prefs.get("use_chapter_titles", True))

    # Navigation logic
    i = next((i for i, ch in enumerate(chapters) if ch["number"] == num), None)
    prev_ch = chapters[i - 1] if i > 0 else None
    next_ch = chapters[i + 1] if i is not None and i < len(chapters) - 1 else None

    nav_links = []
    if prev_ch:
        nav_links.append(f'<a href="{prev_ch["number"]}.html">← Previous</a>')
    else:
        nav_links.append('<span class="disabled">← Previous</span>')

    nav_links.append('<a href="../index.html">Table of Contents</a>')

    if next_ch:
        nav_links.append(f'<a href="{next_ch["number"]}.html">Next →</a>')
    else:
        nav_links.append('<span class="disabled">Next →</span>')

    # Optional EPUB/PDF links
    downloads = []
    epub_name = f"{slug}_chapter_{num}.epub"
    epub_path = os.path.join(project_path, "download", epub_name)
    if os.path.exists(epub_path):
        downloads.append(f'<a href="../download/{epub_name}">EPUB</a>')

    pdf_name = f"{slug}_chapter_{num}.pdf"
    pdf_path = os.path.join(project_path, "download", pdf_name)
    if os.path.exists(pdf_path):
        downloads.append(f'<a href="../download/{pdf_name}">PDF</a>')

    if downloads:
        nav_links.extend(["|"] + downloads)

    nav_block = f'<div class="nav-links">\n  {" | ".join(nav_links)}\n</div>\n'

    # Header block with cover and chapter heading
    cover_image = prefs.get("cover_image", "")
    cover_tag = ""
    if cover_image:
        cover_tag = f'<img src="../{os.path.basename(cover_image)}" alt="Cover" class="cover" />'

    header_block = f"""
<header class="chapter-header">
  {cover_tag}
  <h1>{prefs["story_title"]}</h1>
  <h3>{prefs["story_author"]}</h3>
  <h2>{chapter_heading}</h2>
</header>
"""

    # Discussion link (if present)
    discussion_block = ""
    if chapter.get("post"):
        discussion_block = f'''
<div class="discussion-link">
  <a href="{chapter["post"]}" target="_blank">Discuss this Chapter</a>
</div>
'''

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{chapter_heading}</title>
  <link rel="stylesheet" href="../styles.css" />
</head>
<body>
{header_block}
<br><br>
{nav_block}
<br><br>
{body}
<br><br>
{discussion_block}
{nav_block}
<br><br>
<footer>
  <p>&copy; {prefs.get("copyright", "")} {prefs.get("story_author", "")}</p>
</footer>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Chapter {num} written to {output_path}")

def create_index_page(chapters, prefs, project_path):
    toc = "\n".join([
        f'<li><a href="chapter/{ch["number"]}.html">{format_chapter_heading(ch, prefs["use_chapter_titles"])}</a></li>'
        for ch in chapters
    ])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{prefs["story_title"]} - Table of Contents</title>
    <link rel="stylesheet" href="includes/styles.css">
</head>
<body>
{page_header(prefs)}
<main><center><h3>Table of Contents</h3></center>
<ul>{toc}</ul>
</main>
<footer><br><br>&copy; {prefs['copyright']} {prefs['story_author']}.</footer>
</body>
</html>"""

    out_path = os.path.join(project_path, "public", "index.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ TOC page created: {out_path}")
