import os

def import_content(path, fmt):
    ext = os.path.splitext(path)[1].lower()

    if fmt == "html":
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    elif fmt == "txt":
        with open(path, "r", encoding="utf-8") as f:
            paragraphs = f.read().split("\n\n")
            return "\n".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())

    elif fmt == "docx":
        return import_docx(path)

    else:
        raise Exception(f"Unsupported import format: {fmt}")


def import_docx(path):
    try:
        from docx import Document
    except ImportError:
        raise Exception("python-docx not installed. Run 'pip install python-docx'.")

    doc = Document(path)
    html = ""

    for para in doc.paragraphs:
        if not para.text.strip():
            continue

        style = para.style.name
        text_parts = []

        for run in para.runs:
            text = run.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if run.bold:
                text = f"<strong>{text}</strong>"
            if run.italic:
                text = f"<em>{text}</em>"
            text_parts.append(text)

        content = "".join(text_parts)

        if style.startswith("Heading"):
            try:
                level = int(style.split()[-1])
                if 1 <= level <= 6:
                    html += f"<h{level}>{content}</h{level}>\n"
                    continue
            except:
                pass  # fallback to paragraph if Heading isn't parsable

        html += f"<p>{content}</p>\n"

    return html
