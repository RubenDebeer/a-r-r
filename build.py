#!/usr/bin/env python3
"""Build static HTML study-notes site from markdown sources.

No static-site framework — pure HTML/CSS output.
Run: python build.py
Output: _site/
"""

import html as _html
import re
import shutil
import sys
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).parent
BOOKS_DIR = ROOT / "books"
SITE_DIR = ROOT / "_site"

# ── CSS ────────────────────────────────────────────────────────────────────────
CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

:root{
  --sidebar-w:260px;
  --sidebar-bg:#0f172a;
  --sidebar-text:#94a3b8;
  --sidebar-text-hover:#e2e8f0;
  --sidebar-active:#3b82f6;
  --sidebar-active-bg:rgba(59,130,246,.12);
  --accent:#3b82f6;
  --accent-hover:#2563eb;
  --bg:#ffffff;
  --bg-alt:#f8fafc;
  --text:#1e293b;
  --text-muted:#64748b;
  --border:#e2e8f0;
  --code-bg:#f1f5f9;
  --note-bg:#eff6ff;
  --note-border:#3b82f6;
  --warning-bg:#fffbeb;
  --warning-border:#f59e0b;
}

html{font-size:16px;-webkit-text-size-adjust:100%}

body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
  color:var(--text);
  background:var(--bg);
  line-height:1.75;
}

/* ── layout ── */
.layout{display:flex;min-height:100vh}

.sidebar{
  width:var(--sidebar-w);
  min-width:var(--sidebar-w);
  background:var(--sidebar-bg);
  position:fixed;
  top:0;left:0;bottom:0;
  overflow-y:auto;
  display:flex;
  flex-direction:column;
  z-index:100;
}

.content{
  margin-left:var(--sidebar-w);
  flex:1;
  min-width:0;
  padding:56px 80px 96px;
}

.prose{max-width:740px}

/* ── sidebar ── */
.sidebar-header{
  padding:28px 20px 20px;
  border-bottom:1px solid rgba(255,255,255,.07);
}

