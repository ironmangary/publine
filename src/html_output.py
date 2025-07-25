import os
import shutil
import json
from src.utils import load_prefs, save_prefs, load_json
from src.chapter_utils import format_chapter_heading
from src.social_utils import load_follow_links, load_share_links

def choose_html_layout_features(project_path):
    prefs = load_prefs(project_path)

    default_features = {
        "use_chapter_titles": True,
        "cover_image": True,
        "chapter_nav_top": True,
        "epub_link": False,
        "pdf_link": False,
        "share_links": True,
        "discuss_link": True,
        "chapter_nav_bottom": True,
        "social_links": True,
        "copyright": True,
        "license": True
    }

    # Inject or merge into prefs
    prefs.setdefault("display_features", default_features.copy())
    features = prefs["display_features"]

    # Menu sections
    sections = [
        ("HEADER", [
            ("use_chapter_titles", "Use Chapter Titles"),
            ("cover_image", "Cover Image"),
            ("chapter_nav_top", "Top Chapter Navigation"),
            ("epub_link", "EPUB Download Link"),
            ("pdf_link", "PDF Download Link")
        ]),
        ("FOOTER", [
            ("share_links", "Share This Chapter Links"),
            ("discuss_link", "Discuss This Chapter Link"),
            ("chapter_nav_bottom", "Bottom Chapter Navigation"),
            ("social_links", "Social Media Links"),
            ("copyright", "Copyright"),
            ("license", "License Info")
        ])
    ]

    print("\nHTML Layout\n")
    print("Choose which items to display on your static web pages. Press Enter when done.\n")

    while True:
        option_map = {}
        idx = 1
        for section_title, items in sections:
            print(section_title)
            for key, label in items:
                state = "Yes" if features.get(key, False) else "No"
                print(f"{idx}. {label} ({state})")
                option_map[str(idx)] = key
                idx += 1
            print()

        choice = input("Toggle item number (or press Enter to finish): ").strip()
        if not choice:
            break
        elif choice in option_map:
            key = option_map[choice]
            features[key] = not features[key]
        else:
            print("Invalid choice. Try again.\n")

    prefs["display_features"] = features
    save_prefs(project_path, prefs)
    return features

def html_header(prefs, chapter=None, epub_exists=False, pdf_exists=False, chapter_list=None):
    features = prefs.get("display_features", {})
    cover_path = prefs.get("cover_image", "")
    story_title = prefs.get("story_title", "")
    author = prefs.get("story_author", "")
    use_titles = features.get("use_chapter_titles", True)

    html = ['<header class="chapter-header">']

    # Cover Image (if enabled)
    if features.get("cover_image", True) and cover_path:
        html.append(f'<img src="../{os.path.basename(cover_path)}" alt="Cover" class="cover" />')

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
        html.append(html_chapter_nav(chapter, chapter_list, prefs))

    # EPUB/PDF download links
    download_links = []
    if chapter and features.get("epub_link") and epub_exists:
        slug = story_title.lower().replace(" ", "_")
        download_links.append(f'<a href="../download/{slug}_chapter_{chapter["number"]}.epub">EPUB</a>')
    if chapter and features.get("pdf_link") and pdf_exists:
        slug = story_title.lower().replace(" ", "_")
        download_links.append(f'<a href="../download/{slug}_chapter_{chapter["number"]}.pdf">PDF</a>')

    if download_links:
        html.append('<div class="download-links">' + " | ".join(download_links) + '</div>')

    html.append('</header>')
    return "\n".join(html)

def html_chapter_nav(current_chapter, chapter_list, prefs):
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
    nav_links.append('<a href="../index.html">Table of Contents</a>')

    # Next
    if index is not None and index < len(chapter_list) - 1:
        nxt = chapter_list[index + 1]
        next_title = f"Chapter {nxt['number']}: {nxt['title']}" if use_titles else f"Chapter {nxt['number']}"
        nav_links.append(f'<a href="{nxt["number"]}.html">Next ({next_title}) &rarr;</a>')
    else:
        nav_links.append('<span class="disabled">Next &rarr;</span>')

    return f'<nav class="chapter-nav">\n  {" | ".join(nav_links)}\n</nav>'

