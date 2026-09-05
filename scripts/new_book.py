#!/usr/bin/env python3
"""Create catalog, note, and discussion scaffolds for a new book."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "books.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--author", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--source-url", default="")
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.slug):
        parser.error("slug must contain lowercase letters, numbers, and hyphens only")

    config = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    if any(book["slug"] == args.slug for book in config["books"]):
        parser.error(f"book already exists: {args.slug}")

    config["books"].append(
        {
            "slug": args.slug,
            "title": args.title,
            "original_title": args.title,
            "author": args.author,
            "category": args.category,
            "note_status": "阅读准备",
            "reading_status": "待读",
            "date": date.today().isoformat(),
            "summary": "待补充一句话判断。",
        }
    )
    DATA_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    source_file = ROOT / "sources" / "catalog.json"
    sources = json.loads(source_file.read_text(encoding="utf-8"))
    sources["files"].append(
        {
            "slug": args.slug,
            "local_filename": "",
            "format": "",
            "bytes": None,
            "sha256": "",
            "redistributable": False,
            "integrity_note": "来源文件、版本、大小和校验值待补充。",
            "public_reference": args.source_url,
        }
    )
    source_file.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    note = f"""# 《{args.title}》：待补充副标题

> 笔记状态：阅读准备｜作者：{args.author}

## 版本与阅读范围

待补充。

## 一句话结论

待补充。

## 核心论点

### 论点

待补充。

### 书内论据

待补充。

### 论证链与强度

待补充。

## 外部观点与反方

待补充，并优先引用一手资料。

## 适用边界

待补充。

## 读后行动

1. 待补充。

## 最终评价

待补充。
"""
    discussion = f"""# 《{args.title}》讨论记录

> 状态：尚未开始讨论

## 讨论时间线

## 讨论后改变的判断

## 仍未解决的问题
"""
    (ROOT / "notes" / f"{args.slug}.md").write_text(note, encoding="utf-8")
    (ROOT / "discussions" / f"{args.slug}.md").write_text(discussion, encoding="utf-8")
    print(f"Created notes/{args.slug}.md and discussions/{args.slug}.md")


if __name__ == "__main__":
    main()