.site-link{
  display:block;
  font-size:11px;
  font-weight:700;
  letter-spacing:.1em;
  text-transform:uppercase;
  color:var(--accent);
  text-decoration:none;
  margin-bottom:10px;
}
.site-link:hover{color:#60a5fa}

.book-title{
  font-size:14px;
  font-weight:600;
  color:#f1f5f9;
  line-height:1.4;
}

.sidebar-nav{padding:12px 10px;flex:1}

.nav-label{
  display:block;
  padding:4px 10px;
  font-size:11px;
  font-weight:700;
  letter-spacing:.08em;
  text-transform:uppercase;
  color:#475569;
  margin-top:8px;
  margin-bottom:4px;
}

.nav-item{
  display:block;
  padding:8px 10px;
  border-radius:6px;
  font-size:14px;
  color:var(--sidebar-text);
  text-decoration:none;
  margin-bottom:1px;
  transition:background .12s,color .12s;
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
}
.nav-item:hover{background:rgba(255,255,255,.06);color:var(--sidebar-text-hover)}
.nav-item.active{background:var(--sidebar-active-bg);color:var(--accent);font-weight:500}

/* ── headings ── */
.prose h1{
  font-size:2rem;
  font-weight:800;
  line-height:1.2;
  letter-spacing:-.02em;
  margin-bottom:24px;
  padding-bottom:20px;
  border-bottom:2px solid var(--border);
}
.prose h2{
  font-size:1.375rem;
  font-weight:700;
  letter-spacing:-.01em;
  margin-top:52px;
  margin-bottom:14px;
  padding-bottom:6px;
  border-bottom:1px solid var(--border);
}
.prose h3{
  font-size:1.125rem;
  font-weight:600;
  margin-top:32px;
  margin-bottom:10px;
}
.prose h4,.prose h5,.prose h6{
  font-size:1rem;
  font-weight:600;
  margin-top:24px;
  margin-bottom:8px;
}

/* ── text ── */
.prose p{margin-bottom:18px}
.prose a{color:var(--accent);text-decoration:none}
.prose a:hover{text-decoration:underline}
.prose strong{font-weight:600}
.prose em{font-style:italic}

.prose hr{
  border:none;
  border-top:1px solid var(--border);
  margin:44px 0;
}

/* ── lists ── */
.prose ul,.prose ol{margin:0 0 18px 26px}
.prose li{margin-bottom:6px}
.prose li>ul,.prose li>ol{margin-top:6px;margin-bottom:0}

/* ── code ── */
.prose code{
  font-family:'SF Mono','Fira Code','Consolas',monospace;
  font-size:.875em;
  background:var(--code-bg);
  color:#0f172a;
  padding:.15em .4em;
  border-radius:4px;
  border:1px solid var(--border);
}
.prose pre{
  background:#1e293b;
  border-radius:10px;
  padding:20px 24px;
  overflow-x:auto;
  margin-bottom:24px;
  line-height:1.6;
}
.prose pre code{
  background:none;
  border:none;
  padding:0;
  font-size:.875rem;
  color:#e2e8f0;
}

/* ── tables ── */
.prose table{
  width:100%;
  border-collapse:collapse;
  margin-bottom:28px;
  font-size:.9375rem;
  border:1px solid var(--border);
  border-radius:8px;
  overflow:hidden;
}
.prose th{
  background:var(--bg-alt);
  font-weight:600;
  text-align:left;
  padding:11px 16px;
  border-bottom:2px solid var(--border);
}
.prose th+th,.prose td+td{border-left:1px solid var(--border)}
.prose td{
  padding:10px 16px;
  border-bottom:1px solid var(--border);
  vertical-align:top;
}
.prose tr:last-child td{border-bottom:none}
.prose tr:nth-child(even) td{background:var(--bg-alt)}

/* ── admonitions ── */
.prose .admonition{
  border-radius:8px;
  padding:16px 20px;
  margin:24px 0;
  border-left:4px solid;
}
.prose .admonition.note{background:var(--note-bg);border-color:var(--note-border)}
.prose .admonition.warning,.prose .admonition.caution{background:var(--warning-bg);border-color:var(--warning-border)}
.prose .admonition-title{
  font-size:.8rem;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:.07em;
  margin-bottom:8px;
}
.prose .admonition.note .admonition-title{color:var(--note-border)}
.prose .admonition.warning .admonition-title,.prose .admonition.caution .admonition-title{color:#d97706}
.prose .admonition p:last-child{margin-bottom:0}

/* ── mermaid ── */
.prose .mermaid{
  display:flex;
  justify-content:center;
  margin:32px 0;
  overflow-x:auto;
}

/* ── landing ── */
body.landing-body{background:var(--bg-alt)}

.landing{
  max-width:960px;
  margin:0 auto;
  padding:80px 48px 120px;
}

.landing-header{margin-bottom:64px}

.landing-header h1{
  font-size:2.75rem;
  font-weight:800;
  letter-spacing:-.03em;
  color:var(--text);
  margin-bottom:14px;
}

.landing-header p{
  font-size:1.125rem;
  color:var(--text-muted);
  max-width:520px;
}

.section-label{
  font-size:12px;
  font-weight:700;
  letter-spacing:.1em;
  text-transform:uppercase;
  color:var(--text-muted);
  margin-bottom:20px;
}

.book-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
  gap:20px;
}

.book-card{
  display:block;
  text-decoration:none;
  background:var(--bg);
  border:1px solid var(--border);
  border-radius:12px;
  padding:28px;
  transition:box-shadow .2s,border-color .2s,transform .15s;
}
.book-card:hover{
  box-shadow:0 8px 30px rgba(0,0,0,.08);
  border-color:var(--accent);
  transform:translateY(-2px);
}
.book-card-tag{
  font-size:11px;
  font-weight:700;
  letter-spacing:.08em;
  text-transform:uppercase;
  color:var(--accent);
  margin-bottom:10px;
}
.book-card h2{
  font-size:1.125rem;
  font-weight:700;
  color:var(--text);
  line-height:1.35;
  margin-bottom:8px;
}
.book-card p{
  font-size:.9375rem;
  color:var(--text-muted);
  line-height:1.5;
}

/* ── responsive ── */
@media(max-width:768px){
  .sidebar{display:none}
  .content{margin-left:0;padding:28px 20px 64px}
  .landing{padding:40px 20px 80px}
  .landing-header h1{font-size:2rem}
}
"""

# ── HTML templates ─────────────────────────────────────────────────────────────

SCRIPTS = """
  <script>
    MathJax = {
      tex: {
        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
        displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
      },
      options: { skipHtmlTags: ['script','noscript','style','textarea','pre'] }
    };
  </script>
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
  <script>mermaid.initialize({startOnLoad:true,theme:'neutral',fontFamily:'inherit'});</script>
"""


def book_page(*, title, book_title, body, nav_items, current_file, prefix):
    """Render a full book-chapter HTML page."""
    nav_html = ""
    for label, filename in nav_items:
        href = filename.replace(".md", ".html")
        active = " active" if filename == current_file else ""
        nav_html += (
            f'<a href="{href}" class="nav-item{active}" title="{_html.escape(label)}">'
            f"{_html.escape(label)}</a>\n"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{_html.escape(title)} — {_html.escape(book_title)}</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <a href="{prefix}index.html" class="site-link">Study Notes</a>
        <div class="book-title">{_html.escape(book_title)}</div>
      </div>
      <nav class="sidebar-nav">
        {nav_html}
      </nav>
    </aside>
    <main class="content">
      <article class="prose">
        {body}
      </article>
    </main>
  </div>
{SCRIPTS}
</body>
</html>"""


def landing_page(books):
    """Render the root index.html listing all books."""
    cards = ""
    for slug, book_title, description in books:
        cards += f"""
    <a href="{slug}/index.html" class="book-card">
      <div class="book-card-tag">Study Notes</div>
      <h2>{_html.escape(book_title)}</h2>
      <p>{_html.escape(description)}</p>
    </a>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Study Notes</title>
  <style>{CSS}</style>
</head>
<body class="landing-body">
  <div class="landing">
    <header class="landing-header">
      <h1>Study Notes</h1>
      <p>Chapter-by-chapter summaries of technical textbooks.</p>
    </header>
    <div class="section-label">Books</div>
    <div class="book-grid">
      {cards}
    </div>
  </div>
</body>
</html>"""


# ── markdown conversion ────────────────────────────────────────────────────────

_MD_EXTENSIONS = [
    "markdown.extensions.tables",
    "markdown.extensions.fenced_code",
    "markdown.extensions.admonition",
    "markdown.extensions.toc",
]


def md_to_html(text: str) -> str:
    """Convert markdown text to HTML."""
    # Strip YAML frontmatter
    text = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL)

    md = markdown.Markdown(extensions=_MD_EXTENSIONS)
    body = md.convert(text)

    # Convert mermaid fenced blocks → mermaid divs (before any JS runs)
    body = re.sub(
        r'<pre><code[^>]*class="[^"]*(?:language-)?mermaid[^"]*"[^>]*>(.*?)</code></pre>',
        lambda m: f'<div class="mermaid">{_html.unescape(m.group(1))}</div>',
        body,
        flags=re.DOTALL,
    )
    return body


