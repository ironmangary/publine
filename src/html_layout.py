import os
import shutil

def build_html(project_path, prefs, chapters):
    print("\n🛠️ Generating HTML...")
    for ch in chapters:
        create_chapter_page(ch, chapters, prefs, project_path)
    create_index_page(chapters, prefs, project_path)
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
