# Pagefind Search Design

## Goal

Add private, fully static site search to the Markdown notes site. Readers should be able to search note titles, summaries, tags, and rendered note bodies without any backend service.

## Approach

Use Pagefind after the existing Python static build. `scripts/build.py` will continue to generate HTML into `site/`; a separate Pagefind indexing step can scan that output and write the static `site/pagefind/` bundle.

The site template will load a small local search script. The homepage will include a compact search panel above the latest notes list. Note pages will expose metadata and filters through `data-pagefind-*` attributes so Pagefind can return useful results and filter by tags.

## User Experience

The homepage search panel contains a text input, a status line, tag filter controls, and a result list. Results show title, excerpt, date, and matching tags. Empty, loading, and error states should be quiet and readable.

## Data Flow

1. Notes are parsed from Markdown front matter.
2. The generator renders note pages with Pagefind metadata for title, date, summary, and tag filters.
3. Static assets are copied into `site/assets/`.
4. Pagefind indexes `site/` and emits `site/pagefind/`.
5. The browser-side script imports `pagefind/pagefind.js` and queries the index.

## Error Handling

If the Pagefind bundle is unavailable, the search panel explains that the search index is not ready. The rest of the site still works. If a query is empty, the panel resets to its default state.

## Testing

Unit tests should verify that generated pages contain Pagefind metadata and the homepage includes the search container. A local build should still pass, and Pagefind indexing should be run when the CLI is available.
