# zhengyuhong.cn

这个仓库保存 `zhengyuhong.cn` 的 Markdown 笔记源文件和静态站点生成脚本。

## 写一篇笔记

在 `notes/` 目录下创建带日期前缀的 Markdown 文件：

```text
notes/2026-07-21-some-topic.md
```

每篇笔记用 YAML front matter 描述标题、日期、标签和摘要：

```md
---
title: 某个主题
date: 2026-07-21
tags: [笔记, Codex]
summary: 用一句话概括这篇笔记。
---
```

## 本地预览

```bash
pip install -r requirements.txt
python3 scripts/build.py
python3 -m http.server 8000 -d site
```

打开 `http://localhost:8000/` 查看生成后的网站。

## 运行测试

```bash
python3 -m unittest discover -s tests -v
```

## 发布网站

推送到 `master` 或 `main` 后，GitHub Actions 会构建 `site/` 并部署到 GitHub Pages。仓库设置里的 Pages Source 需要选择 GitHub Actions。
