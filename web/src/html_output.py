import os
import shutil
import json
import markdown # For converting markdown blurb to HTML
from core.src.utils import load_prefs, load_json
from web.src.chapter_utils import format_chapter_heading, get_includes_path # Adjusted for web context, added get_includes_path
from core.src.social_utils import load_links

# Define default.css file for projects (moved from cli/src/html_output.py)
DEFAULT_CSS = """\
body {
    font-family: sans-serif;
    line-height: 1.6;
    margin: 2em auto;
    max-width: 700px;
    padding: 0 1em;
}

h1, h2, h3 {
    font-weight: normal;
}

h1 {
    font-size: 2em;
    margin-bottom: 1em;
}

h2 {
    font-size: 1.5em;
    margin-bottom: 0.8em;
}

h3 {
    font-size: 1.2em;
    margin-bottom: 0.6em;
}

p {
    margin-bottom: 1em;
}

a {
    color: #007bff;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

.chapter-header {
    text-align: center;
    margin-bottom: 2em;
}

.chapter-header img {
    max-width: 100%;
    height: auto;
    margin-bottom: 1em;
}

.chapter-nav {
    text-align: center;
    margin-bottom: 1em;
}

.chapter-nav a {
    margin: 0 0.5em;
}

.chapter-nav .disabled {
    color: #ccc;
}

.download-links {
    text-align: center;
    margin-bottom: 1em;
}

.download-links a {
    margin: 0 0.5em;
}

.share-links, .follow-links {
    text-align: center;
    margin-bottom: 1em;
}

.share-links a, .follow-links a {
    margin: 0 0.5em;
}

.footer {
    text-align: center;
    margin-top: 2em;
    padding-top: 1em;
    border-top: 1px solid #eee;
}
"""

def html_header(prefs, chapter=None, epub_exists=False, pdf_exists=False, chapter_list=None, relative_path_to_root=""):
    features = prefs.get("display_features", {})
    cover_path = prefs.get("cover_image", "")
    story_title = prefs.get("story_title", "")
    author = prefs.get("story_author", "")
    use_titles = features.get("use_chapter_titles", True)

    html = ['<header class="chapter-header">']

    # Cover Image (if enabled)
    if features.get("cover_image", True) and cover_path:
        html.append(f'<img src="{relative_path_to_root}{os.path.basename(cover_path)}" alt="Cover" class="cover" />')

    # Title + Author
    html.append(f'<h1>{story_title}</h1>')
    html.append(f'<h3>{author}</h3>')

    # Chapter Heading (if present and enabled)
    if chapter and use_titles:
        number = chapter["number"]
        heading = chapter["title"]
        chapter_heading = f"Chapter {number}: {heading}" if heading else f"Chapter {number}"
        html.append(f'<h2>{chapter_heading}</h2>')

    # Top chapter Navigation
    if chapter and features.get("chapter_nav_top", True) and chapter_list:
        html.append(html_chapter_nav(chapter, chapter_list, prefs, relative_path_to_root))

    # EPUB/PDF download links
    download_links = []
    if chapter and features.get("epub_link") and epub_exists:
        slug = story_title.lower().replace(" ", "_")
        download_links.append(f'<a href="{relative_path_to_root}download/{slug}_chapter_{chapter["number"]}.epub">EPUB</a>')
    if chapter and features.get("pdf_link") and pdf_exists:
        slug = story_title.lower().replace(" ", "_")
        download_links.append(f'<a href="{relative_path_to_root}download/{slug}_chapter_{chapter["number"]}.pdf">PDF</a>')

    if download_links:
        html.append('<div class="download-links">' + " | ".join(download_links) + '</div>')

    html.append('</header>')
    return "\n".join(html)

def html_chapter_nav(current_chapter, chapter_list, prefs, relative_path_to_root=""):
    features = prefs.get("display_features", {})
    use_titles = features.get("use_chapter_titles", True)

    index = next((i for i, ch in enumerate(chapter_list) if ch["number"] == current_chapter["number"]), None)
    nav_links = []

    # Previous
    if index is not None and index > 0:
        prev = chapter_list[index - 1]
        prev_title = f"Chapter {prev['number']}: {prev['title']}" if use_titles else f"Chapter {prev['number']}"
        nav_links.append(f'<a href="{prev["number"]}.html">&larr; Previous ({prev_title})</a>')
    else:
        nav_links.append('<span class="disabled">&larr; Previous</span>')

    # TOC
    nav_links.append(f'<a href="{relative_path_to_root}index.html">Table of Contents</a>')

    # Next
    if index is not None and index < len(chapter_list) - 1:
        nxt = chapter_list[index + 1]
        next_title = f"Chapter {nxt['number']}: {nxt['title']}" if use_titles else f"Chapter {nxt['number']}"
        nav_links.append(f'<a href="{nxt["number"]}.html">Next ({next_title}) &rarr;</a>')
    else:
        nav_links.append('<span class="disabled">Next &rarr;</span>')

    return f'<nav class="chapter-nav">\n  {" | ".join(nav_links)}\n</nav>'

