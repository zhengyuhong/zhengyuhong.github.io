# Pagefind Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add fully static Pagefind search to the Markdown notes site.

**Architecture:** The Python generator renders Pagefind-aware HTML into `site/`. A local browser script imports the Pagefind bundle generated after build and drives the homepage search UI. GitHub Actions runs Pagefind before uploading the Pages artifact.

**Tech Stack:** Python 3.12, `unittest`, vanilla HTML/CSS/JavaScript, Pagefind CLI, GitHub Actions, GitHub Pages.

## Global Constraints

- Search must not require a backend service.
- `site/` remains generated output and should not be edited by hand.
- The homepage owns the visible search UI.
- Note pages expose title, date, summary, body, and tag filters through `data-pagefind-*` attributes.
- If `site/pagefind/` is missing during local preview, the site should still render and the search UI should show a quiet error after interaction.
- GitHub Actions must generate the Pagefind bundle after `python scripts/build.py` and before uploading `site/`.

---

## File Structure

- Modify `scripts/build.py`: render homepage search markup, Pagefind metadata, and tag filter attributes.
- Modify `templates/layout.html`: load `assets/search.js`.
- Create `assets/search.js`: lazy-load Pagefind, render filters, run searches, and display results.
- Modify `assets/style.css`: style the search panel, filters, results, and status states.
- Modify `.github/workflows/pages.yml`: install Node and run `npx -y pagefind --site site`.
- Modify `README.md`: document local Pagefind indexing for full search previews.
- Modify `tests/test_build.py`: cover search markup and Pagefind metadata in generated HTML.

---

### Task 1: Generated Search Markup Tests

**Files:**
- Modify: `tests/test_build.py`

**Interfaces:**
- Consumes: `build_site(root: Path) -> None`
- Produces: tests that assert the homepage search container and note Pagefind metadata are generated.

- [ ] **Step 1: Write failing tests**

Add these tests to `BuildSiteTests`:

```python
    def test_homepage_includes_search_mount(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_layout(root)
            self.write_note(
                root,
                "2026-07-21-searchable.md",
                """---
title: Searchable Note
date: 2026-07-21
tags: [search, notes]
summary: A searchable summary.
---

Body
""",
            )
            (root / "CNAME").write_text("zhengyuhong.cn\n", encoding="utf-8")

            build_site(root)

            index_html = (root / "site" / "index.html").read_text(encoding="utf-8")
            self.assertIn('class="search-section"', index_html)
            self.assertIn('data-search-root', index_html)
            self.assertIn('id="site-search-input"', index_html)

    def test_note_page_exposes_pagefind_metadata_and_filters(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_layout(root)
            self.write_note(
                root,
                "2026-07-21-pagefind.md",
                """---
title: Pagefind Note
date: 2026-07-21
tags: [C++, 长期思考]
summary: A Pagefind summary.
---

Body
""",
            )
            (root / "CNAME").write_text("zhengyuhong.cn\n", encoding="utf-8")

            build_site(root)

            note_html = (root / "site" / "notes" / "2026-07-21-pagefind.html").read_text(encoding="utf-8")
            self.assertIn('data-pagefind-body', note_html)
            self.assertIn('data-pagefind-meta="title"', note_html)
            self.assertIn('data-pagefind-meta="date"', note_html)
            self.assertIn('data-pagefind-meta="summary"', note_html)
            self.assertIn('data-pagefind-filter="tag[data-pagefind-tag]" data-pagefind-tag="C++"', note_html)
            self.assertIn('data-pagefind-filter="tag[data-pagefind-tag]" data-pagefind-tag="长期思考"', note_html)
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: FAIL because the search container and Pagefind attributes do not exist yet.

---

### Task 2: Generator and Template Integration

**Files:**
- Modify: `scripts/build.py`
- Modify: `templates/layout.html`
- Modify: `tests/test_build.py`

**Interfaces:**
- Produces: `render_search_panel() -> str`
- Changes: `tag_link(tag: str, base: str = "", pagefind_filter: bool = False) -> str`
- Changes: `render_tag_links(tags: tuple[str, ...], base: str = "", pagefind_filters: bool = False) -> str`

- [ ] **Step 1: Add search panel renderer**

Add this function near `render_note_card` in `scripts/build.py`:

```python
def render_search_panel() -> str:
    return """
<section class="content-section search-section" id="search">
  <h2>站内搜索</h2>
  <div class="search-panel" data-search-root>
    <label class="search-label" for="site-search-input">搜索笔记</label>
    <input class="search-input" id="site-search-input" type="search" placeholder="标题、标签、正文" autocomplete="off" data-search-input>
    <div class="search-filters" data-search-filters hidden></div>
    <p class="search-status" data-search-status>输入关键词开始搜索。</p>
    <div class="search-results" data-search-results></div>
  </div>
</section>
""".strip()
```

- [ ] **Step 2: Render search panel on the homepage**

In `render_index`, place `{render_search_panel()}` between the hero and latest notes sections:

```python
return f"""
<section class="hero">
  <p class="eyebrow">{SITE_NAME}</p>
  <h1>个人知识笔记</h1>
  <p>{SITE_DESCRIPTION}<br><a href="mailto:{escape(SITE_EMAIL)}">{escape(SITE_EMAIL)}</a></p>
</section>

{render_search_panel()}

<section class="content-section">
  <h2>最新笔记</h2>
  <div class="note-list">{note_cards}</div>
</section>
...
""".strip()
```

- [ ] **Step 3: Add Pagefind tag filter attributes**

Change the tag helpers to accept a Pagefind filter mode:

```python
def tag_link(tag: str, base: str = "", pagefind_filter: bool = False) -> str:
    pagefind_attrs = ""
    if pagefind_filter:
        pagefind_attrs = (
            ' data-pagefind-filter="tag[data-pagefind-tag]"'
            f' data-pagefind-tag="{escape(tag, quote=True)}"'
        )
    return f'<a class="tag" href="{base}#tag-{tag_fragment(tag)}"{pagefind_attrs}>#{escape(tag)}</a>'


