# 添加论文 项目与活动

三个主页面的数据来自 pages 子文件夹。不要手动修改 content-index.js。

| 文件夹 | 自动归入 |
| --- | --- |
| pages/publications/ | Publications |
| pages/activities/ | Activities |
| pages/projects/ | Projects |

每条记录是一个 UTF-8 Markdown 文件，文件名必须唯一（同目录），可使用日期加英文短名。允许嵌套文件夹。文件头是 YAML，下面是 Markdown 正文。复制已有的 ICOMOS 文件修改即可。

```yaml
---
title: "Your title"
subtitle: ""
date: 2026-10-21
authors: [Wei Feng, Xiao Wang, Peng Tang]
pub_type: Conference Paper
source: "Conference or institution"
keywords: [Built Heritage]
image: "https://example.com/cover.png"
tags: [Built Heritage]
external_url:
navs: []
draft: false
---

### Overview

正文、图片、链接和列表写在这里。
```

- title 或 name 必填；不填 date 时从 YYYY-MM-DD 文件名前缀读取。date 推荐填写 YYYY-MM-DD，决定年份分组和倒序排列。没有日期会显示 Undated。
- authors、tags、keywords 使用数组。pub_type 也可用于活动和项目分类，例如 Workshop / Research Project。
- image 为封面。缺省时使用纯文字列表；可用根目录相对路径，如 photos/example.png。
- external_url 是详情页中的外部链接，列表标题仍打开本地详情。
- draft: true 或 navs: [template] 会跳过该文件。文件名以 _ 或 . 开头也会跳过，可用于保存模板。
- 空字段不会显示，不必删除。不要在这个静态站点中粘贴 Liquid 循环。

## 本地自动更新

只需要 Python 3，无需安装 PyYAML 或其他依赖。在仓库目录运行：

```powershell
python scripts/build_content.py --watch
```

保持终端运行，新增或修改文件后会自动刷新索引。浏览器刷新页面即可看到结果。单次生成可省略 --watch。生成的脚本数据也支持直接打开 HTML，不依赖 fetch 读取本地文件。

YAML 文件头支持本项目使用的扁平字段、`[a, b]` 数组、单双引号、空值以及 `true/false`。暂不支持缩进嵌套的 YAML 对象；复杂内容请写在 `---` 后面的 Markdown 正文中。

## GitHub

本次仅创建本地配置，没有推送或开启 Pages。推送后，GitHub Actions 的 Update content index 工作流会扫描三个文件夹并提交新索引，需要仓库允许 Actions 写入内容。它只生成内容，不公开网站。正式上线时还需要配置 Pages 发布流程。

详情使用 content.html?id=publications%2F文件名，三个列表页不需要逐条修改。
