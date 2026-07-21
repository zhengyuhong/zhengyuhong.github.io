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
NOTE_FILENAME_RE = re.compile(r"\A(\d{4}-\d{2}-\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.md\Z")
ATX_H1_RE = re.compile(
    r"\A {0,3}#(?!#)[ \t]+(?P<heading>.*?)(?:[ \t]+#+[ \t]*)?(?:\n|\Z)"
)


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
    return re.sub(r"\s+", "-", tag.strip().lower())


def tag_fragment(tag: str) -> str:
    return quote(tag_slug(tag), safe="-_")


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

    if any(not isinstance(tag, str) or not tag.strip() for tag in value):
        raise ValueError(f"{source_path}: tags must contain only non-empty strings")

    tags = tuple(dict.fromkeys(tag.strip() for tag in value))
    if not tags:
        raise ValueError(f"{source_path}: tags must include at least one tag")
    return tags


def render_markdown(markdown_text: str) -> str:
    return markdown.markdown(
        markdown_text,
        extensions=["extra", "sane_lists"],
        output_format="html5",
    )


def strip_duplicate_title(body: str, title: str) -> str:
    match = ATX_H1_RE.match(body)
    if not match or match.group("heading").rstrip() != title:
        return body
    return body[match.end():].lstrip()


def validate_note_filename(path: Path, note_date: date) -> None:
    match = NOTE_FILENAME_RE.match(path.name)
    if not match:
        raise ValueError(f"{path}: filename must use YYYY-MM-DD-title.md")

    try:
        filename_date = date.fromisoformat(match.group(1))
    except ValueError as exc:
        raise ValueError(f"{path}: filename must use YYYY-MM-DD-title.md") from exc

    if filename_date != note_date:
        raise ValueError(f"{path}: filename date must match front matter date")


def parse_note(path: Path) -> Note:
    metadata, body = parse_front_matter(path.read_text(encoding="utf-8"), path)
    note_date = parse_date(metadata.get("date"), path)
    title = metadata_text(metadata, "title", path)
    validate_note_filename(path, note_date)
    body_markdown = strip_duplicate_title(body, title)
    return Note(
        source_path=path,
        slug=path.stem,
        title=title,
        date=note_date,
        tags=metadata_tags(metadata, path),
        summary=metadata_text(metadata, "summary", path),
        body_markdown=body_markdown,
        body_html=render_markdown(body_markdown),
    )


def load_notes(notes_dir: Path) -> list[Note]:
    notes = [parse_note(path) for path in sorted(notes_dir.glob("*.md"))]
    return sorted(notes, key=lambda note: (note.date, note.title), reverse=True)


def tag_link(tag: str, base: str = "") -> str:
    return f'<a class="tag" href="{base}#tag-{tag_fragment(tag)}">#{escape(tag)}</a>'


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
<section class="tag-group" id="tag-{escape(tag_slug(tag), quote=True)}">
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
  <h1>个人知识花园</h1>
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
        "{{ body_class }}": escape(body_class),
        "{{ asset_prefix }}": asset_prefix,
    }
    for token, value in replacements.items():
        template = template.replace(token, value)
    return template.replace("{{ content }}", content)


def prepare_site_dir(site_dir: Path) -> None:
    if site_dir.exists():
        shutil.rmtree(site_dir)
    (site_dir / "notes").mkdir(parents=True)


def copy_static_files(root: Path, site_dir: Path) -> None:
    assets_dir = root / "assets"
    if assets_dir.exists():
        shutil.copytree(assets_dir, site_dir / "assets")

    cname_path = root / "CNAME"
    if not cname_path.exists():
        raise FileNotFoundError(cname_path)
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