# ── build book ─────────────────────────────────────────────────────────────────

def build_book(book_dir: Path) -> tuple[str, str, str] | None:
    """Build all pages for one book. Returns (slug, title, description)."""
    config_file = book_dir / "mkdocs.yml"
    if not config_file.exists():
        return None

    config = yaml.safe_load(config_file.read_text())
    slug = book_dir.name
    book_title = config.get("site_name", slug)
    nav_raw = config.get("nav", [])

    # Parse nav: list of {label: filename} dicts
    nav_items: list[tuple[str, str]] = []
    for entry in nav_raw:
        for label, filename in entry.items():
            nav_items.append((label, filename))

    docs_dir = book_dir / "docs"
    out_dir = SITE_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    description = ""

    for label, md_filename in nav_items:
        md_file = docs_dir / md_filename
        if not md_file.exists():
            print(f"  [skip] {md_file} not found", file=sys.stderr)
            continue

        text = md_file.read_text(encoding="utf-8")

        # Grab first real paragraph as book description (from index.md)
        if md_filename == "index.md" and not description:
            clean = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL)
            for line in clean.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    description = line[:160]
                    break

        body = md_to_html(text)
        html_filename = md_filename.replace(".md", ".html")

        page = book_page(
            title=label,
            book_title=book_title,
            body=body,
            nav_items=nav_items,
            current_file=md_filename,
            prefix="../",
        )
        (out_dir / html_filename).write_text(page, encoding="utf-8")
        print(f"  {slug}/{html_filename}")

    # Copy figures if present
    figures_src = docs_dir / "figures"
    if figures_src.exists():
        shutil.copytree(figures_src, out_dir / "figures", dirs_exist_ok=True)

    return slug, book_title, description or book_title


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    SITE_DIR.mkdir(exist_ok=True)

    books = []
    for book_dir in sorted(BOOKS_DIR.iterdir()):
        if not book_dir.is_dir():
            continue
        result = build_book(book_dir)
        if result:
            books.append(result)

    index_html = landing_page(books)
    (SITE_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"index.html")

    print(f"\nBuilt {len(books)} book(s) → {SITE_DIR}")


if __name__ == "__main__":
    main()
