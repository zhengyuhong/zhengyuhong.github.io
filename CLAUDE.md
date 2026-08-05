# Claude Code Instructions

Read and follow `AGENTS.md` first; it is the source of truth for this notes site and is also the shared rule file used by Codex and opencode.

When using `paper-comic` for a paper note in this repository:

- Default to Chinese output, `sketchnote` style, and the use case “论文阅读笔记”.
- Prefer a multi-image explanation within the skill's 1-10 page limit, covering method flow, core mechanisms, and key results.
- Use the original paper title plus “图解” for the front matter `title` and the body H1, formatted as `<paper title> 图解`. Do not use “图解笔记”, “深度解读”, or a generic Chinese rewrite.
- Publish the final Markdown under `notes/YYYY-MM-DD-<paper-title-slug>-comic.md`: use a lowercase kebab-case slug from the paper title, or pinyin kebab-case when the paper title is Chinese. Avoid generic topic slugs or arbitrary abbreviations.
- Put generated images under `assets/images/<note-slug>/` and reference them with relative paths from the note.
- Build with `python3 scripts/build.py`, test with `python3 -m unittest discover -s tests -v`, then commit and push the paper note to `main` when publishing.

When using `paper-deck` for a paper deck in this repository:

- Keep `paper-deck`'s raster-first workflow: analysis, confirmation, `deck-brief.md`, `outline.md`, prompt files, real image generation, `generation-log.md`, then PPTX/PDF.
- Align content defaults with `paper-comic`: Chinese output, method flow, core mechanisms, and key results; avoid spending slides on generic background, related work, vague inspiration, or minor ablations.
- Default to a warm, clear, academic visual direction such as `warm-notes` or `journal-minimal` for paper reading / group meeting decks, unless the user requests another style.
- Use the original paper title plus “解读” on the cover, in `deck-brief.md`, and in `outline.md`, formatted as `<paper title> 解读`. Do not use “图解笔记”, “深度解读”, “论文PPT”, or a generic Chinese rewrite.
- Use the paper-title slug plus `deck` for the output directory and deck files: `paper-deck/<paper-title-slug>-deck/<paper-title-slug>-deck.pptx` and `.pdf`; use lowercase kebab-case for English titles or pinyin kebab-case for Chinese titles.
- If the deck should be published to `zhengyuhong.github.io`, also create a matching note under `notes/YYYY-MM-DD-<paper-title-slug>-deck.md` with title/H1 `<paper title> 解读` that links the deck and follows the site note rules.

Do not manually edit `site/`, do not commit temporary outputs, and do not mix unrelated user changes into a publication commit.