def render_tag_links(tags: tuple[str, ...], base: str = "", pagefind_filters: bool = False) -> str:
    return '<span class="tag-list">' + "".join(
        tag_link(tag, base, pagefind_filter=pagefind_filters) for tag in tags
    ) + "</span>"
```

- [ ] **Step 4: Add Pagefind note metadata**

In `render_note_page`, add metadata attributes and mark the rendered body:

```python
<p class="note-date" data-pagefind-meta="date">{note.date.isoformat()}</p>
<h1 data-pagefind-meta="title">{escape(note.title)}</h1>
<p data-pagefind-meta="summary">{escape(note.summary)}</p>
{render_tag_links(note.tags, "../index.html", pagefind_filters=True)}
...
<div class="prose" data-pagefind-body>
```

- [ ] **Step 5: Load the local search script**

In `templates/layout.html`, after the stylesheet link, add:

```html
    <script defer src="{{ asset_prefix }}assets/search.js"></script>
```

- [ ] **Step 6: Add template test for the script**

In `test_repository_template_links_favicon`, also assert:

```python
        self.assertTrue((root / "assets" / "search.js").exists())
        self.assertIn(
            '<script defer src="{{ asset_prefix }}assets/search.js"></script>',
            layout,
        )
```

- [ ] **Step 7: Run unit tests**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: PASS after Task 3 creates `assets/search.js`; until then the template test can fail on file existence.

---

### Task 3: Browser Search Asset and Styling

**Files:**
- Create: `assets/search.js`
- Modify: `assets/style.css`

**Interfaces:**
- Consumes: homepage elements with `data-search-root`, `data-search-input`, `data-search-status`, `data-search-filters`, and `data-search-results`.
- Consumes: Pagefind bundle at `site/pagefind/pagefind.js`.

- [ ] **Step 1: Create the search script**

Create `assets/search.js` with:

```javascript
(function () {
  const root = document.querySelector("[data-search-root]");
  if (!root) {
    return;
  }

  const input = root.querySelector("[data-search-input]");
  const filtersElement = root.querySelector("[data-search-filters]");
  const statusElement = root.querySelector("[data-search-status]");
  const resultsElement = root.querySelector("[data-search-results]");
  const scriptUrl = document.currentScript ? document.currentScript.src : window.location.href;
  const pagefindUrl = new URL("../pagefind/pagefind.js", scriptUrl).href;

  let pagefindPromise = null;
  let activeTag = "";
  let debounceTimer = 0;
  let requestId = 0;

  function setStatus(message) {
    statusElement.textContent = message;
  }

  function clearResults() {
    resultsElement.replaceChildren();
  }

  function textFromHtml(html) {
    const template = document.createElement("template");
    template.innerHTML = html || "";
    return template.content.textContent || "";
  }

  function createResultItem(data) {
    const article = document.createElement("article");
    article.className = "search-result";

    const title = document.createElement("h3");
    const link = document.createElement("a");
    link.href = data.url || "#";
    link.textContent = data.meta && data.meta.title ? data.meta.title : "未命名笔记";
    title.append(link);

    const excerpt = document.createElement("p");
    excerpt.textContent = textFromHtml(data.excerpt || data.meta && data.meta.summary || "");

    const meta = document.createElement("div");
    meta.className = "search-result-meta";
    const date = data.meta && data.meta.date ? data.meta.date : "";
    const tags = data.filters && data.filters.tag ? data.filters.tag : [];
    meta.textContent = [date, tags.map((tag) => "#" + tag).join(" ")].filter(Boolean).join(" · ");

    article.append(title, excerpt, meta);
    return article;
  }

  function renderResults(items, total) {
    clearResults();
    if (!items.length) {
      setStatus("没有找到相关笔记。");
      return;
    }

    const fragment = document.createDocumentFragment();
    items.forEach((item) => fragment.append(createResultItem(item)));
    resultsElement.append(fragment);
    setStatus("找到 " + total + " 条结果。");
  }

  async function loadPagefind() {
    if (!pagefindPromise) {
      pagefindPromise = import(pagefindUrl).then((pagefind) => {
        pagefind.init();
        return pagefind;
      });
    }
    return pagefindPromise;
  }

  function renderFilters(filters) {
    const tagCounts = filters.tag || {};
    const tags = Object.keys(tagCounts).sort((a, b) => a.localeCompare(b, "zh-CN"));
    if (!tags.length) {
      return;
    }

    const allButton = document.createElement("button");
    allButton.type = "button";
    allButton.className = "search-filter is-active";
    allButton.textContent = "全部";
    allButton.addEventListener("click", () => {
      activeTag = "";
      updateFilterButtons();
      runSearch();
    });
    filtersElement.append(allButton);

    tags.forEach((tag) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "search-filter";
      button.dataset.tag = tag;
      button.textContent = tag + " " + tagCounts[tag];
      button.addEventListener("click", () => {
        activeTag = activeTag === tag ? "" : tag;
        updateFilterButtons();
        runSearch();
      });
      filtersElement.append(button);
    });

    filtersElement.hidden = false;
  }

  function updateFilterButtons() {
    filtersElement.querySelectorAll(".search-filter").forEach((button) => {
      const isActive = (button.dataset.tag || "") === activeTag;
      button.classList.toggle("is-active", isActive);
    });
  }

  async function loadFilters() {
    try {
      const pagefind = await loadPagefind();
      const filters = await pagefind.filters();
      renderFilters(filters);
    } catch (error) {
      setStatus("搜索索引还没有生成。");
    }
  }

  async function runSearch() {
    const query = input.value.trim();
    const currentRequest = ++requestId;
    clearResults();

    if (!query) {
      setStatus("输入关键词开始搜索。");
      return;
    }

    setStatus("搜索中...");
    try {
      const pagefind = await loadPagefind();
      const options = activeTag ? { filters: { tag: activeTag } } : {};
      const search = await pagefind.search(query, options);
      const resultData = await Promise.all(search.results.slice(0, 12).map((result) => result.data()));
      if (currentRequest !== requestId) {
        return;
      }
      renderResults(resultData, search.results.length);
    } catch (error) {
      setStatus("搜索索引还没有生成。");
    }
  }

  input.addEventListener("focus", loadFilters, { once: true });
  input.addEventListener("input", () => {
    window.clearTimeout(debounceTimer);
    debounceTimer = window.setTimeout(runSearch, 180);
  });
})();
```

- [ ] **Step 2: Style the search UI**

Append focused styles to `assets/style.css` for `.search-panel`, `.search-input`, `.search-filters`, `.search-filter`, `.search-status`, and `.search-result`. Use the existing color variables and 8px radius style.

- [ ] **Step 3: Run unit tests**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: PASS.

---

### Task 4: Pagefind Build Pipeline and Verification

**Files:**
- Modify: `.github/workflows/pages.yml`
- Modify: `README.md`

**Interfaces:**
- Produces: deployed artifact containing `site/pagefind/`.

- [ ] **Step 1: Update GitHub Actions**

Add Node setup after Python setup:

```yaml
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: "22"
```

Add Pagefind after the site build:

```yaml
      - name: Build search index
        run: npx -y pagefind --site site
```

- [ ] **Step 2: Update README preview instructions**

Document:

```bash
python3 scripts/build.py
npx -y pagefind --site site
python3 -m http.server 8000 -d site
```

- [ ] **Step 3: Run local verification**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

Expected: tests pass and `site/` builds successfully.

- [ ] **Step 4: Run Pagefind when available**

Run:

```bash
npx -y pagefind --site site
```

Expected: `site/pagefind/pagefind.js` exists. If local network access blocks the command, GitHub Actions should still run it during deployment.
