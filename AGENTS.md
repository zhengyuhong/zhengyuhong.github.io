# 仓库指南

## 项目结构与模块组织

这个仓库是 `zhengyuhong.cn` 的 Markdown 笔记站点。源笔记放在 `notes/`，文件名使用 `YYYY-MM-DD-title.md`。共享模板在 `templates/layout.html`，样式在 `assets/style.css`，生成脚本在 `scripts/build.py`，测试在 `tests/`。`site/` 是生成产物，不要手动编辑。

## 构建、测试与开发命令

- `pip install -r requirements.txt` - 安装 Markdown 和 YAML 解析依赖。
- `python3 scripts/build.py` - 将静态网站生成到 `site/`。
- `python3 -m http.server 8000 -d site` - 在 `http://localhost:8000/` 预览生成结果。
- `python3 -m unittest discover -s tests -v` - 运行生成器测试。

## 编码风格与命名约定

Python 使用 4 空格缩进，HTML/CSS 使用 2 空格缩进。Python 函数应保持短小、确定、易测试。笔记文件名使用小写英文和连字符，例如 `2026-07-21-reading-notes.md`。front matter 字段固定为 `title`、`date`、`tags`、`summary`。

## 测试指南

修改解析、渲染、URL、资源复制或发布假设时，同步更新 `tests/test_build.py`。提交前运行完整 unittest 命令。视觉改动需要本地构建，并检查首页和至少一个笔记页。

## 提交与 Pull Request 规范

提交信息使用简短的祈使句，沿用现有风格，例如 `Create CNAME`、`Add notes site generator`。Pull Request 需要说明面向读者的网站变化、发布流程变化；涉及视觉更新时附截图。

## 安全与配置提示

不要提交密钥、令牌、统计服务凭据或私人草稿。`CNAME` 必须保留在仓库根目录，并确保构建时复制到 `site/`。

## AI Agent 论文图解发布规则

这些规则适用于 Codex、opencode、Claude Code、Cursor 等 AI Agent 在本仓库中生成或发布论文图解笔记。

### 使用 paper-comic 时的默认要求

- 当用户要求使用 `paper-comic` 或 `/Users/zhengyuhong/.codex/skills/paper-comic/SKILL.md` 时，先读取该 skill，并保留其“先读论文、推荐图解方案、等待用户确认范围/张数/语言/风格”的确认门。
- 本仓库的默认输出语言是中文。正文、图注、图上标注、总结和解释都优先写中文；论文原题、模型名、方法名、公式、变量和专有名词按原文保留。
- 默认视觉风格是 `sketchnote`，用途填写为“论文阅读笔记”。除非用户明确要求其他风格，否则不要改成 `paper-figure`。
- 图解要尽量充分：在 `paper-comic` 允许的 1-10 页范围内，优先推荐能讲清方法流程、核心机制和关键结果的多图组合，不要只给一张概念封面图。推荐页数应随论文复杂度说明原因。
- 每张图都要服务理解：图上必须有清晰流程、关键箭头、模块名、必要维度/公式/例子和短标注，避免只做装饰图。

### 转成本站 Markdown 笔记

- 最终产物必须发布为 `notes/YYYY-MM-DD-<paper-title-slug>.md`，不要只把结果留在 `papers/`、`output/`、`downloads/` 或 `tmp/`。文件名必须使用日期 + 论文标题 slug：英文论文标题转为小写 kebab-case，去掉标点；中文论文标题转为无声调拼音 kebab-case。不要用泛化主题、随意缩写或 `illustrated` 替代论文标题；只有标题过长时，才可保留论文主标题并省略副标题。
- Markdown front matter 必须包含 `title`、`date`、`tags`、`summary`。`date` 与文件名前缀保持一致；`tags` 至少包含 `论文`、`论文图解`、`sketchnote`，并按论文主题补充 2-5 个标签。
- 发布标题必须对齐论文标题：front matter `title` 和正文 H1 默认使用论文原题，不要改写成泛化中文标题，也不要追加“图解笔记”“深度解读”等后缀。需要强调图解属性时，用副标题、导语、摘要或标签表达，而不是替换论文原题。
- 正文结构建议包含：论文链接、作者/会议或年份（如果可确认）、一句话总结、每张图的章节、图下中文讲解、最后 3 个核心要点。
- 生成图片放到 `assets/images/<note-slug>/`，Markdown 中使用 `../assets/images/<note-slug>/<file>.png` 引用。不要引用本机绝对路径。
- 如果 `paper-comic` 已在其他目录生成图片或草稿，需要把可发布的 Markdown 和图片整理到 `notes/` 与 `assets/images/` 后再构建。

### 发布与校验

- 不要手动编辑 `site/`；运行 `python3 scripts/build.py` 生成站点。
- 发布前运行 `python3 -m unittest discover -s tests -v`。如果修改了样式、模板或图片引用，还要本地构建并检查首页和至少一个笔记页。
- 发布论文笔记时应在 `main` 分支提交并推送到远端 `main`。推送前先运行 `git status --short`，只提交本次论文笔记相关的 `notes/`、`assets/images/` 和必要规则/模板改动，避免带上临时文件或用户未确认的改动。
- 如果当前分支不是 `main`，或工作区已有无关改动，先向用户说明并等待确认，不要擅自覆盖、回滚或混入无关文件。
