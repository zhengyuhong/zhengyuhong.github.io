# Notes Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Markdown-authored personal notes site for `zhengyuhong.cn` that GitHub Actions generates and publishes through GitHub Pages.

**Architecture:** Markdown notes in `notes/` are the source of truth. A small Python generator parses YAML front matter, converts Markdown to HTML, renders pages through a simple HTML template, writes generated output to `site/`, and GitHub Actions publishes that directory.

**Tech Stack:** Python 3.12, `Markdown`, `PyYAML`, `unittest`, GitHub Actions, GitHub Pages.

## Global Constraints

- `notes/` is the primary writing surface.
- Each note filename uses `YYYY-MM-DD-title.md`.
- Each note has YAML front matter fields: `title`, `date`, `tags`, and `summary`.
- The canonical URL for `notes/2026-07-21-some-topic.md` is `/notes/2026-07-21-some-topic.html`.
- `site/` is generated output and should not be edited by hand.
- `CNAME` must stay at the repository root and be copied into `site/` during build.
- First version includes Markdown-to-HTML generation, homepage generation, note pages, homepage tag sections, local preview commands, and GitHub Actions publishing.
- First version defers full-text search, RSS, separate tag archive pages, related-note recommendations, comments, analytics, and complex theming.

---

## File Structure

- Create `requirements.txt`: Python runtime dependencies for the generator.
- Create `scripts/build.py`: static generator, including front matter parsing, Markdown conversion, page rendering, asset copying, and CLI entry point.
- Create `tests/test_build.py`: unit tests for parsing, sorting, rendering, and generated files.
- Create `templates/layout.html`: shared HTML shell for homepage and note pages.
- Create `assets/style.css`: global visual design for the knowledge garden.
- Create `notes/2026-07-21-welcome.md`: first sample note and publishing smoke test.
- Create `.github/workflows/pages.yml`: GitHub Pages deployment workflow.
- Create `.gitignore`: ignore generated `site/` and Python cache files.
- Modify `README.md`: document authoring, local preview, and publishing.
- Modify `AGENTS.md`: update contributor guidance now that the repository has build and test commands.
- Delete `index.html`: remove the old root-level `Hello World` page because GitHub Actions publishes `site/`.

---

### Task 1: Generator Core and Unit Tests

**Files:**
- Create: `requirements.txt`
- Create: `scripts/build.py`
- Create: `tests/test_build.py`

**Interfaces:**
- Produces: `Note` dataclass with fields `source_path: Path`, `slug: str`, `title: str`, `date: date`, `tags: tuple[str, ...]`, `summary: str`, `body_markdown: str`, `body_html: str`.
- Produces: `load_notes(notes_dir: Path) -> list[Note]`.
- Produces: `build_site(root: Path = ROOT) -> None`.
- Produces: CLI command `python3 scripts/build.py`.

- [ ] **Step 1: Add dependency file**

Create `requirements.txt`:

```text
Markdown>=3.6,<4
PyYAML>=6.0,<7
```

- [ ] **Step 2: Install dependencies**

Run:

```bash
python3 -m pip install -r requirements.txt
```

Expected: `Markdown` and `PyYAML` install successfully.

- [ ] **Step 3: Write failing tests**

Create `tests/test_build.py`:

