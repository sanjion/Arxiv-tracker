# Arxiv-tracker · arXiv 每日论文追踪器

[![Stars](https://img.shields.io/github/stars/colorfulandcjy0806/Arxiv-tracker?style=flat-square)](https://github.com/colorfulandcjy0806/Arxiv-tracker/stargazers)
[![CI](https://img.shields.io/github/actions/workflow/status/colorfulandcjy0806/Arxiv-tracker/digest.yml?label=Arxiv%20Digest&style=flat-square)](../../actions)
[![Pages](https://img.shields.io/badge/GitHub%20Pages-online-2ea44f?style=flat-square)](https://colorfulandcjy0806.github.io/Arxiv-tracker/)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square&logo=python)
![Last Commit](https://img.shields.io/github/last-commit/colorfulandcjy0806/Arxiv-tracker?style=flat-square)
![Open Issues](https://img.shields.io/github/issues/colorfulandcjy0806/Arxiv-tracker?style=flat-square)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg?style=flat-square)](./LICENSE)

> **如果你喜欢本项目，欢迎点亮一个 ⭐ Star 获取最新进展！**

**简体中文** | [English](./README_EN.md) 

---

## 😮 项目亮点（Highlights）

- 🔎 **多学科多主题检索**：支持 `cs.CV / cs.LG / cs.CL` 等分类，任意关键词 AND/OR 组合
- 🧠 **LLM 双语总结**：**英文一段 + 中文一段**，覆盖动机 / 方法 / 主要实验结果
- 🔗 **自动提取链接**：Abs / PDF / 代码仓库 / 项目页
- 📨 **邮件推送**：内置 QQ 邮箱（SSL/465），支持多收件人
- 🌐 **网页发布**：自动生成美观 HTML（GitHub Pages），历史归档与折叠/展开
- ⚙️ **易于扩展**：模块化代码，支持 GitHub Actions 与本地运行

**网页效果如下图：**
<img src="images/html.png" alt="Preview" width="720">

---

**邮件效果如下图：**
<img src="images/email.png" alt="Preview" width="720">

---

## 🧭 仓库结构

```
arxiv_tracker/        # 核心逻辑（客户端、解析、总结、站点、邮件等）
docs/                 # GitHub Pages 站点输出（自动生成）
outputs/              # 每次运行保存的 JSON/MD 等（可选）
.github/workflows/    # digest.yml 定时任务（每日 03:00 北京时间）
config.yaml           # 检索/摘要/邮件/站点配置
requirements.txt      # 运行依赖
```

---

## 🚀 快速开始（Fork & 部署）

### 1) Fork 本仓库

点击右上角 **Fork**，得到你自己的副本。

### 2) 配置 Secrets & Variables

> Settings → **Secrets and variables** → **Actions**

**Secrets（机密）**

- `DS_API_KEY`：LLM Key（如 DeepSeek的API，sk-xxxxx）
- `SMTP_PASS`：QQ 邮箱 **SMTP 授权码**（非登录密码）

**Variables（非机密，可用 Secrets 替代）**

- `EMAIL_TO`：收件人（多个用 `,` 或 `;` 分隔，比如xxx@qq.com）
- `EMAIL_SENDER`：发件人邮箱（通常与 SMTP 用户一致，比如xxx@qq.com）
- `SMTP_USER`：SMTP 用户名（通常 = 发件人邮箱，比如xxx@qq.com）

### 3) 启用 GitHub Pages

Settings → **Pages**：Source 选 **Deploy from a branch**；Branch 选 `main`，Folder 选 `/docs`。

### 4) 触发工作流

`.github/workflows/digest.yml` 已配置**每日北京时间 03:00**自动运行。也可在 **Actions** 中手动 **Run workflow**。

---

## ⚙️ 配置说明（`config.yaml`）

```yaml
categories: ["cs.CV", "cs.LG", "cs.CL"]
keywords:
  - "open vocabulary segmentation"
  - "referring segmentation"
  - "vision-language segmentation"
logic: "AND"
max_results: 10
sort_by: "submittedDate"
sort_order: "descending"

lang: "both"            # 生成英文+中文两段“总结”

summary:
  mode: "llm"           # 使用 LLM 生成总结
  scope: "both"

translate:
  enabled: true
  lang: "zh"
  fields: ["title", "summary"]

llm:
  base_url: "https://api.deepseek.com"
  model: "deepseek-chat"
  api_key_env: "DS_API_KEY"

email:
  enabled: true
  smtp_server: "smtp.qq.com"
  smtp_port: 465
  tls: "ssl"
  debug: false
  detail: "full"
  max_items: 20
  attach_md: false
  attach_pdf: false

site:
  enabled: true
  dir: "docs"
  title: "arXiv 论文速递"
  keep_runs: 1024
  theme: "light"
  accent: "#2563eb"
```

> 工作流会把 `--site-url` 自动传入，不必在 `config.yaml` 写死站点 URL。

---

## 🛠️ 本地运行（可选）

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

export DS_API_KEY="你的LLM密钥"
export EMAIL_TO="your@qq.com"
export EMAIL_SENDER="your@qq.com"
export SMTP_USER="your@qq.com"
export SMTP_PASS="你的QQ SMTP授权码"

python -m arxiv_tracker.cli run   --config config.yaml   --site-dir docs   --verbose
```

---

## 📨 邮件与防重复

- SMTP：`smtp.qq.com:465 + SSL`（或 `587 + STARTTLS`）
- 多收件人：`,` 或 `;` 分隔
- 防重复策略：
  - Workflow 重试仅**首轮**发送（后续传 `--no-email`）
  - 代码中有**幂等标记**（同一快照只发一次）

---

## 🧩 页面特性

- 亮色主题，响应式布局
- 卡片信息：标题、作者、时间、Comments/会议、链接区（Abs/PDF/Code/Project）
- **Summary / 总结**：**英文一段 + 中文一段**（LLM 输出）
- Abstract 与中文标题/摘要为折叠块；首页支持历史归档

---

## ❓ 常见问题（FAQ）

- **没收到邮件？** 检查 Actions 日志中的“Show email env (masked)”是否全部注入成功；确认 TLS/端口组合正确；QQ 开启 POP3/SMTP 并使用**授权码**。
- **总结只有一句话？** 日志若显示 `[Run] summary   : heuristic/both`，说明 LLM 未启用或密钥未注入。确认 `summary.mode: llm` 且 `DS_API_KEY` 存在，且不要用 CLI 参数覆盖为 heuristic。

---

## 🗺️ Roadmap

- [ ] 支持更多LLM，下一步考虑硅基流动的API
- [ ] 更多站点主题（暗色、跟随系统）
- [ ] 自定义卡片字段开关与顺序



**欢迎 PR 与 Issue！**

---

## ✨ Star History

[![Star History](https://api.star-history.com/svg?repos=colorfulandcjy0806/Arxiv-tracker&type=Date)](https://star-history.com/#colorfulandcjy0806/Arxiv-tracker&Date)


---

## 🤝 Community contributors

<a href="https://github.com/colorfulandcjy0806/Arxiv-tracker/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=colorfulandcjy0806/Arxiv-tracker" alt="Contributors"/>
</a>

## 🔒 License

本项目基于 **MIT 协议** 开源，详见 [LICENSE](./LICENSE)。


帮我翻译成英文版本的readme 给我直接可以下载的
