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
