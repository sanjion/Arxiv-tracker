# -*- coding: utf-8 -*-
import os, json, re
from typing import Dict, Any

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # 允许在无 openai 包时跳过 LLM

def _json_loose(s: str) -> Dict[str, Any]:
    """
    容错解析，只截取首个 {...} JSON 段
    """
    m = re.search(r"\{.*\}", s, flags=re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except Exception:
        # 尝试去掉尾随逗号等小问题
        t = re.sub(r",\s*([}\]])", r"\1", m.group(0))
        try:
            return json.loads(t)
        except Exception:
            return {}

def call_llm_bilingual_summary(
    item: Dict[str, Any],
    *,
    base_url: str,
    model: str,
    api_key: str,
    system_prompt_zh: str = "",
    system_prompt_en: str = ""
) -> Dict[str, str]:
    """
    让 LLM 直接输出两段“总结”：digest_en / digest_zh
    内容要求：动机、方法、实验结果（各 1-2 句、合成一段）
    """
    client = OpenAI(api_key=api_key, base_url=base_url or None)

    title   = item.get("title") or ""
    summary = item.get("summary") or ""
    comments= item.get("comments") or ""
    venue   = item.get("venue_inferred") or (item.get("journal_ref") or "")

    sys_prompt = system_prompt_en or (
        "You are a precise academic assistant. Summarize papers concisely."
    )

    user_payload = {
        "title": title,
        "abstract": summary,
        "venue_or_comments": (venue or comments or "")
    }

    # 单次请求产出双语，避免两次调用
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": (
            "Given the paper metadata below, write TWO concise one-paragraph digests:\n"
            "1) English paragraph first.\n"
            "2) Then a Simplified Chinese paragraph.\n"
            "- Each paragraph must briefly cover: motivation, method, and main experimental results.\n"
            "- Do not include links, bullet lists, markdown, or headings. Plain sentences only.\n"
            '- Return STRICT JSON: {"digest_en": "...", "digest_zh": "..."}\n\n'
            f"DATA:\n{json.dumps(user_payload, ensure_ascii=False)}"
        )}
    ]

    resp = client.chat.completions.create(
        model=model or "deepseek-chat",
        messages=messages,
        temperature=0.2,
        max_tokens=500,
        stream=False,
    )
    text = resp.choices[0].message.content or ""
    data = _json_loose(text)
    return {
        "digest_en": (data.get("digest_en") or "").strip(),
        "digest_zh": (data.get("digest_zh") or "").strip(),
    }
# ========== 工具函数 ==========
def _loose_json_load(s: str) -> Dict[str, Any]:
    """宽松 JSON 解析：容忍包裹文本/代码块，尽力抽取第一个 {...} 为 JSON。"""
    try:
        return json.loads(s)
    except Exception:
        pass
    m = re.search(r"\{[\s\S]*\}", s)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return {}

# ========== 两阶段摘要（保留你原有接口） ==========
def build_llm_prompt(item: Dict[str, Any], lang: str = "zh", scope: str = "both"):
    title   = item.get("title") or ""
    authors = ", ".join(item.get("authors") or [])
    venue   = item.get("venue_inferred") or (item.get("journal_ref") or "")
    comments = item.get("comments") or ""
    summary  = item.get("summary") or ""
    links = {
        "html": item.get("html_url"),
        "pdf": item.get("pdf_url"),
        "code": item.get("code_urls") or [],
        "project": item.get("project_urls") or [],
        "other": item.get("other_urls") or [],
    }
    meta = {
        "title": title, "authors": authors, "venue": venue,
        "comments": comments, "summary": summary, "links": links
    }
    ask_lang = "中文" if lang == "zh" else "English"
    user_prompt = f"""
请阅读以下论文元信息(JSON)，用{ask_lang}输出“两阶段摘要”：
1) TL;DR（1~2 句，先总后分，避免口号）
2) **Method Card**：任务/动机、核心方法、关键设计、数据与指标、主要结果与结论、局限与未来工作、保留链接（PDF/代码/项目页）
3) **Discussion Questions**：3~5 个高质量问题（可用于组会讨论）
请保留所有给定链接，不要臆造。scope="{scope}" 表示输出范围（tldr/full/both）。

JSON:
{json.dumps(meta, ensure_ascii=False, indent=2)}
""".strip()
    return user_prompt