def html_footer(prefs, chapter=None, chapter_list=None, project_path=None, relative_path_to_root=""):
    try:
        share_links, follow_links, handles = load_links(project_path)
    except (FileNotFoundError, json.JSONDecodeError):
        share_links = []
        follow_links = {}
        handles = {}

    features = prefs.get("display_features", {})
    html = ['<footer class="footer">']

    # Bottom Chapter Navigation
    if chapter and features.get("chapter_nav_bottom", True) and chapter_list:
        html.append(html_chapter_nav(chapter, chapter_list, prefs, relative_path_to_root))

    # Share This Chapter Links
    if chapter and features.get("share_links", True) and share_links:
        html.append('<div class="share-links"><p>Share this chapter:</p>')
        for platform in share_links:
            if platform == "email":
                html.append(f'<a href="mailto:?subject=Check out this chapter">Email</a>')
            elif platform == "x":
                html.append(f'<a href="https://twitter.com/intent/tweet?text=Reading+{prefs["story_title"]}">X</a>')
            elif platform == "mastodon":
                html.append('<a href="#" onclick="alert(\'Toot manually using your Mastodon instance.\')">Mastodon</a>')
            elif platform == "bluesky":
                html.append('<a href="https://bsky.app/">Bluesky</a>')
        html.append('</div>')

    # Discuss This Chapter Link
    if chapter and features.get("discuss_link", True) and chapter.get("discussion"):
        html.append(f'<div class="discussion-link"><a href="{chapter["discussion"]}" target="_blank">Discuss this Chapter</a></div>')

    # Social Follow Links
    if features.get("social_links", True) and follow_links:
        html.append('<div class="follow-links"><p>Follow me:</p>')
        for platform, handle in follow_links.items():
            handle_value = handles.get(platform) # Get handle from handles dict
            if handle_value:
                if platform == "github":
                    url = f"https://github.com/{handle_value}"
                elif platform == "x":
                    url = f"https://x.com/{handle_value}"
                elif platform == "bluesky":
                    url = f"https://bsky.app/profile/{handle_value}.bsky.social"
                elif platform == "mastodon":
                    url = handle_value  # Full URL expected
                else:
                    url = f"https://www.instagram.com/{handle_value}" # Default to Instagram if no specific URL
                html.append(f'<a href="{url}" target="_blank">{platform.title()}</a>')
        html.append('</div>')

    # Copyright
    if features.get("copyright", True):
        html.append(f'<p>&copy; {prefs.get("copyright", "")} {prefs.get("story_author", "")}</p>')

    # License Info
    if features.get("license", True):
        raw_license_data = prefs.get("license", "")
        license_code_id = ""
        license_url_from_pref = None

        if isinstance(raw_license_data, dict):
            license_code_id = raw_license_data.get("id", "")
            license_url_from_pref = raw_license_data.get("url")
        elif isinstance(raw_license_data, str):
            license_code_id = raw_license_data

        license_map = {
            "CC-BY-NC-SA-4.0": "https://creativecommons.org/licenses/by-nc-sa/4.0/"
            # Add more codes here as needed
        }
        license_url = license_url_from_pref if license_url_from_pref else license_map.get(license_code_id, "#")
        html.append(f'<p>Licensed under <a href="{license_url}" target="_blank">{license_code_id}</a></p>')

    html.append('Powered by <a href="https://www.github.com/ironmangary/publine" target="_blank">Publine</a><br>')
    html.append('</footer>')
    return "\n".join(html)

