#!/usr/bin/env python3
"""Validate catalog consistency and generated site files."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOKS = json.loads((ROOT / "data" / "books.json").read_text(encoding="utf-8"))["books"]
SOURCES = json.loads((ROOT / "sources" / "catalog.json").read_text(encoding="utf-8"))["files"]
PROTECTED_EXTENSIONS = {".pdf", ".epub", ".mobi", ".azw3"}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    slugs = [book["slug"] for book in BOOKS]
    if len(slugs) != len(set(slugs)):
        fail("data/books.json contains duplicate slugs")
    if len(BOOKS) < 20:
        fail(f"expected at least the 20 initial books, got {len(BOOKS)}")

    source_slugs = {source["slug"] for source in SOURCES}
    for book in BOOKS:
        slug = book["slug"]
        if slug not in source_slugs:
            fail(f"missing source catalog entry: {slug}")
        for path in [ROOT / "notes" / f"{slug}.md", ROOT / "docs" / "books" / f"{slug}.html"]:
            if not path.is_file() or path.stat().st_size == 0:
                fail(f"missing or empty file: {path.relative_to(ROOT)}")

    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, check=True, text=True, capture_output=True
    ).stdout.splitlines()
    approved_paths = {
        source["repo_path"]
        for source in SOURCES
        if source.get("redistributable") and source.get("repo_path")
    }
    illegal = [
        path
        for path in tracked
        if Path(path).suffix.lower() in PROTECTED_EXTENSIONS and path not in approved_paths
    ]
    if illegal:
        fail("protected book files are tracked: " + ", ".join(illegal))

    for source in SOURCES:
        repo_path = source.get("repo_path")
        if not repo_path:
            continue
        if not source.get("redistributable"):
            fail(f"tracked source is not marked redistributable: {repo_path}")
        path = ROOT / repo_path
        if not path.is_file():
            fail(f"missing redistributable source: {repo_path}")
        if path.stat().st_size != source.get("bytes"):
            fail(f"source size mismatch: {repo_path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != source.get("sha256"):
            fail(f"source checksum mismatch: {repo_path}")

    index = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    if index.count('data-book-card') != len(BOOKS):
        fail("generated index card count does not match catalog")
    if not (ROOT / "docs" / "sources.html").is_file():
        fail("generated source and copyright page is missing")
    print(f"OK: {len(BOOKS)} books, {len(SOURCES)} source files, site is consistent")


if __name__ == "__main__":
    main()
