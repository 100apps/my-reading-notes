# 我的读书笔记

这是一个长期维护的个人阅读仓库：保留书目来源、结构化笔记、讨论记录，并把笔记构建成可公开访问的静态博客。

在线阅读：<https://100apps.github.io/my-reading-notes/>

## 当前内容

- 收录书目：21 本
- 深度报告：《有效的单元测试》《幸福之路》
- 其余书目：结构化初读报告，后续随实际阅读持续修订
- 网站源码：`notes/`、`discussions/`、`data/books.json`
- GitHub Pages 成品：`docs/`

## 目录

```text
data/books.json        书目、状态与首页摘要
notes/                 每本书的 Markdown 笔记
discussions/           我和 AI 的讨论记录
sources/catalog.json   本地原文件的来源、格式、校验值
sources/public-domain/ 核验为公版或可再分发的原文
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

## 共用阅读布局

所有书页、讨论记录和来源页使用 `scripts/build.py` 中的同一套阅读模板，样式与交互统一放在 `docs/assets/`。新增书目后运行构建器即可使用同样的布局。

- 页头参与正常滚动；屏幕宽度达到 1024px 时，目录在左侧独立列内吸顶。
- 手机、平板和分屏窗口使用页内折叠目录，展开会向下推开正文；每个主要章节提供返回目录入口。
- 正文字号可在 16–24px 间调整，字号与深浅主题保存到当前设备；没有本地存储权限也可以阅读。
- 表格和代码块在各自区域内横向滚动，长链接与图片适应正文宽度。
- 目录在构建时生成，不依赖 JavaScript；支持键盘跳到正文、章节焦点、减少动画偏好与打印样式。
- CSS 和 JavaScript 链接包含内容校验版本，发布后的页面会获取匹配的新资源。

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

《幸福之路》的英文原著来自 Project Gutenberg，标注为美国公版，因而同时保存 TXT 与 EPUB；仓库不收录现代中文译本。不同司法辖区的版权期限可能不同，使用者仍应核对当地法律。

笔记为个人学习记录，不替代购买或阅读原书。