def html_footer(prefs, chapter=None, chapter_list=None, project_path=None):
    follow_links = load_follow_links(project_path)
    share_links = load_share_links(project_path)
    features = prefs.get("display_features", {})
    html = ['<footer class="footer">']

    # Bottom Chapter Navigation
    if chapter and features.get("chapter_nav_bottom", True) and chapter_list:
        html.append(html_chapter_nav(chapter, chapter_list, prefs))

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
            if platform == "github":
                url = f"https://github.com/{handle}"
            elif platform == "x":
                url = f"https://x.com/{handle}"
            elif platform == "bluesky":
                url = f"https://bsky.app/profile/{handle}.bsky.social"
            elif platform == "mastodon":
                url = handle  # Full URL expected
            else:
                url = "#"
            html.append(f'<a href="{url}" target="_blank">{platform.title()}</a>')
        html.append('</div>')

    # Copyright
    if features.get("copyright", True):
        html.append(f'<p>&copy; {prefs.get("copyright", "")} {prefs.get("story_author", "")}</p>')

    # License Info
    if features.get("license", True):
        license_code = prefs.get("license", "")
        license_map = {
            "CC-BY-NC-SA-4.0": "https://creativecommons.org/licenses/by-nc-sa/4.0/"
            # Add more codes here as needed
        }
        license_url = license_map.get(license_code, "#")
        html.append(f'<p>Licensed under <a href="{license_url}" target="_blank">{license_code}</a></p>')

    html.append('Powered by <a href="https://www.github.com/ironmangary/publine" target="_blank">Publine</a><br>')
    html.append('</footer>')
    return "\n".join(html)

def build_html(project_path, prefs, chapters):
    print("\n🛠️ Generating HTML...")
    for ch in chapters:
        create_html_chapter_page(ch, chapters, prefs, project_path)
    create_html_index_page(chapters, prefs, project_path)
    public_dir = os.path.join(project_path, "public")
    os.makedirs(public_dir, exist_ok=True)

# Check for styles.css
    style_src = os.path.join(project_path, "includes", "styles.css")
    if not os.path.isfile(style_src):
        print("⚠️  styles.css not found in /includes/")
        choice = input("Create default stylesheet now? [Y/n] ").strip().lower()
        if choice in ("", "y", "yes"):
            with open(style_src, "w", encoding="utf-8") as f:
                f.write(DEFAULT_CSS)  # Make sure DEFAULT_CSS is in scope
            print("✅ Default stylesheet created.")
        else:
            print("🚫 Skipping stylesheet generation.")

# Copy styles.css
    style_dst = os.path.join(public_dir, "styles.css")
    if os.path.isfile(style_src) and not os.path.exists(style_dst):
        shutil.copyfile(style_src, style_dst)

# Copy cover image
    cover_src = os.path.join(project_path, "includes", prefs.get("cover_image", ""))
    cover_dst = os.path.join(public_dir, os.path.basename(cover_src))
    if os.path.isfile(cover_src) and not os.path.exists(cover_dst):
        shutil.copyfile(cover_src, cover_dst)

def create_html_chapter_page(chapter, chapters, prefs, project_path):
    num = chapter["number"]
    slug = prefs["story_title"].lower().replace(" ", "_")
    includes_path = os.path.join(project_path, "includes", f"chapter_{num}.html")
    output_path = os.path.join(project_path, "public", "chapter", f"{num}.html")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(includes_path, "r", encoding="utf-8") as f:
        body = f.read()

    # Heading
    chapter_heading = format_chapter_heading(chapter, prefs["display_features"].get("use_chapter_titles", True))
    epub_name = f"{slug}_chapter_{num}.epub"
    epub_path = os.path.join(project_path, "download", epub_name)
    epub_exists = os.path.exists(epub_path)
    pdf_name = f"{slug}_chapter_{num}.pdf"
    pdf_path = os.path.join(project_path, "download", pdf_name)
    pdf_exists = os.path.exists(pdf_path)
    header_block = html_header(prefs, chapter, epub_exists=os.path.exists(epub_path), pdf_exists=os.path.exists(pdf_path), chapter_list=chapters)

    # FOOTER
    footer_block = html_footer(prefs, chapter=chapter, chapter_list=chapters, project_path=project_path)

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
        f'<li><a href="chapter/{ch["number"]}.html">{format_chapter_heading(ch, prefs["use_chapter_titles"])}</a></li>'
        for ch in chapters
    ])

    header_block = html_header(prefs)
    footer_block = html_footer(prefs, project_path=project_path)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{prefs["story_title"]} - Table of Contents</title>
    <link rel="stylesheet" href="includes/styles.css">
</head>
<body>
{header_block}
<br>
<main><center><h3>Table of Contents</h3></center>
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