```python
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.build import build_site, load_notes, tag_slug


class BuildSiteTests(unittest.TestCase):
    def write_note(self, root: Path, filename: str, content: str) -> None:
        notes_dir = root / "notes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        (notes_dir / filename).write_text(content, encoding="utf-8")

    def write_layout(self, root: Path) -> None:
        templates_dir = root / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        (templates_dir / "layout.html").write_text(
            "<!doctype html><html><head><title>{{ title }}</title>"
            '<meta name="description" content="{{ description }}">'
            '<link rel="stylesheet" href="{{ asset_prefix }}assets/style.css">'
            '</head><body class="{{ body_class }}">{{ content }}</body></html>',
            encoding="utf-8",
        )

    def test_load_notes_parses_metadata_and_sorts_newest_first(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_note(
                root,
                "2026-07-20-older.md",
                """---
title: Older Note
date: 2026-07-20
tags: [archive]
summary: Older summary.
---

# Older

Body
""",
            )
            self.write_note(
                root,
                "2026-07-21-newer.md",
                """---
title: Newer Note
date: 2026-07-21
tags: [codex, notes]
summary: Newer summary.
---

# Newer

This is **important**.
""",
            )

            notes = load_notes(root / "notes")

            self.assertEqual([note.title for note in notes], ["Newer Note", "Older Note"])
            self.assertEqual(notes[0].slug, "2026-07-21-newer")
            self.assertEqual(notes[0].tags, ("codex", "notes"))
            self.assertIn("<strong>important</strong>", notes[0].body_html)

    def test_tag_slug_supports_spaces_and_non_ascii_text(self) -> None:
        self.assertEqual(tag_slug("Codex Notes"), "codex-notes")
        self.assertEqual(tag_slug("长期思考"), "%E9%95%BF%E6%9C%9F%E6%80%9D%E8%80%83")

    def test_build_site_generates_pages_assets_and_cname(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_layout(root)
            self.write_note(
                root,
                "2026-07-21-newer.md",
                """---
title: Newer Note
date: 2026-07-21
tags: [codex, notes]
summary: Newer summary.
---

# Newer

Generated body.
""",
            )
            assets_dir = root / "assets"
            assets_dir.mkdir()
            (assets_dir / "style.css").write_text("body { color: #222; }\n", encoding="utf-8")
            (root / "CNAME").write_text("zhengyuhong.cn\n", encoding="utf-8")

            build_site(root)

            index_html = (root / "site" / "index.html").read_text(encoding="utf-8")
            note_html = (root / "site" / "notes" / "2026-07-21-newer.html").read_text(encoding="utf-8")

            self.assertIn("zhengyuhong.cn", index_html)
            self.assertIn("Newer summary.", index_html)
            self.assertIn('id="tag-codex"', index_html)
            self.assertIn("Generated body.", note_html)
            self.assertEqual((root / "site" / "CNAME").read_text(encoding="utf-8"), "zhengyuhong.cn\n")
            self.assertTrue((root / "site" / "assets" / "style.css").exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run tests to confirm failure**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: FAIL because `scripts.build` does not exist yet.

- [ ] **Step 5: Implement generator**

Create `scripts/build.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from html import escape
from pathlib import Path
import re
import shutil
from typing import Any
from urllib.parse import quote

import markdown
import yaml


ROOT = Path(__file__).resolve().parents[1]
SITE_NAME = "zhengyuhong.cn"
SITE_DESCRIPTION = "这里记录技术、思考和长期积累的笔记。"

FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.DOTALL)


@dataclass(frozen=True)
class Note:
    source_path: Path
    slug: str
    title: str
    date: date
    tags: tuple[str, ...]
    summary: str
    body_markdown: str
    body_html: str


def tag_slug(tag: str) -> str:
    normalized = re.sub(r"\s+", "-", tag.strip().lower())
    return quote(normalized, safe="-")


def note_url(note: Note) -> str:
    return f"notes/{note.slug}.html"


def parse_date(value: Any, source_path: Path) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"{source_path}: date must use YYYY-MM-DD") from exc
    raise ValueError(f"{source_path}: date must use YYYY-MM-DD")


