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
    const summary = data.meta && data.meta.summary ? data.meta.summary : "";
    excerpt.textContent = textFromHtml(data.excerpt || summary);

    const meta = document.createElement("div");
    meta.className = "search-result-meta";
    const date = data.meta && data.meta.date ? data.meta.date : "";
    const tags = data.filters && data.filters.tag ? data.filters.tag : [];
    meta.textContent = [date, tags.map((tag) => "#" + tag).join(" ")]
      .filter(Boolean)
      .join(" · ");

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
      pagefindPromise = import(pagefindUrl).then(async (pagefind) => {
        await pagefind.init();
        return pagefind;
      });
    }
    return pagefindPromise;
  }

  function updateFilterButtons() {
    filtersElement.querySelectorAll(".search-filter").forEach((button) => {
      const isActive = (button.dataset.tag || "") === activeTag;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
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
    allButton.setAttribute("aria-pressed", "true");
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
      button.setAttribute("aria-pressed", "false");
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
      const resultData = await Promise.all(
        search.results.slice(0, 12).map((result) => result.data())
      );
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
