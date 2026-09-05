#!/usr/bin/env python3
"""Build the reading notes as a static site in docs/."""

from __future__ import annotations

import html
import json
from pathlib import Path

import markdown


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "books.json"
NOTES_DIR = ROOT / "notes"
DISCUSSIONS_DIR = ROOT / "discussions"
DOCS_DIR = ROOT / "docs"


def markdown_to_html(text: str) -> str:
    return markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
        output_format="html5",
    )


def shell(*, title: str, description: str, asset_prefix: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(description, quote=True)}">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{asset_prefix}assets/style.css">
</head>
<body>
{body}
<script src="{asset_prefix}assets/site.js"></script>
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
<main class="home">
  <section class="hero">
    <p class="eyebrow">A PERSONAL READING SYSTEM</p>
    <h1>{html.escape(site['title'])}</h1>
    <p class="hero-copy">{html.escape(site['subtitle'])}。{html.escape(site['description'])}</p>
    <div class="stats" aria-label="书库统计">
      <div class="stat"><strong>{len(books)}</strong><span>首批书目</span></div>
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
    return f"""<div id="progress" aria-hidden="true"></div>
{header(home_href)}
<button class="icon-button menu-button" type="button" data-menu-toggle aria-label="打开目录" aria-expanded="false">目录</button>
<div class="reader-shell">
  <aside class="reader-sidebar" aria-label="文档目录">
    <p class="sidebar-label">{html.escape(sidebar_label)}</p>
    <p class="toc-title">阅读目录</p>
    <nav id="toc"></nav>
  </aside>
  <main class="reader-main">
    <article class="paper">{content}</article>
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
        note = source.get("integrity_note", "")
        rows.append(
            "<tr>"
            f"<td>{html.escape(titles.get(source['slug'], source['slug']))}</td>"
            f"<td>{html.escape(source.get('local_filename') or '待补充')}</td>"
            f"<td>{html.escape(source.get('format', '—').upper())}<br>{size_label}<br>{pages} 页</td>"
            f"<td><code>{html.escape(digest)}</code></td>"
            f"<td>{reference_link}{('<br><small>' + html.escape(note) + '</small>') if note else ''}</td>"
            "</tr>"
        )
    content = f"""<h1>来源与版权清单</h1>
<p class="book-summary">{html.escape(source_catalog['policy'])}</p>
<h2>为什么不把全部电子书放进公开仓库</h2>
<p>公开读书笔记与再次分发整本受版权保护的电子书是两件事。本站公开自己的分析、讨论和合法来源；私人阅读副本仅保留在本地 <code>library/</code>，并用 SHA-256 确认版本。</p>
<h2>首批来源记录</h2>
<table>
  <thead><tr><th>书</th><th>本地文件名</th><th>格式/大小</th><th>SHA-256</th><th>公开参考</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
<h2>完整性说明</h2>
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
