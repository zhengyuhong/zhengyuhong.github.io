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