def build_html(project_path, prefs, chapters):
    """Build HTML files for the project."""
    print("\n🛠️ Generating HTML...")
    public_dir = os.path.join(project_path, "public")
    os.makedirs(public_dir, exist_ok=True)
    download_dir = os.path.join(project_path, "download")
    os.makedirs(download_dir, exist_ok=True) # Ensure download dir exists for epub/pdf links

    # Check for styles.css
    style_src = os.path.join(project_path, "includes", "styles.css")
    if not os.path.isfile(style_src):
        print("⚠️  styles.css not found in /includes/")
        # In a web context, we shouldn't prompt. We should just create it.
        with open(style_src, "w", encoding="utf-8") as f:
                f.write(DEFAULT_CSS)
        print("✅ Default stylesheet created.")

    # Copy styles.css
    style_dst = os.path.join(public_dir, "styles.css")
    if os.path.isfile(style_src): # Always copy, potentially overwrite if already exists
        shutil.copyfile(style_src, style_dst)
        print(f"✅ Copied stylesheet to {style_dst}")

    # Copy cover image
    cover_filename = prefs.get("cover_image", "")
    if cover_filename:
        cover_src = os.path.join(project_path, "includes", cover_filename)
        cover_dst = os.path.join(public_dir, os.path.basename(cover_src))
        if os.path.isfile(cover_src):
            shutil.copyfile(cover_src, cover_dst)
            print(f"✅ Copied cover image to {cover_dst}")
        else:
            print(f"⚠️ Cover image file not found: {cover_src}")

    for ch in chapters:
        create_html_chapter_page(ch, chapters, prefs, project_path)
    create_html_index_page(chapters, prefs, project_path)
    print("✅ HTML generation complete.")

def create_html_chapter_page(chapter, chapters, prefs, project_path):
    num = chapter["number"]
    slug = prefs["story_title"].lower().replace(" ", "_")
    includes_path = os.path.join(project_path, "includes", f"chapter_{num}.html")
    output_path = os.path.join(project_path, "public", "chapter", f"{num}.html")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not os.path.exists(includes_path):
        print(f"⚠️ Chapter HTML file not found: {includes_path}. Skipping chapter {num}.")
        return

    with open(includes_path, "r", encoding="utf-8") as f:
        body = f.read()

    chapter_heading = format_chapter_heading(chapter, prefs["display_features"].get("use_chapter_titles", True))
    epub_name = f"{slug}_chapter_{num}.epub"
    epub_path = os.path.join(project_path, "download", epub_name)
    epub_exists = os.path.exists(epub_path)
    pdf_name = f"{slug}_chapter_{num}.pdf"
    pdf_path = os.path.join(project_path, "download", pdf_name)
    pdf_exists = os.path.exists(pdf_path)

    header_block = html_header(prefs, chapter, epub_exists=epub_exists, pdf_exists=pdf_exists, chapter_list=chapters, relative_path_to_root="../")
    footer_block = html_footer(prefs, chapter=chapter, chapter_list=chapters, project_path=project_path, relative_path_to_root="../")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{chapter_heading}</title>
  <link rel="stylesheet" href="../styles.css" />
</head>
<body>
{header_block}
<br>
{body}
<br>
{footer_block}
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Chapter {num} written to {output_path}")

def create_html_index_page(chapters, prefs, project_path):
    toc = "\n".join([
        f'<li><a href="chapter/{ch["number"]}.html">{format_chapter_heading(ch, prefs.get("display_features", {}).get("use_chapter_titles", True))}</a></li>'
        for ch in chapters
    ])

    header_block = html_header(prefs, relative_path_to_root="")
    footer_block = html_footer(prefs, project_path=project_path, relative_path_to_root="")

    blurb_html = ""
    display_features = prefs.get("display_features", {})
    if display_features.get("html_include_blurb", False):
        includes_path = get_includes_path(project_path)
        blurb_filepath = os.path.join(includes_path, "blurb.md")
        if os.path.exists(blurb_filepath):
            with open(blurb_filepath, "r", encoding="utf-8") as f:
                blurb_markdown = f.read()
            # Convert markdown to HTML. The markdown library by default sanitizes by escaping HTML.
            blurb_html = f'<div class="index-blurb">{markdown.markdown(blurb_markdown)}</div><br>'
            print(f"✅ Included blurb from {blurb_filepath}")
        else:
            print(f"⚠️ 'html_include_blurb' is enabled but blurb file not found: {blurb_filepath}")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{prefs["story_title"]} - Table of Contents</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
{header_block}
<br>
<main>
{blurb_html}<center><h3>Table of Contents</h3></center>
<ul>{toc}</ul>
</main>
<br>
{footer_block}
</body>
</html>"""

    out_path = os.path.join(project_path, "public", "index.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ TOC page created: {out_path}")
