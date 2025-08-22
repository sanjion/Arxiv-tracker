# Arxiv-tracker · Daily arXiv Paper Tracker

[![Stars](https://img.shields.io/github/stars/colorfulandcjy0806/Arxiv-tracker?style=flat-square)](https://github.com/colorfulandcjy0806/Arxiv-tracker/stargazers)
[![CI](https://img.shields.io/github/actions/workflow/status/colorfulandcjy0806/Arxiv-tracker/digest.yml?label=Arxiv%20Digest&style=flat-square)](../../actions)
[![Pages](https://img.shields.io/badge/GitHub%20Pages-online-2ea44f?style=flat-square)](https://colorfulandcjy0806.github.io/Arxiv-tracker/)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square&logo=python)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg?style=flat-square)](./LICENSE)

**English | [简体中文](./README_CN.md)**

> **If you like this project, please give us a star ⭐ for the latest updates!**


---

## 😮 Highlights

- 🔎 **Multi-field & multi-topic** arXiv search (e.g., `cs.CV / cs.LG / cs.CL`) with flexible AND/OR keyword logic
- 🧠 **LLM bilingual digest**: **one English paragraph + one Chinese paragraph** (motivation, method, key results)
- 🔗 **Link extraction**: Abs / PDF / code repos / project pages
- 📨 **Email delivery**: built-in QQ SMTP (SSL/465), multiple recipients
- 🌐 **Web publishing**: pretty HTML via GitHub Pages with history archive & collapsible sections
- 🛡️ **Robustness**: retry, idempotent email flag, `--no-email` for retries, concurrency guard
- ⚙️ **Extensible**: modular code, works with GitHub Actions and locally

---

## 🧭 What’s inside

```
arxiv_tracker/        # core logic (client, parsing, LLM digest, site, email)
docs/                 # GitHub Pages site output (auto-generated)
outputs/              # saved JSON/MD snapshots (optional)
.github/workflows/    # digest.yml (runs daily at 03:00 Beijing time)
config.yaml           # search/summary/email/site configuration
requirements.txt      # dependencies
```

---

## 🚀 Quick Start (Fork & Deploy)

### 1) Fork the repo

Click **Fork** to create your copy.

### 2) Configure Secrets & Variables

Go to Settings → **Secrets and variables** → **Actions**

**Secrets**

- `DS_API_KEY`: your LLM key (e.g., DeepSeek)
- `SMTP_PASS`: QQ Mail **SMTP authorization code** (not your login password)

**Variables** (or also as Secrets)

- `EMAIL_TO`: recipients (comma/semicolon separated)
- `EMAIL_SENDER`: sender email (usually same as SMTP user)
- `SMTP_USER`: SMTP username (usually = sender email)

### 3) Enable GitHub Pages

Settings → **Pages**: Source = **Deploy from a branch**, Branch = `main`, Folder = `/docs`.

### 4) Run the workflow

The workflow `.github/workflows/digest.yml` runs **daily 03:00 Beijing (19:00 UTC)**. You can also run it manually from the **Actions** tab.

---

## ⚙️ Configuration (`config.yaml`)

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

lang: "both"            # bilingual digest (English + Chinese)

summary:
  mode: "llm"           # LLM-generated digest
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
  title: "arXiv Daily Digest"
  keep_runs: 1024
  theme: "light"
  accent: "#2563eb"
```

> The workflow passes `--site-url` automatically; no need to hardcode it in `config.yaml`.

---

## 🛠️ Run locally (optional)

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

export DS_API_KEY="your-LLM-key"
export EMAIL_TO="your@qq.com"
export EMAIL_SENDER="your@qq.com"
export SMTP_USER="your@qq.com"
export SMTP_PASS="your-qq-smtp-auth-code"

python -m arxiv_tracker.cli run   --config config.yaml   --site-dir docs   --verbose
```

---

## 📨 Email & Duplicates

- SMTP: `smtp.qq.com:465 + SSL` (or `587 + STARTTLS`)
- Multiple recipients supported
- Duplicate-safety:
  - Only the **first attempt** sends an email (`--no-email` for retries)
  - **Idempotent flag** avoids re-sending for the same snapshot

---

## 🧩 Page features

- Light theme, responsive layout
- Card info: title, authors, times, comments/venue, links (Abs/PDF/Code/Project)
- **Summary**: **English + Chinese** (LLM output)
- Abstract & Chinese title/abstract as collapsible sections; historical archive on homepage

---

## ❓ FAQ

- **No email received?** Check the “Show email env (masked)” output in Actions; make sure all variables are present and TLS/port combo matches; enable QQ POP3/SMTP and use the **authorization code**.
- **Heuristic instead of LLM?** Ensure the log shows `[Run] summary   : llm/both` and `DS_API_KEY` is injected; avoid overriding with CLI flags.
- **Double emails?** Avoid concurrent runs; rely on `--no-email` + idempotent flag to prevent duplicates.

---

## 🗺️ Roadmap

- [ ] More themes (dark/system)
- [ ] Toggle/order for card fields
- [ ] Multiple jobs for different topic subscriptions
- [ ] Site search & filters
- [ ] Slack / Telegram push
- [ ] Auto-collect code links from PDFs

Contributions welcome!

---

## ✨ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=colorfulandcjy0806/Arxiv-tracker&type=Date)](https://star-history.com/#colorfulandcjy0806/Arxiv-tracker&Date)

---

## 🔒 License

This project is released under the **MIT License** — see [LICENSE](./LICENSE).
