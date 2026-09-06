#!/usr/bin/env python3
"""Build the reading notes as a static site in docs/."""

from __future__ import annotations

import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

import markdown


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "books.json"
NOTES_DIR = ROOT / "notes"
DISCUSSIONS_DIR = ROOT / "discussions"
DOCS_DIR = ROOT / "docs"


class Outline(HTMLParser):
    """Extract the same headings for book, discussion, and source navigation."""

    def __init__(self) -> None:
        super().__init__()
        self.headings = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag in {"h2", "h3"}:
            self.current = [tag, dict(attrs).get("id"), []]

    def handle_data(self, data):
        if self.current is not None:
            self.current[2].append(data)

    def handle_endtag(self, tag):
        if self.current is not None and tag == self.current[0]:
            level, anchor, parts = self.current
            if anchor:
                self.headings.append((level, anchor, "".join(parts)))
            self.current = None

    def render(self) -> str:
        sections = []
        for level, anchor, label in self.headings:
            link = (f'<a href="#{html.escape(anchor, quote=True)}" '
                    f'class="level-{level[-1]}">{html.escape(label)}</a>')
            if level == "h3" and sections:
                sections[-1][1].append(f"<li>{link}</li>")
            else:
                sections.append([link, []])
        return "<ol>" + "".join(
            f"<li>{link}" + ("<ol>" + "".join(children) + "</ol>" if children else "") + "</li>"
            for link, children in sections
        ) + "</ol>"


def markdown_to_html(text: str) -> str:
    return markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
        output_format="html5",
    )


def shell(*, title: str, description: str, asset_prefix: str, body: str) -> str:
    asset_versions = {
        name: hashlib.sha256((DOCS_DIR / "assets" / name).read_bytes()).hexdigest()[:12]
        for name in ("style.css", "site.js")
    }
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(description, quote=True)}">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{asset_prefix}assets/style.css?v={asset_versions['style.css']}">
</head>
<body>
{body}
<script src="{asset_prefix}assets/site.js?v={asset_versions['site.js']}"></script>
</body>
</html>
"""


def header(home_href: str) -> str:
    sources_href = home_href.replace("index.html", "sources.html")
    return f"""<header class="site-header">
  <a class="brand" href="{home_href}">我的读书笔记</a>
  <div class="header-actions">
    <a class="quiet-link" href="{sources_href}">来源与版权</a>
    <a class="quiet-link" href="{home_href}#method">关于这套笔记</a>
    <a class="quiet-link" href="https://github.com/100apps/my-reading-notes">GitHub</a>
    <button class="icon-button" type="button" data-theme-toggle>深浅色</button>
  </div>
</header>"""


def footer() -> str:
    return """<footer class="site-footer">
  <p>个人学习记录 · 明确区分作者主张、证据、外部观点与个人判断。笔记不替代原书。</p>
</footer>"""


def render_index(config: dict) -> None:
    site = config["site"]
    books = config["books"]
    categories = list(dict.fromkeys(book["category"] for book in books))
    deep_count = sum(book["note_status"] == "深度报告" for book in books)
    filters = "".join(
        f'<button class="filter{(" active" if category == "全部" else "")}" '
        f'type="button" data-filter="{html.escape(category, quote=True)}">{html.escape(category)}</button>'
        for category in ["全部", *categories]
    )

    cards = []
    for number, book in enumerate(books, 1):
        searchable = " ".join(
            [book["title"], book["original_title"], book["author"], book["category"]]
        ).lower()
        cards.append(
            f"""<article class="book-card" data-book-card data-number="{number:02d}"
  data-category="{html.escape(book['category'], quote=True)}"
  data-search="{html.escape(searchable, quote=True)}">
  <div class="card-meta">
    <span>{html.escape(book['category'])}</span>
    <span class="status">{html.escape(book['note_status'])}</span>
  </div>
  <h2>{html.escape(book['title'])}</h2>
  <p class="author">{html.escape(book['author'])}</p>
  <p class="summary">{html.escape(book['summary'])}</p>
  <a class="card-link" href="books/{book['slug']}.html" aria-label="阅读《{html.escape(book['title'], quote=True)}》笔记">阅读笔记 →</a>
</article>"""
        )

    body = f"""{header('index.html')}
