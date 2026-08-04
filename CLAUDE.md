# Claude Code Instructions

Read and follow `AGENTS.md` first; it is the source of truth for this notes site and is also the shared rule file used by Codex and opencode.

When using `paper-comic` for a paper note in this repository:

- Default to Chinese output, `sketchnote` style, and the use case “论文阅读笔记”.
- Prefer a multi-image explanation within the skill's 1-10 page limit, covering method flow, core mechanisms, and key results.
- Use the original paper title for the front matter `title` and the body H1. Do not append “图解笔记”, “深度解读”, or a generic Chinese rewrite to the published title.
- Publish the final Markdown under `notes/YYYY-MM-DD-<paper-title-slug>.md`: use a lowercase kebab-case slug from the paper title, or pinyin kebab-case when the paper title is Chinese. Avoid generic topic slugs or arbitrary abbreviations.
- Put generated images under `assets/images/<note-slug>/` and reference them with relative paths from the note.
- Build with `python3 scripts/build.py`, test with `python3 -m unittest discover -s tests -v`, then commit and push the paper note to `main` when publishing.

Do not manually edit `site/`, do not commit temporary outputs, and do not mix unrelated user changes into a publication commit.
