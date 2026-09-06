# 我的读书笔记

这是一个长期维护的个人阅读仓库：保留书目来源、结构化笔记、讨论记录，并把笔记构建成可公开访问的静态博客。

在线阅读：<https://100apps.github.io/my-reading-notes/>

## 当前内容

- 首批书单：20 本
- 深度报告：《有效的单元测试》
- 其余书目：结构化初读报告，后续随实际阅读持续修订
- 网站源码：`notes/`、`discussions/`、`data/books.json`
- GitHub Pages 成品：`docs/`

## 目录

```text
data/books.json        书目、状态与首页摘要
notes/                 每本书的 Markdown 笔记
discussions/           我和 AI 的讨论记录
sources/catalog.json   本地原文件的来源、格式、校验值
library/               本地电子书目录；默认不提交
docs/                  构建后的 GitHub Pages 静态站点
scripts/build.py       Markdown → HTML 构建器
scripts/new_book.py    新书脚手架
```

## 本地构建

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build.py
```

然后打开 `docs/index.html`。

## 新增一本书

```bash
.venv/bin/python scripts/new_book.py \
  --slug example-book \
  --title '书名' \
  --author '作者' \
  --category '分类'
```

填写生成的笔记和讨论文件，重新运行构建器，再提交和推送。

## 原文与版权

公开仓库不再分发仍受版权保护的 PDF、EPUB、MOBI、AZW3 或全文文本。`sources/catalog.json` 只记录本地文件名、格式、大小和 SHA-256，便于确认自己的合法副本；公版或具有明确再分发许可的材料，可以在核验许可证后单独加入。

笔记为个人学习记录，不替代购买或阅读原书。