<main class="home" id="main-content">
  <section class="hero">
    <p class="eyebrow">A PERSONAL READING SYSTEM</p>
    <h1>{html.escape(site['title'])}</h1>
    <p class="hero-copy">{html.escape(site['subtitle'])}。{html.escape(site['description'])}</p>
    <div class="stats" aria-label="书库统计">
      <div class="stat"><strong>{len(books)}</strong><span>收录书目</span></div>
      <div class="stat"><strong>{deep_count}</strong><span>深度报告</span></div>
      <div class="stat"><strong>{len(categories)}</strong><span>阅读方向</span></div>
    </div>
  </section>
  <section aria-label="书目列表">
    <div class="controls">
      <input class="search" type="search" placeholder="搜索书名、作者或主题…" aria-label="搜索书目" data-search>
      {filters}
    </div>
    <div class="books-grid">
      {''.join(cards)}
      <p class="empty" data-empty hidden>没有找到匹配的书。</p>
    </div>
  </section>
  <section class="method" id="method">
    <h2>这不是摘要仓库，<br>而是判断的版本历史。</h2>
    <div>
      <p>每篇笔记分别记录作者的论点、书内论据、论证链、外部证据、反方观点、适用边界和可执行行动。结构化初读只代表完成了书目与核心论证整理，不冒充逐章精读。</p>
      <p>以后每次共读都会更新阅读状态，并把真实讨论追加到对应记录。受版权保护的电子书只保留本地副本和校验信息，不在公开站点重新分发。</p>
    </div>
  </section>
</main>
{footer()}"""
    output = shell(
        title=site["title"],
        description=site["description"],
        asset_prefix="",
        body=body,
    )
    (DOCS_DIR / "index.html").write_text(output, encoding="utf-8")


def reader_layout(*, content: str, sidebar_label: str, home_href: str) -> str:
    outline = Outline()
    outline.feed(content)
    section_count = sum(level == "h2" for level, _, _ in outline.headings)
    content = content.replace("<table>", '<div class="table-scroll" role="region" '
                              'aria-label="表格，可横向滚动" tabindex="0"><table>')
    content = content.replace("</table>", "</table></div>")
    content = re.sub(r'<(h[23]) id="([^"]+)">', r'<\1 id="\2" tabindex="-1">', content)
    content = content.replace("</h2>", '</h2><a class="section-toc" href="#reader-toc">目录 ↑</a>')
    return f"""<a class="skip-link" href="#main-content">跳到正文</a>
<div id="progress" aria-hidden="true"></div>
{header(home_href)}
<div class="reader-shell">
  <aside class="reader-sidebar" aria-label="文档目录">
    <details class="reader-toc" id="reader-toc">
      <summary><span>阅读目录</span><span class="toc-count">{section_count} 节</span></summary>
      <div class="toc-content">
        <p class="sidebar-label">{html.escape(sidebar_label)}</p>
        <nav id="toc" aria-label="章节导航">{outline.render()}</nav>
      </div>
    </details>
  </aside>
  <main class="reader-main" id="main-content" tabindex="-1">
    <div class="reader-toolbar" aria-label="阅读工具">
      <a class="quiet-link" href="{home_href}">← 返回书架</a>
      <div class="reading-settings" data-reading-settings hidden>
        <button class="icon-button" type="button" data-font-decrease aria-label="减小正文字号">A−</button>
        <output class="font-size-label" data-font-label aria-live="polite">18</output>
        <button class="icon-button" type="button" data-font-increase aria-label="增大正文字号">A＋</button>
      </div>
    </div>
    <article class="paper">{content}
      <div class="reader-end"><a href="#reader-toc">↑ 返回目录</a><a href="{home_href}">返回书架 →</a></div>
    </article>
  </main>
</div>
{footer()}"""


def render_book(book: dict) -> None:
    note_path = NOTES_DIR / f"{book['slug']}.md"
    rendered = markdown_to_html(note_path.read_text(encoding="utf-8"))
    info = f"""<div class="book-tags">
  <span class="book-tag">{html.escape(book['category'])}</span>
  <span class="book-tag">{html.escape(book['note_status'])}</span>
  <span class="book-tag">阅读状态：{html.escape(book['reading_status'])}</span>