def call_llm_two_stage(item: Dict[str, Any], lang: str, scope: str,
                       base_url: str, model: str, api_key: str,
                       system_prompt: str = "") -> Dict[str, str]:
    if OpenAI is None:
        raise RuntimeError("openai SDK 未安装，无法调用 LLM（请 pip install openai）。")
    client = OpenAI(api_key=api_key, base_url=base_url)
    user_content = build_llm_prompt(item, lang=lang, scope=scope)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_content})
    resp = client.chat.completions.create(
        model=model, messages=messages, stream=False, temperature=0.2
    )
    text = resp.choices[0].message.content.strip()
    tldr, full_md = "", ""
    if "TL;DR" in text or "TLDR" in text or "Tl;dr" in text:
        parts = text.splitlines()
        tldr_lines, rest_lines, in_tldr = [], [], False
        for ln in parts:
            if "TL;DR" in ln or "TLDR" in ln or "Tl;dr" in ln:
                in_tldr = True
                tldr_lines.append(ln.replace("TL;DR","").replace("TLDR","").replace("Tl;dr","").strip(" :："))
            elif in_tldr and (ln.strip().startswith("**Method") or ln.strip().lower().startswith("**discussion")):
                in_tldr = False
                rest_lines.append(ln)
            elif in_tldr:
                tldr_lines.append(ln)
            else:
                rest_lines.append(ln)
        tldr = " ".join([s.strip() for s in tldr_lines if s.strip()])
        full_md = "\n".join(rest_lines).strip()
    else:
        full_md = text
    return {"tldr": tldr, "full_md": full_md}

# ========== 新增：标题/摘要中文翻译 ==========
def call_llm_translate(item: Dict[str, Any], target_lang: str,
                       base_url: str, model: str, api_key: str,
                       system_prompt: str = "") -> Dict[str, str]:
    """
    返回字典：可能包含 title_zh / summary_zh / comments_zh（按需要）
    """
    if OpenAI is None:
        raise RuntimeError("openai SDK 未安装，无法调用 LLM（请 pip install openai）。")
    title   = item.get("title") or ""
    summary = item.get("summary") or ""
    comments= item.get("comments") or ""

    want_comments = bool(comments.strip())
    schema_keys = ["title_zh", "summary_zh"] + (["comments_zh"] if want_comments else [])

    sys_prompt = system_prompt or "You are a precise academic translator. Translate to Simplified Chinese concisely and faithfully; keep technical terms."

    inst = f"""
Translate the following fields into Simplified Chinese. 
Return ONLY compact JSON with keys {schema_keys} (omit keys you can't translate). 
Do not add commentary.

DATA:
{json.dumps({"title": title, "summary": summary, "comments": comments}, ensure_ascii=False, indent=2)}
""".strip()

    client = OpenAI(api_key=api_key, base_url=base_url)
    messages = [{"role":"system","content":sys_prompt},
                {"role":"user","content":inst}]
    resp = client.chat.completions.create(model=model, messages=messages, stream=False, temperature=0.0)
    text = resp.choices[0].message.content.strip()
    data = _loose_json_load(text)
    out = {}
    if isinstance(data, dict):
        if "title_zh" in data and isinstance(data["title_zh"], str):
            out["title_zh"] = data["title_zh"].strip()
        if "summary_zh" in data and isinstance(data["summary_zh"], str):
            out["summary_zh"] = data["summary_zh"].strip()
        if "comments_zh" in data and isinstance(data["comments_zh"], str):
            out["comments_zh"] = data["comments_zh"].strip()
    return out