def parse_front_matter(text: str, source_path: Path) -> tuple[dict[str, Any], str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError(f"{source_path}: missing YAML front matter")

    raw_metadata, body = match.groups()
    metadata = yaml.safe_load(raw_metadata) or {}
    if not isinstance(metadata, dict):
        raise ValueError(f"{source_path}: front matter must be a mapping")

    return metadata, body.strip()


def metadata_text(metadata: dict[str, Any], key: str, source_path: Path) -> str:
    value = metadata.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{source_path}: {key} must be a non-empty string")
    return value.strip()


def metadata_tags(metadata: dict[str, Any], source_path: Path) -> tuple[str, ...]:
    value = metadata.get("tags")
    if not isinstance(value, list):
        raise ValueError(f"{source_path}: tags must be a YAML list")

    tags = tuple(str(tag).strip() for tag in value if str(tag).strip())
    if not tags:
        raise ValueError(f"{source_path}: tags must include at least one tag")
    return tags


def render_markdown(markdown_text: str) -> str:
    return markdown.markdown(
        markdown_text,
        extensions=["extra", "sane_lists"],
        output_format="html5",
    )


def parse_note(path: Path) -> Note:
    metadata, body = parse_front_matter(path.read_text(encoding="utf-8"), path)
    note_date = parse_date(metadata.get("date"), path)
    return Note(
        source_path=path,
        slug=path.stem,
        title=metadata_text(metadata, "title", path),
        date=note_date,
        tags=metadata_tags(metadata, path),
        summary=metadata_text(metadata, "summary", path),
        body_markdown=body,
        body_html=render_markdown(body),
    )


def load_notes(notes_dir: Path) -> list[Note]:
    notes = [parse_note(path) for path in sorted(notes_dir.glob("*.md"))]
    return sorted(notes, key=lambda note: (note.date, note.title), reverse=True)


def tag_link(tag: str, base: str = "") -> str:
    return f'<a class="tag" href="{base}#tag-{tag_slug(tag)}">#{escape(tag)}</a>'


def render_tag_links(tags: tuple[str, ...], base: str = "") -> str:
    return '<span class="tag-list">' + "".join(tag_link(tag, base) for tag in tags) + "</span>"


def render_note_card(note: Note) -> str:
    return f"""
<article class="note-card">
  <p class="note-date">{note.date.isoformat()}</p>
  <h3><a href="{note_url(note)}">{escape(note.title)}</a></h3>
  <p>{escape(note.summary)}</p>
  {render_tag_links(note.tags)}
</article>
""".strip()


def group_notes_by_tag(notes: list[Note]) -> dict[str, list[Note]]:
    grouped: dict[str, list[Note]] = {}
    for note in notes:
        for tag in note.tags:
            grouped.setdefault(tag, []).append(note)
    return dict(sorted(grouped.items(), key=lambda item: item[0].casefold()))


def render_tag_index(notes: list[Note]) -> str:
    groups = group_notes_by_tag(notes)
    if not groups:
        return '<p class="empty-state">还没有标签。</p>'

    sections = []
    for tag, tagged_notes in groups.items():
        links = "".join(
            f'<li><a href="{note_url(note)}">{escape(note.title)}</a></li>'
            for note in tagged_notes
        )
        sections.append(
            f"""
<section class="tag-group" id="tag-{tag_slug(tag)}">
  <h3>#{escape(tag)}</h3>
  <ul>{links}</ul>
</section>
""".strip()
        )
    return "\n".join(sections)


def render_index(notes: list[Note]) -> str:
    if notes:
        note_cards = "\n".join(render_note_card(note) for note in notes)
    else:
        note_cards = '<p class="empty-state">还没有发布笔记。</p>'

    return f"""
<section class="hero">
  <p class="eyebrow">{SITE_NAME}</p>
  <h1>个人知识笔记</h1>
  <p>{SITE_DESCRIPTION}</p>
</section>

<section class="content-section">
  <h2>最新笔记</h2>
  <div class="note-list">{note_cards}</div>
</section>

<section class="content-section">
  <h2>标签索引</h2>
  <div class="tag-index">{render_tag_index(notes)}</div>
</section>
""".strip()


def render_note_page(note: Note) -> str:
    return f"""
<article class="note-page">
  <nav class="breadcrumb"><a href="../index.html">首页</a></nav>
  <header class="note-header">
    <p class="note-date">{note.date.isoformat()}</p>
    <h1>{escape(note.title)}</h1>
    <p>{escape(note.summary)}</p>
    {render_tag_links(note.tags, "../index.html")}
  </header>
  <div class="prose">
    {note.body_html}
  </div>
</article>
""".strip()


def render_layout(root: Path, title: str, description: str, content: str, body_class: str, asset_prefix: str = "") -> str:
    template_path = root / "templates" / "layout.html"
    template = template_path.read_text(encoding="utf-8")
    page_title = SITE_NAME if title == SITE_NAME else f"{title} - {SITE_NAME}"
    replacements = {
        "{{ title }}": escape(page_title),
        "{{ description }}": escape(description),
        "{{ site_name }}": escape(SITE_NAME),
        "{{ content }}": content,
        "{{ body_class }}": escape(body_class),
        "{{ asset_prefix }}": asset_prefix,
    }
    for token, value in replacements.items():
        template = template.replace(token, value)
    return template


def prepare_site_dir(site_dir: Path) -> None:
    if site_dir.exists():
        shutil.rmtree(site_dir)
    (site_dir / "notes").mkdir(parents=True)


def copy_static_files(root: Path, site_dir: Path) -> None:
    assets_dir = root / "assets"
    if assets_dir.exists():
        shutil.copytree(assets_dir, site_dir / "assets")

    cname_path = root / "CNAME"
    if cname_path.exists():
        shutil.copy2(cname_path, site_dir / "CNAME")


def build_site(root: Path = ROOT) -> None:
    root = Path(root)
    notes_dir = root / "notes"
    site_dir = root / "site"

    notes = load_notes(notes_dir)
    prepare_site_dir(site_dir)
    copy_static_files(root, site_dir)

    index_html = render_layout(
        root=root,
        title=SITE_NAME,
        description=SITE_DESCRIPTION,
        content=render_index(notes),
        body_class="home",
    )
    (site_dir / "index.html").write_text(index_html, encoding="utf-8")

    for note in notes:
        note_html = render_layout(
            root=root,
            title=note.title,
            description=note.summary,
            content=render_note_page(note),
            body_class="note",
            asset_prefix="../",
        )
        (site_dir / "notes" / f"{note.slug}.html").write_text(note_html, encoding="utf-8")


def main() -> None:
    build_site(ROOT)
    print(f"Built site into {ROOT / 'site'}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Run tests to verify pass**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: PASS with all `BuildSiteTests` tests reporting `ok`.

- [ ] **Step 7: Commit task**

Run:

```bash
git add requirements.txt scripts/build.py tests/test_build.py
git commit -m "Add notes site generator"
```

Expected: commit succeeds.

---

### Task 2: Site Template, Styling, and First Note

**Files:**
- Create: `templates/layout.html`
- Create: `assets/style.css`
- Create: `notes/2026-07-21-welcome.md`

**Interfaces:**
- Consumes: `scripts/build.py` reads `templates/layout.html`, `assets/`, and `notes/*.md`.
- Produces: usable local preview under `site/` after `python3 scripts/build.py`.

- [ ] **Step 1: Add shared HTML layout**

Create `templates/layout.html`:

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="{{ description }}">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="{{ asset_prefix }}assets/style.css">
  </head>
  <body class="{{ body_class }}">
    <header class="site-header">
      <a class="site-title" href="{{ asset_prefix }}index.html">{{ site_name }}</a>
      <nav aria-label="Primary navigation">
        <a href="{{ asset_prefix }}index.html">首页</a>
      </nav>
    </header>
    <main>
      {{ content }}
    </main>
    <footer class="site-footer">
      <p>这里记录技术、思考和长期积累的笔记。</p>
    </footer>
  </body>
</html>
```

- [ ] **Step 2: Add site stylesheet**

Create `assets/style.css`:

```css
:root {
  color-scheme: light;
  --bg: #f7f4ee;
  --surface: #fffaf2;
  --text: #26231f;
  --muted: #6f675d;
  --line: #ded4c5;
  --accent: #2f6f73;
  --accent-soft: #dceceb;
  --link: #245f63;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.7;
}

a {
  color: var(--link);
  text-decoration-thickness: 0.08em;
  text-underline-offset: 0.18em;
}

.site-header,
.site-footer,
main {
  width: min(100% - 32px, 920px);
  margin: 0 auto;
}

.site-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 0;
  border-bottom: 1px solid var(--line);
}

.site-title {
  color: var(--text);
  font-weight: 700;
  text-decoration: none;
}

.site-header nav a {
  color: var(--muted);
  font-size: 0.95rem;
}

.hero {
  padding: 72px 0 48px;
}

.eyebrow,
.note-date {
  margin: 0 0 8px;
  color: var(--muted);
  font-size: 0.9rem;
}

h1,
h2,
h3 {
  line-height: 1.25;
}

h1 {
  margin: 0 0 18px;
  font-size: clamp(2.25rem, 7vw, 4.5rem);
  letter-spacing: 0;
}

h2 {
  margin: 0 0 20px;
  font-size: 1.5rem;
}

.hero p:last-child {
  max-width: 620px;
  margin: 0;
  color: var(--muted);
  font-size: 1.08rem;
}

.content-section {
  padding: 32px 0;
  border-top: 1px solid var(--line);
}

.note-list {
  display: grid;
  gap: 16px;
}

.note-card {
  padding: 20px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
}

.note-card h3 {
  margin: 0 0 8px;
  font-size: 1.25rem;
}

.note-card p {
  margin: 0 0 12px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 0.9rem;
  text-decoration: none;
}

.tag-index {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.tag-group {
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(255, 250, 242, 0.7);
}

.tag-group h3 {
  margin: 0 0 10px;
}

.tag-group ul {
  margin: 0;
  padding-left: 20px;
}

.note-page {
  max-width: 760px;
  padding: 48px 0;
}

.breadcrumb {
  margin-bottom: 32px;
}

.note-header {
  margin-bottom: 36px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--line);
}

.note-header p {
  color: var(--muted);
}

.prose {
  font-size: 1.05rem;
}

.prose img {
  max-width: 100%;
  height: auto;
}

.prose code {
  padding: 0.15em 0.3em;
  border-radius: 4px;
  background: #ebe3d6;
}

.prose pre {
  overflow-x: auto;
  padding: 16px;
  border-radius: 8px;
  background: #1f2526;
  color: #f5f2ea;
}

.prose pre code {
  padding: 0;
  background: transparent;
}

.site-footer {
  padding: 36px 0;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.95rem;
}

.empty-state {
  color: var(--muted);
}

@media (max-width: 640px) {
  .site-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .hero {
    padding: 48px 0 32px;
  }

  .note-card,
  .tag-group {
    padding: 16px;
  }
}
```

- [ ] **Step 3: Add first note**

Create `notes/2026-07-21-welcome.md`:

```md
---
title: 开始记录
date: 2026-07-21
tags: [notes, codex]
summary: 这个个人知识笔记从一条清晰的写作和发布链路开始。
---

# 开始记录

这里会逐步记录技术、思考和长期积累的笔记。

第一版目标很简单：用 Markdown 写作，由脚本生成静态 HTML，再通过 GitHub Pages 发布到 `zhengyuhong.cn`。
```

- [ ] **Step 4: Generate local site**

Run:

```bash
python3 scripts/build.py
```

Expected: output contains `Built site into` and `site/index.html` exists.

- [ ] **Step 5: Run tests**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: PASS with all `BuildSiteTests` tests reporting `ok`.

- [ ] **Step 6: Inspect generated files**

Run:

```bash
python3 -m http.server 8000 -d site
```

Expected: local server starts at `http://0.0.0.0:8000/`. Open `http://localhost:8000/` and confirm the homepage shows `个人知识笔记` and the first note.

- [ ] **Step 7: Commit task**

Stop the local server, then run:

```bash
git add templates/layout.html assets/style.css notes/2026-07-21-welcome.md
git commit -m "Add notes site template"
```

Expected: commit succeeds.

---

### Task 3: GitHub Pages Publishing

**Files:**
- Create: `.github/workflows/pages.yml`
- Create: `.gitignore`
- Delete: `index.html`

**Interfaces:**
- Consumes: `python3 scripts/build.py` writes `site/`.
- Produces: GitHub Pages deployment from the generated `site/` artifact.

- [ ] **Step 1: Ignore generated output and caches**

Create `.gitignore`:

```gitignore
site/
__pycache__/
.pytest_cache/
*.pyc
```

- [ ] **Step 2: Add GitHub Pages workflow**

Create `.github/workflows/pages.yml`:

```yaml
name: Build and publish notes site

on:
  push:
    branches:
      - master
      - main
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: python -m unittest discover -s tests -v

      - name: Build site
        run: python scripts/build.py

      - name: Configure Pages
        uses: actions/configure-pages@v5

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: site

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 3: Delete old root homepage**

Delete `index.html`. The generated homepage now lives at `site/index.html` during builds and is published by the workflow.

- [ ] **Step 4: Verify local build still works**

Run:

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests -v
test -f site/index.html
test -f site/CNAME
```

Expected: build succeeds, tests pass, and both `test` commands exit successfully.

- [ ] **Step 5: Commit task**

Run:

```bash
git add .github/workflows/pages.yml .gitignore index.html
git commit -m "Add GitHub Pages workflow"
```

Expected: commit succeeds and records deletion of `index.html`.

---

### Task 4: Documentation and Contributor Guidance

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`

**Interfaces:**
- Consumes: final commands from Tasks 1-3.
- Produces: reader-facing instructions for writing notes, previewing locally, testing, and publishing.

- [ ] **Step 1: Update README**

Replace `README.md` with:

````md
# zhengyuhong.cn

This repository contains the Markdown source and static generator for the personal notes site published at `zhengyuhong.cn`.

## Write a Note

Create a Markdown file in `notes/` using a date-prefixed filename:

```text
notes/2026-07-21-some-topic.md
```

Each note starts with YAML front matter:

```md
---
title: Some Topic
date: 2026-07-21
tags: [notes, codex]
summary: One sentence summary.
---
```

## Preview Locally

```bash
pip install -r requirements.txt
python3 scripts/build.py
python3 -m http.server 8000 -d site
```

Open `http://localhost:8000/`.

## Test

```bash
python3 -m unittest discover -s tests -v
```

## Publish

Push to `master` or `main`. GitHub Actions builds `site/` and deploys it to GitHub Pages. In repository settings, Pages must use the GitHub Actions source.
````

- [ ] **Step 2: Update AGENTS.md**

Replace `AGENTS.md` with:

```md
# Repository Guidelines

## Project Structure & Module Organization

This repository is a Markdown-authored GitHub Pages site for `zhengyuhong.cn`. Write source notes in `notes/` using `YYYY-MM-DD-title.md` filenames. Shared layout lives in `templates/layout.html`, styling in `assets/style.css`, the generator in `scripts/build.py`, and tests in `tests/`. The `site/` directory is generated output and should not be edited by hand.

## Build, Test, and Development Commands

- `pip install -r requirements.txt` - install Markdown and YAML parsing dependencies.
- `python3 scripts/build.py` - generate the static site into `site/`.
- `python3 -m http.server 8000 -d site` - preview the generated site at `http://localhost:8000/`.
- `python3 -m unittest discover -s tests -v` - run generator tests.

## Coding Style & Naming Conventions

Use 4-space indentation for Python and 2-space indentation for HTML/CSS. Keep Python functions small and deterministic. Use lowercase hyphenated note filenames such as `2026-07-21-reading-notes.md`. Keep front matter fields named `title`, `date`, `tags`, and `summary`.

## Testing Guidelines

Add or update `tests/test_build.py` when changing parsing, rendering, URLs, asset copying, or publishing assumptions. Run the full unittest command before committing. For visual changes, build locally and inspect the homepage plus at least one note page.

## Commit & Pull Request Guidelines

Use short imperative commit subjects, following the existing style such as `Create CNAME` and `Add notes site generator`. Pull requests should summarize user-facing site changes, note publishing workflow changes, and include screenshots for visual updates.

## Security & Configuration Tips

Do not commit secrets, tokens, analytics credentials, or private drafts. Keep `CNAME` at the repository root and ensure the build copies it into `site/`.
```

- [ ] **Step 3: Run final verification**

Run:

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests -v
```

Expected: build succeeds and all tests report `ok`.

- [ ] **Step 4: Confirm generated files are ignored**

Run:

```bash
git status --short
```

Expected: `site/` does not appear in the status output.

- [ ] **Step 5: Commit task**

Run:

```bash
git add README.md AGENTS.md
git commit -m "Document notes workflow"
```

Expected: commit succeeds.

---

### Task 5: Final Review and Release Readiness

**Files:**
- Inspect: `docs/superpowers/specs/2026-07-21-notes-site-design.md`
- Inspect: `requirements.txt`
- Inspect: `scripts/build.py`
- Inspect: `tests/test_build.py`
- Inspect: `templates/layout.html`
- Inspect: `assets/style.css`
- Inspect: `notes/2026-07-21-welcome.md`
- Inspect: `.github/workflows/pages.yml`
- Inspect: `README.md`
- Inspect: `AGENTS.md`

**Interfaces:**
- Consumes: all previous task outputs.
- Produces: verified branch ready to push.

- [ ] **Step 1: Check spec coverage**

Run:

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests -v
git status --short
```

Expected: build succeeds, tests pass, and only intentional uncommitted files appear. If all previous task commits succeeded, status should be clean.

- [ ] **Step 2: Inspect generated homepage**

Run:

```bash
sed -n '1,220p' site/index.html
```

Expected: output includes `个人知识笔记`, `开始记录`, `#notes`, and `#codex`.

- [ ] **Step 3: Inspect generated note page**

Run:

```bash
sed -n '1,220p' site/notes/2026-07-21-welcome.html
```

Expected: output includes `开始记录`, `2026-07-21`, `第一版目标很简单`, and links back to `../index.html`.

- [ ] **Step 4: Confirm workflow keeps custom domain**

Run:

```bash
test "$(cat site/CNAME)" = "zhengyuhong.cn"
```

Expected: command exits successfully.

- [ ] **Step 5: Commit final corrections if needed**

If Step 1 through Step 4 reveal a concrete issue, edit only the affected source files, rerun:

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests -v
```

Then commit with:

```bash
git add requirements.txt scripts/build.py tests/test_build.py templates/layout.html assets/style.css notes/2026-07-21-welcome.md .github/workflows/pages.yml .gitignore README.md AGENTS.md
git commit -m "Polish notes site setup"
```

Expected: commit succeeds only when corrections were necessary.
