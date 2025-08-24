# Arxiv-tracker · arXiv Daily Paper Tracker

[![Stars](https://img.shields.io/github/stars/colorfulandcjy0806/Arxiv-tracker?style=flat-square)](https://github.com/colorfulandcjy0806/Arxiv-tracker/stargazers)
[![CI](https://img.shields.io/github/actions/workflow/status/colorfulandcjy0806/Arxiv-tracker/digest.yml?label=Arxiv%20Digest&style=flat-square)](https://github.com/colorfulandcjy0806/Arxiv-tracker/actions)
[![Pages](https://img.shields.io/badge/GitHub%20Pages-online-2ea44f?style=flat-square)](https://colorfulandcjy0806.github.io/Arxiv-tracker/)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square&logo=python)
![Last Commit](https://img.shields.io/github/last-commit/colorfulandcjy0806/Arxiv-tracker?style=flat-square)
![Open Issues](https://img.shields.io/github/issues/colorfulandcjy0806/Arxiv-tracker?style=flat-square)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg?style=flat-square)](./LICENSE)

> If you like this project, please give it a **⭐ Star** to get the latest updates!

**[简体中文](./README.md) | English**

---

## 😮 Highlights

- 🔎 **Multi-field & multi-topic search**: supports categories like `cs.CV / cs.LG / cs.CL`, with keyword combinations using AND/OR.
- 🧠 **LLM bilingual summary**: **one English paragraph + one Chinese paragraph**, covering motivation / method / key results.
- 🔗 **Automatic link extraction**: Abs / PDF / code repos / project pages (venue inferred from comments/journal_ref if available).
- 📨 **Email delivery**: built-in QQ Mail (SSL/465), supports multiple recipients.
- 🌐 **Web publishing**: auto-generated HTML via GitHub Pages, with archive & collapsible sections.
- ⚙️ **Extensible**: modular codebase; supports GitHub Actions and local runs.

**Web preview:**

<p align="center">
  <img src="images/html.png" alt="Web Preview" width="720">
</p>



---

**Email preview:**

<p align="center">
  <img src="images/email.png" alt="Email Preview" width="720">
</p>



---

## 🧭 Repository Structure

```
arxiv_tracker/        # Core logic (client, parser, summarizer, site generator, mailer, etc.)
docs/                 # GitHub Pages output (auto-generated)
outputs/              # JSON/MD snapshots per run (optional)
.github/workflows/    # digest.yml schedule (03:00 Beijing time daily)
config.yaml           # Search/summary/email/site configuration
requirements.txt      # Dependencies
```

---

## 🚀 Quick Start (Fork & Deploy)

### 1) Fork this repository

Click **Fork** (top-right) to create your copy.

### 2) Configure Secrets & Variables

> Settings → **Secrets and variables** → **Actions**

**Secrets (confidential)**

- `DS_API_KEY`: LLM key (e.g., DeepSeek API, `sk-xxxxx`)
- `SMTP_PASS`: QQ Mail **SMTP authorization code** (NOT the login password)

**Variables (non-confidential; you may also use Secrets)**

- `EMAIL_TO`: recipients (`,` or `;` separated, e.g., `a@qq.com;b@xx.com`)
- `EMAIL_SENDER`: sender address (usually same as SMTP user, e.g., `a@qq.com`)
- `SMTP_USER`: SMTP username (usually equals sender)

> ⚠️ **Never commit API keys or SMTP codes to the repo.** Keep them in **Actions → Secrets** only.

### 3) Enable GitHub Pages

Settings → **Pages**: Source = **Deploy from a branch**; Branch = `main`, Folder = `/docs`.

### 4) Trigger the workflow

`.github/workflows/digest.yml` runs **daily at 03:00 Beijing time**. You can also run it manually in **Actions → Run workflow**.

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

lang: "both"            # Generate English + Chinese summary

summary:
  mode: "llm"           # Use LLM
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

> The workflow passes `--site-url` automatically, so you don’t need to hardcode the Pages URL in `config.yaml`.

---

## 🛠️ Run Locally (optional)

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

## 📨 Email & De-duplication

- SMTP: `smtp.qq.com:465 + SSL` (or `587 + STARTTLS`)
- Multiple recipients: separate with `,` or `;`
- De-dup:
  - Workflow retries: only the **first attempt** sends email (`--no-email` for subsequent attempts)
  - CLI: idempotency guard to avoid duplicate sends for the same snapshot

---

## 🧩 Site Features

- Light theme, responsive layout
- Cards: title, authors, timestamps (first/latest), comments/venue, links (Abs/PDF/Code/Project)
- **Summary**: **one English paragraph + one Chinese paragraph** (LLM output)
- Collapsible Abstract and CN title/summary; home shows latest digest with archives

---

## ❓ FAQ

- **No email received?** Check “Show email env (masked)” in Actions logs for injected variables; verify TLS/port; ensure QQ Mail SMTP/POP3 enabled and use the **authorization code**.
- **Summary looks like only the first sentence?** If logs show `[Run] summary   : heuristic/both`, LLM wasn’t enabled or API key missing. Ensure `summary.mode: llm` and `DS_API_KEY` exists; don’t override with CLI flags forcing heuristic.

---

## 🗺️ Roadmap

- [ ] Address the issue of retrieving the same literature every day
- [ ] The bug that sends 2 emails every time
- [ ] More LLM backends (OpenAI-compatible providers)
- [ ] More site themes (dark, system)
- [ ] Per-card field toggles & ordering

**PRs and Issues are welcome!**

---

## ✨ Star History

[![Star History](https://api.star-history.com/svg?repos=colorfulandcjy0806/Arxiv-tracker&type=Date)](https://star-history.com/#colorfulandcjy0806/Arxiv-tracker&Date)

---

## 🤝 Community contributors

<a href="https://github.com/colorfulandcjy0806/Arxiv-tracker/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=colorfulandcjy0806/Arxiv-tracker" alt="Contributors"/>
</a>

---

## 🔒 License

Released under the **MIT License**. See [LICENSE](./LICENSE).
