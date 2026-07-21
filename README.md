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
