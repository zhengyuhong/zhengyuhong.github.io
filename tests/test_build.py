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
