<p align="center">
  <img src="assets/wechat-article-studio-banner.png" alt="WeChat Article Studio 品牌横幅" width="100%">
</p>

# WeChat Article Studio

> 面向微信公众号长文的本地编辑工作流：把事实控制、中文编辑、内容型排版、图片处理、严格 HTML 审计和微信交付检查放在同一条可复现流水线上。

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/License-MIT-2f855a)](LICENSE)
[![CI](https://github.com/LostSirius/wechat-article-studio-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/LostSirius/wechat-article-studio-skill/actions/workflows/ci.yml)
[![Three themes](https://img.shields.io/badge/Themes-academy%20%7C%20editorial%20%7C%20minimal-c4a06a)](guides/layout.md)

[GitHub](https://github.com/LostSirius/wechat-article-studio-skill) · [English](README_EN.md) · [架构](docs/ARCHITECTURE.md) · [微信兼容边界](docs/WECHAT-COMPATIBILITY.md) · [评测方法](docs/BENCHMARK.md)

## 定位

它不是“给 Markdown 换一套颜色”的模板仓库。Skill 先要求建立事实证据、识别目标账号的语气和信息结构，再选择有限的内容组件；脚本负责确定性渲染、图片标准化、GIF 合成和严格兼容审计。

适合：校园新闻、活动纪实、人物稿、访谈、品牌长文和已审稿件的格式化。它不会自动发布，也不会绕过微信编辑器的最终检查。

## 为什么不是又一个换色模板

- **事实先于文风**：先处理来源冲突、引语和不确定项，再做低 AI 痕迹编辑。
- **组件服从内容**：时间线、引语、表格、信息卡只在提升理解时出现。
- **写作与呈现分离**：UTF-8 JSON manuscript 是唯一内容输入，renderer 转成保守的内联样式 HTML。
- **真实交付边界**：浏览器里好看不等于微信里可发布；外链图片仍需进入微信素材库。
- **可复现测试**：公开仓库只含匿名合成夹具，Windows、Ubuntu 与 macOS 运行同一套回归。

## 核心能力

1. 证据账本、事实冲突处理和账号语气指纹。
2. 中文低 AI 痕迹编辑，但不把启发式命中当作作者身份判断。
3. `academy`、`editorial`、`minimal` 三套内容型主题。
4. 严格标签、属性和 CSS 白名单；预览脚本与干净正文分离。
5. EXIF 校正、sRGB ICC、JPEG 4:4:4、尺寸限制与非破坏性图片导出。
6. 基于焦点坐标的 cover/contain GIF 幻灯片。
7. 375/414 px 浏览器截图（本机有 Chrome/Edge 时）和结构化构建报告。
8. 仓库卫生扫描，阻止本地路径、实验目录、临时 URL 和常见秘密进入提交。

## 工作流

```mermaid
flowchart LR
    A[资料与已审稿件] --> B[证据账本]
    B --> C[语气与结构计划]
    C --> D[manuscript.json]
    D --> E[render.py]
    E --> F[严格正文 fragment]
    E --> G[浏览器 preview]
    F --> H[audit.py]
    H --> I[微信编辑器粘贴]
    I --> J[素材库 / mmbiz CDN]
    J --> K[手机预览]
```

## 3 分钟安装

先安装 Python 3.10+，再 clone 本仓库：

```bash
git clone https://github.com/LostSirius/wechat-article-studio-skill.git
```

本命令不依赖 GitHub Release；随后按系统执行：

### Windows PowerShell

```powershell
cd wechat-article-studio-skill
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe scripts/self_test.py --with-slideshow
```

### macOS / Linux

```bash
cd wechat-article-studio-skill
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python scripts/self_test.py --with-slideshow
```

路径示例统一使用 `/`；Python 与 PowerShell 都能正确处理。

## 安装为 Cursor Skill

仓库根目录保留 `SKILL.md`，复制后无需再套一层目录。

### 项目级

PowerShell：

```powershell
New-Item -ItemType Directory -Force .cursor/skills | Out-Null
Copy-Item -Recurse -Force wechat-article-studio-skill .cursor/skills/wechat-article-studio
```

跨平台：

```bash
mkdir -p .cursor/skills
cp -R wechat-article-studio-skill .cursor/skills/wechat-article-studio
```

### 个人级

PowerShell：

```powershell
New-Item -ItemType Directory -Force "$HOME/.cursor/skills" | Out-Null
Copy-Item -Recurse -Force wechat-article-studio-skill "$HOME/.cursor/skills/wechat-article-studio"
```

跨平台：

```bash
mkdir -p "$HOME/.cursor/skills"
cp -R wechat-article-studio-skill "$HOME/.cursor/skills/wechat-article-studio"
```

### Claude Code、Codex 等

六份指南是普通 Markdown，`scripts/` 提供七个标准 Python CLI，另有一个版本模块，因此可被其他支持自定义指令或脚本调用的代理使用；但不同产品的 Skill 自动发现路径、触发语义、工具权限和上下文加载方式并不相同。本项目只验证 Cursor 目录约定和本地 Python 脚本，不声称对其他代理提供原生或完全等价兼容。

## 快速开始

PowerShell：

```powershell
python scripts/build.py examples/manuscript.json --output-dir output --no-screenshots
python scripts/audit.py output/article.fragment.html --manuscript examples/manuscript.json
```

跨平台：

```bash
python3 scripts/build.py examples/manuscript.json --output-dir output --no-screenshots
python3 scripts/audit.py output/article.fragment.html --manuscript examples/manuscript.json
```

如需在复制时把本地图片路径替换为已批准的 HTTPS 地址，可增加
`--cdn-map cdn_map.json`。这只替换 URL，不会自动上传图片到微信。

输入是结构化 JSON：

```json
{
  "theme": "academy",
  "title": "一篇虚构开放日稿件",
  "sections": [
    {
      "title": "从事实开始",
      "blocks": [{"type": "p", "text": "先核验，再编辑。"}]
    }
  ]
}
```

输出目录包含：

- `article.fragment.html`：只含文章根节点，可复制正文。
- `article.preview.html`：浏览器预览与复制按钮。
- `article.render-report.json`：结构与图片交付状态。
- `audit.json`：兼容性和编辑启发式报告。
- `build-report.json`：构建路径与截图状态。
- `mobile-375.png`、`mobile-414.png`：仅在浏览器可用且未禁用截图时生成。

## 三套主题

- `academy`：大学、机构新闻、学习项目和时间线纪实。
- `editorial`：人物、访谈、品牌故事和长篇特写。
- `minimal`：图片主导或已经审定、只需克制格式化的稿件。

三套主题共享保守 HTML 合同，不是同一模板的颜色替换。详见
[guides/layout.md](guides/layout.md)。

## 脚本命令

```text
python scripts/build.py MANUSCRIPT --output-dir output [--cdn-map MAP] [--no-screenshots]
python scripts/render.py MANUSCRIPT --output-dir output [--cdn-map MAP]
python scripts/audit.py FRAGMENT --manuscript MANUSCRIPT [--json]
python scripts/prepare_images.py INPUT_DIR OUTPUT_DIR
python scripts/slideshow.py MANIFEST [--force]
python scripts/self_test.py --with-slideshow
python scripts/hygiene.py . --json
```

图片导出会保留 sRGB ICC，并以 `subsampling=0` 输出 JPEG 4:4:4；自测会直接断言这两个行为。

## 微信的真实限制

- 微信编辑器可能过滤标签、属性和 CSS；本项目采用的严格配置是保守基线，不是官方规范。
- **复制按钮复制的是 HTML 排版和图片 URL，不会复制本地 JPG、PNG、GIF 文件。**
- `file://`、相对路径、`blob:` 或 `data:` 图片即使在桌面预览可见，也不能据此认为可以粘贴到微信；新预览页会在发现此类未解析图片时禁用复制。
- 普通 HTTPS 图片可能暂时粘贴成功，但仍需在微信编辑器内转存/重传。
- 发布前仍需：解决本地图片 → 复制排版 → 粘贴微信编辑器 → 转存/重传非微信图片 → 确认最终图片来自 `mmbiz.qpic.cn` 或官方素材库 → 手机预览。
- GIF 仍受文件体积、256 色和编辑器上传限制。
- 静态兼容分 100 只表示当前审计规则全部通过，**不等于微信官方认证**。

## 实验数据与边界

公开回归包含 3 个匿名合成稿件，覆盖三套主题、事实卡、日期、段落、引语、callout 和四列以内表格；另含非法 HTML 拒绝、ICC/4:4:4 图片导出、双帧 GIF 和仓库卫生测试。

2026-08-31 在全新 Python 3.12 虚拟环境中的公开基线：3/3 fixture 均为 `strict_compatibility=100`、`editorial_heuristic=100`、0 fatal、0 warning；非法 HTML 被拒绝；1200×600 测试 JPEG 含 sRGB ICC 且为 4:4:4；540×720 双帧 GIF 通过；卫生扫描 0 命中。

这些是静态和工程回归，不是审美排行榜。项目目前不能声称 SOTA；详见 [docs/BENCHMARK.md](docs/BENCHMARK.md)。

## 目录

```text
.
├── SKILL.md
├── guides/                     # 编辑、排版、图片、质量与研究方法
├── scripts/                    # 7 个 CLI + 1 个版本模块
├── evals/                      # 3 个匿名合成夹具
├── examples/manuscript.json
├── assets/                     # 1600×450 横幅与 512×512 图标
├── docs/                       # 架构、兼容性、评测与法律说明
└── .github/                    # CI、贡献、安全、Issue 与 PR 模板
```

## 路线图

- 增加经过许可的匿名微信编辑器粘贴回归记录。
- 扩展暗色模式与更多移动端字体测试。
- 发布可复用但不绑定品牌的 manuscript schema。
- 建立盲评协议，在有真实比较数据前不做 SOTA 声称。

## 贡献

请先阅读 [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md) 和
[.github/SECURITY.md](.github/SECURITY.md)。公开 issue、PR 和 fixture 不得包含真实姓名、未授权文章、照片、二维码、账号后台信息、本地绝对路径或访问令牌。

当前维护者与代码所有者：[LostSirius](https://github.com/LostSirius)。

## 来源与致谢

本项目独立实现。思想层面的公开参考包括
[gzh-design-skill](https://github.com/isjiamu/gzh-design-skill)、
[wechat-styler](https://github.com/zjp1997720/wechat-styler)、
[wechat-article-skills](https://github.com/dengqikuang/wechat-article-skills)、
[xiaohu-wechat-format](https://github.com/xiaohuailabs/xiaohu-wechat-format)、
[md2wechat-skill](https://github.com/geekjourneyx/md2wechat-skill)、
[min-skill](https://github.com/limin112/min-skill)、
[lieflat-less-ai-tone](https://github.com/larashero3-dotcom/lieflat-less-ai-tone) 和
[de-aigc-ch](https://github.com/hongcha1101/de-aigc-ch)。
许可证边界见 [NOTICE.md](NOTICE.md)，运行时依赖见
[docs/legal/THIRD_PARTY_NOTICES.md](docs/legal/THIRD_PARTY_NOTICES.md)，品牌图授权见
[docs/legal/ASSETS-LICENSE.md](docs/legal/ASSETS-LICENSE.md)。

## 许可证与非官方声明

独立实现部分以 [MIT License](LICENSE) 发布。本项目与腾讯、微信及上述参考项目均无隶属或背书关系；品牌视觉不含微信官方 Logo，也不暗示官方认可。