</div>
<p class="book-summary">{html.escape(book['summary'])}</p>"""
    rendered = rendered.replace("</h1>", f"</h1>{info}", 1)

    discussion_path = DISCUSSIONS_DIR / f"{book['slug']}.md"
    if discussion_path.exists():
        rendered += (
            f'<a class="discussion-link" href="../discussions/{book["slug"]}.html">'
            "查看这本书的讨论记录 →</a>"
        )

    body = reader_layout(
        content=rendered,
        sidebar_label=book["original_title"],
        home_href="../index.html",
    )
    output = shell(
        title=f"《{book['title']}》｜我的读书笔记",
        description=book["summary"],
        asset_prefix="../",
        body=body,
    )
    (DOCS_DIR / "books" / f"{book['slug']}.html").write_text(output, encoding="utf-8")


def render_discussion(book: dict) -> None:
    discussion_path = DISCUSSIONS_DIR / f"{book['slug']}.md"
    if not discussion_path.exists():
        return
    rendered = markdown_to_html(discussion_path.read_text(encoding="utf-8"))
    rendered += f'<a class="discussion-link" href="../books/{book["slug"]}.html">← 返回读书报告</a>'
    body = reader_layout(
        content=rendered,
        sidebar_label=f"讨论记录 · {book['title']}",
        home_href="../index.html",
    )
    output = shell(
        title=f"《{book['title']}》讨论记录｜我的读书笔记",
        description=f"关于《{book['title']}》的持续讨论与判断修订。",
        asset_prefix="../",
        body=body,
    )
    (DOCS_DIR / "discussions" / f"{book['slug']}.html").write_text(output, encoding="utf-8")


def render_sources(config: dict, source_catalog: dict) -> None:
    titles = {book["slug"]: book["title"] for book in config["books"]}
    rows = []
    for source in source_catalog["files"]:
        size = source.get("bytes")
        size_label = f"{size / 1024 / 1024:.1f} MB" if size else "待补充"
        pages = source.get("pages", "—")
        digest = source.get("sha256", "待补充")
        reference = source.get("public_reference")
        reference_link = (
            f'<a href="{html.escape(reference, quote=True)}">合法来源/书目信息</a>'
            if reference
            else "待补充"
        )
        repo_path = source.get("repo_path")
        repo_link = (
            '<br><a href="https://github.com/100apps/my-reading-notes/blob/main/'
            f'{html.escape(repo_path, quote=True)}">仓库原文</a>'
            if repo_path and source.get("redistributable")
            else ""
        )
        note = source.get("integrity_note", "")
        rows.append(
            "<tr>"
            f"<td>{html.escape(titles.get(source['slug'], source['slug']))}</td>"
            f"<td>{html.escape(source.get('local_filename') or '待补充')}</td>"
            f"<td>{html.escape(source.get('format', '—').upper())}<br>{size_label}<br>{pages} 页</td>"
            f"<td><code>{html.escape(digest)}</code></td>"
            f"<td>{reference_link}{repo_link}{('<br><small>' + html.escape(note) + '</small>') if note else ''}</td>"
            "</tr>"
        )
    content = f"""<h1>来源与版权清单</h1>
<p class="book-summary">{html.escape(source_catalog['policy'])}</p>
<h2 id="copyright">为什么不把全部电子书放进公开仓库</h2>
<p>公开读书笔记与再次分发整本受版权保护的电子书是两件事。本站公开自己的分析、讨论和合法来源；私人阅读副本仅保留在本地 <code>library/</code>，并用 SHA-256 确认版本。</p>
<p>经核验属于公版或具有明确再分发许可的原文，可以连同来源和权利状态保存在仓库；仍受保护的版本只登记元数据，不公开文件。</p>
<h2 id="source-records">来源记录</h2>
<table>
  <thead><tr><th>书</th><th>本地文件名</th><th>格式/大小</th><th>SHA-256</th><th>公开参考</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
<h2 id="integrity">完整性说明</h2>
<p>校验值只能证明“以后拿到的是不是同一个文件”，不能证明文件完整、准确或具有合法来源。标有完整性警告的文件，应在正式精读前从正规渠道重新获取并更新记录。</p>"""
    body = reader_layout(
        content=content,
        sidebar_label="SOURCE & COPYRIGHT",
        home_href="index.html",
    )
    output = shell(
        title="来源与版权｜我的读书笔记",
        description="读书笔记所依据的版本、文件校验值、合法来源与版权处理方式。",
        asset_prefix="",
        body=body,
    )
    (DOCS_DIR / "sources.html").write_text(output, encoding="utf-8")


def main() -> None:
    config = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    source_catalog = json.loads((ROOT / "sources" / "catalog.json").read_text(encoding="utf-8"))
    (DOCS_DIR / "books").mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "discussions").mkdir(parents=True, exist_ok=True)
    render_index(config)
    render_sources(config, source_catalog)
    for book in config["books"]:
        render_book(book)
        render_discussion(book)
    print(f"Built {len(config['books'])} book pages in {DOCS_DIR}")


if __name__ == "__main__":
    main()
