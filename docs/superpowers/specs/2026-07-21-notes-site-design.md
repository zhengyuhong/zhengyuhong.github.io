# Notes Site Design

## Goal

Turn `zhengyuhong.github.io` into a personal notes repository published at `zhengyuhong.cn`. The authoring workflow should be simple: write Markdown notes with Codex, push to GitHub, and let GitHub Actions generate and publish the static website.

## Chosen Approach

Use handwritten Markdown files as the source of truth and a lightweight static generator script to build HTML. GitHub Actions will run the generator on each push and publish the generated site directory through GitHub Pages.

The generator will be a small Python script. It can use a minimal `requirements.txt` for established Markdown and YAML parsing libraries, but it should avoid introducing a full static-site framework in the first version. This keeps the repository understandable and lets Codex create or update notes without touching generated HTML.

## Repository Structure

```text
notes/
  2026-07-21-first-note.md
templates/
  layout.html
scripts/
  build.py
requirements.txt
site/
  index.html
  notes/
    2026-07-21-first-note.html
assets/
  style.css
.github/workflows/
  pages.yml
CNAME
```

`notes/` is the primary writing surface. `site/` is generated output. `assets/` contains shared static styling. `CNAME` stays at the repository root and is copied into `site/` during the build so the custom domain remains active.

## Note Format

Each note uses a date-prefixed filename and YAML front matter:

```md
---
title: A Note Title
date: 2026-07-21
tags: [thinking, codex]
summary: One sentence summary.
---

# A Note Title

Markdown body content.
```

The canonical URL for `notes/2026-07-21-some-topic.md` is `/notes/2026-07-21-some-topic.html`.

## Build Flow

The generator will:

1. Read every `notes/*.md` file.
2. Parse front matter fields: `title`, `date`, `tags`, and `summary`.
3. Convert Markdown bodies to HTML.
4. Generate one HTML page per note under `site/notes/`.
5. Generate `site/index.html` with a personal intro, newest notes, and a tag index.
6. Copy `assets/` and `CNAME` into `site/`.

Local preview should use the same generator:

```bash
python3 scripts/build.py
python3 -m http.server 8000 -d site
```

## Publishing Flow

GitHub Actions will run on push. If generation succeeds, it publishes `site/` to GitHub Pages. If generation fails, the workflow fails and no broken site is published.

## Page Design

The homepage should feel like a personal knowledge garden: calm, readable, and exploratory. It includes a short identity line for `zhengyuhong.cn`, a concise personal description, latest notes sorted by date descending, summaries, and tags.

Note pages prioritize reading. Each page has navigation back to the homepage, title, date, tags, and a clean article body. Tag links can point to tag sections on the homepage in the first version; separate tag archive pages can come later. First-version styling lives in `assets/style.css` and should work well on mobile and desktop.

## First-Version Scope

Include Markdown-to-HTML generation, homepage generation, note pages, homepage tag sections, local preview commands, and GitHub Actions publishing. Defer full-text search, RSS, separate tag archive pages, related-note recommendations, comments, analytics, and complex theming.
