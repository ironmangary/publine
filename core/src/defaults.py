
# Define default.css file for projects
DEFAULT_CSS = """\
body {
    font-family: Georgia, serif;
    line-height: 1.6;
    max-width: 60ch;
    margin: 2em auto;
    padding: 0 1em;
    background: #fff;
    color: #222;
}
h1, h2, h3 { text-align: center; margin-top: 2em; }
img.cover {
    display: block;
    max-width: 100%;
    height: auto;
    margin: 2em auto;
}
nav, footer {
    text-align: center;
    margin: 2em 0;
    font-size: 0.9em;
}
a { color: #0077cc; text-decoration: none; }
a:hover { text-decoration: underline; }
@media print {
    nav, footer { display: none; }
}
"""
