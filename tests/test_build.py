from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.build import build_site, load_notes, strip_duplicate_title, tag_slug


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
        self.assertEqual(tag_slug("长期思考"), "长期思考")

    def test_build_site_uses_raw_tag_ids_and_encoded_tag_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_layout(root)
            self.write_note(
                root,
                "2026-07-21-chinese-tag.md",
                """---
title: Chinese Tag
date: 2026-07-21
tags: [长期思考]
summary: A Chinese tag.
---

Body
""",
            )
            (root / "CNAME").write_text("zhengyuhong.cn\n", encoding="utf-8")

            build_site(root)

            index_html = (root / "site" / "index.html").read_text(encoding="utf-8")
            self.assertIn('href="#tag-%E9%95%BF%E6%9C%9F%E6%80%9D%E8%80%83"', index_html)
            self.assertIn('id="tag-长期思考"', index_html)

    def test_build_site_keeps_punctuation_in_tag_ids_and_encodes_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_layout(root)
            self.write_note(
                root,
                "2026-07-21-punctuation-tags.md",
                """---
title: Punctuation Tags
date: 2026-07-21
tags: [C++, C#, "!!!"]
summary: A punctuation tag test.
---

Body
""",
            )
            (root / "CNAME").write_text("zhengyuhong.cn\n", encoding="utf-8")

            build_site(root)

            index_html = (root / "site" / "index.html").read_text(encoding="utf-8")
            self.assertIn('id="tag-c++"', index_html)
            self.assertIn('id="tag-c#"', index_html)
            self.assertIn('id="tag-!!!"', index_html)
            self.assertIn('href="#tag-c%2B%2B"', index_html)
            self.assertIn('href="#tag-c%23"', index_html)
            self.assertIn('href="#tag-%21%21%21"', index_html)

    def test_note_page_strips_duplicate_leading_markdown_title(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_layout(root)
            self.write_note(
                root,
                "2026-07-21-duplicate-title.md",
                """---
title: Duplicate Title
date: 2026-07-21
tags: [notes]
summary: A title test.
---

# Duplicate Title

Body
""",
            )
            (root / "CNAME").write_text("zhengyuhong.cn\n", encoding="utf-8")

            build_site(root)

            note_html = (root / "site" / "notes" / "2026-07-21-duplicate-title.html").read_text(encoding="utf-8")
            self.assertEqual(note_html.count("<h1>Duplicate Title</h1>"), 1)

    def test_strip_duplicate_title_accepts_equivalent_atx_h1_forms(self) -> None:
        self.assertEqual(strip_duplicate_title("# Duplicate Title #\n\nBody", "Duplicate Title"), "Body")
        self.assertEqual(strip_duplicate_title("# Duplicate Title  \n\nBody", "Duplicate Title"), "Body")

    def test_strip_duplicate_title_keeps_non_h1_and_different_titles(self) -> None:
        self.assertEqual(strip_duplicate_title("## Duplicate Title\n\nBody", "Duplicate Title"), "## Duplicate Title\n\nBody")
        self.assertEqual(strip_duplicate_title("# Another Title\n\nBody", "Duplicate Title"), "# Another Title\n\nBody")

    def test_load_notes_rejects_invalid_filename(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_note(
                root,
                "welcome.md",
                """---
title: Welcome
date: 2026-07-21
tags: [notes]
summary: A welcome note.
---

Body
""",
            )

            with self.assertRaisesRegex(ValueError, "filename must use YYYY-MM-DD-title.md"):
                load_notes(root / "notes")

    def test_load_notes_rejects_filename_date_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_note(
                root,
                "2026-07-20-welcome.md",
                """---
title: Welcome
date: 2026-07-21
tags: [notes]
summary: A welcome note.
---

Body
""",
            )

            with self.assertRaisesRegex(ValueError, "filename date must match front matter date"):
                load_notes(root / "notes")

    def test_rendered_content_preserves_template_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_layout(root)
            self.write_note(
                root,
                "2026-07-21-template-token.md",
                """---
title: Template Token
date: 2026-07-21
tags: [notes]
summary: A template test.
---

Literal {{ body_class }} text.
""",
            )
            (root / "CNAME").write_text("zhengyuhong.cn\n", encoding="utf-8")

            build_site(root)

            note_html = (root / "site" / "notes" / "2026-07-21-template-token.html").read_text(encoding="utf-8")
            self.assertIn("Literal {{ body_class }} text.", note_html)

    def test_build_site_requires_root_cname(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_layout(root)
            self.write_note(
                root,
                "2026-07-21-no-cname.md",
                """---
title: No CNAME
date: 2026-07-21
tags: [notes]
summary: A CNAME test.
---

Body
""",
            )

            with self.assertRaises(FileNotFoundError):
                build_site(root)

    def test_load_notes_rejects_non_string_tags(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_note(
                root,
                "2026-07-21-non-string-tags.md",
                """---
title: Non-string Tags
date: 2026-07-21
tags: [notes, 42]
summary: A tag validation test.
---

Body
""",
            )

            with self.assertRaisesRegex(ValueError, "tags must contain only non-empty strings"):
                load_notes(root / "notes")

    def test_load_notes_deduplicates_tags_preserving_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_note(
                root,
                "2026-07-21-duplicate-tags.md",
                """---
title: Duplicate Tags
date: 2026-07-21
tags: [notes, codex, notes, writing, codex]
summary: A tag deduplication test.
---

Body
""",
            )

            notes = load_notes(root / "notes")

            self.assertEqual(notes[0].tags, ("notes", "codex", "writing"))

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
