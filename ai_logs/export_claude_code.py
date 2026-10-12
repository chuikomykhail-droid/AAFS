#!/usr/bin/env python3
"""Выгрузка логов Claude Code проекта AAFS в читаемый вид для сдачи.

Запуск из корня репозитория:
    python ai_logs/export_claude_code.py

Идемпотентно: каталоги ai_logs/claude_code/ и ai_logs/claude_ai/ пересоздаются
целиком; в ai_logs/README.md перезаписываются только блоки между метками AUTO,
остальной текст не трогается.

  * ai_logs/claude_code/<дата>_<имя>_<id8>.md — сессия (файл > ~800 КБ разбит по дням);
  * ai_logs/claude_code/review_agents/<описание>_<agent id>.md — субагенты;
  * ai_logs/claude_code/raw/ — копии исходных JSONL (zip, если суммарно > 40 МБ);
  * ai_logs/claude_ai/ — чат claude.ai, выгруженный вручную (md и raw/jsonl).

Токен alerts.in.ua (из alerts_api/token.txt) и email автора заменяются на
[REDACTED_TOKEN] / [REDACTED_EMAIL] прямо в сырых строках, до разбора JSON, так что
обрезка текста не может оставить половину секрета. Email в скрипте не хранится:
заменяется любой адрес, чей sha256 совпадает с EMAIL_SHA256. Значения секретов
скрипт не печатает — только счётчики.
"""
import argparse
import hashlib
import html
import json
import re
import shutil
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo

    KYIV = ZoneInfo("Europe/Kyiv")
except Exception:  # нет tzdata: в октябре 2026 Киев живёт по UTC+3
    KYIV = timezone(timedelta(hours=3))

REPO = Path(__file__).resolve().parent.parent
LOGS = REPO / "ai_logs"
OUT_MD = LOGS / "claude_code"
OUT_SUB = OUT_MD / "review_agents"
OUT_RAW = OUT_MD / "raw"
AG = LOGS / "antigravity"  # выгрузка Antigravity (делал Gemini): только читаем
README = LOGS / "README.md"
TOKEN_FILE = REPO / "alerts_api" / "token.txt"
DEFAULT_SRC = Path.home() / ".claude" / "projects" / "d--Flash-golova-KSE-AI-AAFS"

# Основные сессии → короткое имя файла по заголовку чата (aiTitle);
# их субагенты берутся из <id>/subagents/agent-*.jsonl и называются по описанию.
SESSIONS = {
    "2d7ee671-bb22-400b-9eaa-1e096b56edfb": "stage2-plan-decisions",  # «Этап 2, PLAN.md и DECISIONS.md»
    "57049ae5-374c-471e-8191-1ff2343b8a66": "critical-analysis",  # «Критический анализ проекта AAFS»
    "0efe39d2-50ae-4278-9729-dd4dc5bba493": "yellow-red-alerts",  # «Жёлтые и красные тревоги в KSE_AI»
}
# Чат с claude.ai (браузер), выгруженный вручную: копируются md и jsonl с теми же заменами.
CLAUDE_AI = [Path.home() / "Downloads" / "chat_planning.md", Path.home() / "Downloads" / "chat_planning.jsonl"]
OUT_AI = LOGS / "claude_ai"
EMAIL_SHA256 = "121a7c584c173873c4ca775967e4e94a8f48dde5d77ba733b08006bdf4ef1c4d"
ARG_LIMIT, RESULT_LIMIT = 2000, 3000
SPLIT_BYTES = 800_000
ZIP_BYTES = 40_000_000
README_MARK = "<!-- CC-EXPORT:README -->"

EMAIL_RE = re.compile(r"[A-Za-z0-9._+-]+(?:@|%40)[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
SERVICE_RE = re.compile(
    r"<(system-reminder|ide_opened_file|ide_selection|local-command-caveat|command-message)\b[^>]*>.*?</\1>\s*",
    re.S,
)
PASTE_RE = re.compile(r"<(/?)pasted_content\b[^>]*>")
REPO_PREFIX = re.compile(r"(?i)^(?:[a-z]:|/[a-z])?/Flash/golova/KSE_AI/AAFS/")

CATEGORIES = [
    ("Пойманные ошибки", re.compile(r"(?i)ошиб|помил|\bбаг|\bbugs?\b|поймал|неверн|неправильн")),
    ("Ревью", re.compile(r"(?i)ревью|рев['’]?ю|review|аудит")),
    ("Утечка", re.compile(r"(?i)утеч|витік|витоку|leak|look-?ahead|заглядыв")),
]
D_RE = re.compile(r"\bD(\d{1,2})\b")


# ---------- замены секретов ----------

class Redactor:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if len(t) >= 8]
        self.counts = Counter()

    def _is_email(self, addr):
        return hashlib.sha256(addr.replace("%40", "@").lower().encode()).hexdigest() == EMAIL_SHA256

    def _email(self, m):
        if self._is_email(m.group(0)):
            self.counts["email"] += 1
            return "[REDACTED_EMAIL]"
        return m.group(0)

    def __call__(self, s):
        for t in self.tokens:
            n = s.count(t)
            if n:
                self.counts["token"] += n
                s = s.replace(t, "[REDACTED_TOKEN]")
        if "@" in s or "%40" in s:
            s = EMAIL_RE.sub(self._email, s)
        return s

    def leaks(self, s):
        """Следы секретов в готовом тексте: (вхождения префикса токена, адреса автора)."""
        tok = sum(s.count(t[:16]) for t in self.tokens)
        mail = sum(1 for m in EMAIL_RE.finditer(s) if self._is_email(m.group(0)))
        return tok, mail


# ---------- форматирование ----------

def parse_ts(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v / 1000 if v > 1e12 else v, timezone.utc)
    s = re.sub(r"(\.\d{6})\d+", r"\1", str(v).replace("Z", "+00:00"))
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def kyiv(dt, fmt="%Y-%m-%d %H:%M"):
    return dt.astimezone(KYIV).strftime(fmt) if dt else "—"


def utc(dt, fmt="%Y-%m-%d %H:%M"):
    return dt.astimezone(timezone.utc).strftime(fmt) if dt else "—"


def strip_service(s):
    return SERVICE_RE.sub("", s)


def one_line(s, n):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def cell(s):
    return s.replace("|", "\\|").replace("<", "&lt;")


def trunc(s, n):
    return s if len(s) <= n else f"{s[:n]}\n… [обрезано: показано {n} из {len(s)} символов]"


def fence(s, lang=""):
    run = max((len(m) for m in re.findall(r"`+", s)), default=0)
    f = "`" * max(3, run + 1)
    return f"{f}{lang}\n{s}\n{f}"


def details(summary, body):
    return f"<details><summary>{html.escape(summary, quote=False)}</summary>\n\n{body}\n\n</details>\n"


def slugify(s, n=40):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:n].rstrip("-") or "agent"


def rel(p):
    return REPO_PREFIX.sub("", str(p or "").replace("\\", "/"))


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type", "text") == "text")
    return "" if content is None else json.dumps(content, ensure_ascii=False)


def tool_brief(name, inp):
    g = inp.get if isinstance(inp, dict) else (lambda k, d=None: d)
    if name in ("Bash", "PowerShell", "Monitor"):
        s = g("description") or g("command", "")
    elif name in ("Read", "Write", "Edit", "NotebookEdit"):
        s = rel(g("file_path") or g("notebook_path", ""))
    elif name in ("Grep", "Glob"):
        s = g("pattern", "") + (f" в {rel(g('path'))}" if g("path") else "")
    elif name == "Agent":
        s = g("description") or g("prompt", "")
    elif name == "SendMessage":
        msg = g("message")
        s = f"{g('to', '')}: {msg if isinstance(msg, str) else ''}"
    elif name == "AskUserQuestion":
        qs = g("questions") or []
        s = qs[0].get("question", "") if qs and isinstance(qs[0], dict) else ""
    else:
        s = g("query") or g("url") or g("skill") or json.dumps(inp, ensure_ascii=False)
    return one_line(s, 120)


def fmt_args(name, inp):
    if not isinstance(inp, dict):
        return json.dumps(inp, ensure_ascii=False, indent=1), "json"
    if name == "Bash":
        return inp.get("command", ""), "bash"
    if name == "PowerShell":
        return inp.get("command", ""), "powershell"
    if name == "Write":
        return f"# file: {rel(inp.get('file_path'))}\n{inp.get('content', '')}", ""
    if name == "Edit":
        return (f"# file: {rel(inp.get('file_path'))}\n--- old_string ---\n{inp.get('old_string', '')}"
                f"\n--- new_string ---\n{inp.get('new_string', '')}"), ""
    return json.dumps(inp, ensure_ascii=False, indent=1), "json"


def result_text(block):
    c = block.get("content")
    if isinstance(c, list):
        parts = []
        for b in c:
            t = b.get("type")
            if t == "text":
                parts.append(b.get("text", ""))
            elif t == "image":
                parts.append("[изображение опущено]")
            elif t == "tool_reference":
                parts.append(f"[tool_reference: {b.get('tool_name', '')}]")
            else:
                parts.append(f"[{t}]")
        c = "\n".join(parts)
    elif c is None:
        c = ""
    return strip_service(str(c)).strip()


# ---------- модель сессии ----------

@dataclass
class Item:
    ts: datetime | None
    md: str
    kind: str  # user | assistant | tool | notice
    anchor: str | None = None
    text: str = ""  # для поиска кандидатов в README


@dataclass
class Session:
    sid: str
    short: str
    lines: list
    records: list
    bad: int = 0
    parent: "Session | None" = None
    meta: dict = field(default_factory=dict)
    meta_raw: str = ""
    raw_name: str = ""
    raw_ref: str = ""
    slug: str = ""
    title: str = ""
    items: list = field(default_factory=list)
    stats: Counter = field(default_factory=Counter)
    parts: list = field(default_factory=list)  # [(день | None, [Item], имя файла)]
    anchor_file: dict = field(default_factory=dict)

    @property
    def start(self):
        return next((t for t in (parse_ts(r.get("timestamp")) for r in self.records) if t), None)

    @property
    def end(self):
        return next((t for t in (parse_ts(r.get("timestamp")) for r in reversed(self.records)) if t), None)


def load(path, red):
    lines, recs, seen, bad = [], [], set(), 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = red(line)
            lines.append(line)
            try:
                r = json.loads(line)
            except json.JSONDecodeError:  # например, недописанная последняя строка живой сессии
                bad += 1
                continue
            u = r.get("uuid")
            if u in seen:
                continue
            if u:
                seen.add(u)
            recs.append(r)
    return lines, recs, bad


def anchor_of(r, i=0):
    base = (r.get("uuid") or hashlib.md5(json.dumps(r, sort_keys=True).encode()).hexdigest())[:8]
    return f"m-{base}" + (f"-{i}" if i else "")


def user_item(text, who, ts, anc, imgs=0):
    if re.match(r"\s*<task-notification>", text):
        m = re.search(r"<summary>(.*?)</summary>", text, re.S) or re.search(r"<status>(.*?)</status>", text, re.S)
        label = one_line(m.group(1), 100) if m else "фоновая задача"
        body = fence(trunc(strip_service(text).strip(), RESULT_LIMIT))
        return Item(ts, details(f"🔔 Уведомление: {label} · {kyiv(ts, '%H:%M')}", body), "notice")
    s = strip_service(text)
    m = re.search(r"<local-command-stdout>(.*?)</local-command-stdout>", s, re.S)
    if m:
        out = m.group(1).strip()
        if not out:
            return None
        return Item(ts, details(f"Вывод локальной команды · {kyiv(ts, '%H:%M')}", fence(trunc(out, RESULT_LIMIT))), "notice")
    m = re.search(r"<command-name>(.*?)</command-name>", s, re.S)
    if m:
        args = re.search(r"<command-args>(.*?)</command-args>", s, re.S)
        s = "`" + " ".join(x for x in (m.group(1).strip(), args.group(1).strip() if args else "") if x) + "`"
    s = PASTE_RE.sub(lambda m: "\n\n> *[конец вставленного текста]*\n\n" if m.group(1)
                     else "\n\n> *[вставленный текст]*\n\n", s).strip()
    if imgs:
        s = (s + "\n\n" if s else "") + " ".join(["*[изображение опущено]*"] * imgs)
    if not s:
        return None
    return Item(ts, f'<a id="{anc}"></a>\n\n### {who} · {kyiv(ts)}\n\n{s}\n', "user", anc, s)


def tool_item(b, ts, results, agent_links):
    name, inp, tid = b.get("name", "?"), b.get("input") or {}, b.get("id") or ""
    args, lang = fmt_args(name, inp)
    body = "**Аргументы**\n\n" + fence(trunc(args, ARG_LIMIT), lang)
    if tid in results:
        res, err = results[tid]
        body += f"\n\n**Результат**{' (ошибка)' if err else ''}\n\n" + fence(trunc(res, RESULT_LIMIT) if res else "(пусто)")
    else:
        body += "\n\n*Результата в логе нет.*"
    anc = f"t-{tid[-12:]}" if name == "Agent" and tid else None
    md = (f'<a id="{anc}"></a>\n\n' if anc else "") + details(f"🔧 {name}: {tool_brief(name, inp)} · {kyiv(ts, '%H:%M')}", body)
    if tid in agent_links:
        title, href = agent_links[tid]
        md += f"\n↳ Лог субагента: [{title}]({href})\n"
    return Item(ts, md, "tool", anc)


def render(sess, agent_links):
    st, sub = sess.stats, sess.parent is not None
    results = {}
    for r in sess.records:
        c = (r.get("message") or {}).get("content") if r.get("type") == "user" else None
        if isinstance(c, list):
            for b in c:
                if b.get("type") == "tool_result":
                    results[b.get("tool_use_id")] = (result_text(b), bool(b.get("is_error")))
    items, got_task = [], False
    for r in sess.records:
        t, ts = r.get("type"), parse_ts(r.get("timestamp"))
        if t == "ai-title":
            sess.title = r.get("aiTitle") or sess.title
            st["service"] += 1
        elif t == "user":
            if r.get("isMeta"):
                st["service"] += 1
                continue
            c = (r.get("message") or {}).get("content")
            if isinstance(c, str):
                text, imgs = c, 0
            elif isinstance(c, list):
                texts = [b.get("text", "") for b in c if b.get("type") == "text"]
                imgs = sum(1 for b in c if b.get("type") == "image")
                if not texts and not imgs:
                    continue  # только результаты инструментов — они показаны у вызовов
                text = "\n\n".join(texts)
            else:
                continue
            if r.get("isCompactSummary"):
                body = fence(trunc(strip_service(text).strip(), RESULT_LIMIT))
                items.append(Item(ts, details(f"📋 Автосводка предыдущего контекста (compact) · {kyiv(ts, '%H:%M')}", body), "notice"))
                continue
            if sub:
                who = "📨 Сообщение от основного агента" if got_task else "📨 Задание от основного агента"
            else:
                who = "👤 Пользователь"
            it = user_item(text, who, ts, anchor_of(r), imgs)
            if it:
                items.append(it)
                got_task = got_task or it.kind == "user"
            else:
                st["service"] += 1
        elif t == "attachment":
            a = r.get("attachment") or {}
            if a.get("type") != "queued_command":
                st["service"] += 1
                continue
            p = a.get("prompt")
            imgs = 0 if isinstance(p, str) else sum(1 for b in p or [] if isinstance(b, dict) and b.get("type") == "image")
            who = "📨 Сообщение от основного агента" if sub else "👤 Пользователь (написано во время работы ассистента)"
            it = user_item(text_of(p), who, ts, anchor_of(r), imgs)
            if it:
                items.append(it)
        elif t == "assistant":
            c = (r.get("message") or {}).get("content")
            if isinstance(c, str):
                c = [{"type": "text", "text": c}]
            if r.get("isApiErrorMessage"):
                txt = one_line(" ".join(b.get("text", "") for b in c or [] if b.get("type") == "text"), 200)
                items.append(Item(ts, f"*[ошибка API · {kyiv(ts, '%H:%M')}: {html.escape(txt)}]*\n", "notice"))
                continue
            for i, b in enumerate(c or []):
                bt = b.get("type")
                if bt == "text":
                    txt = strip_service(b.get("text", "")).strip()
                    if txt:
                        anc = anchor_of(r, i)
                        items.append(Item(ts, f'<a id="{anc}"></a>\n\n**🤖 Ассистент** · {kyiv(ts)}\n\n{txt}\n', "assistant", anc, txt))
                        st["assistant"] += 1
                elif bt == "tool_use":
                    items.append(tool_item(b, ts, results, agent_links))
                    st["tools"] += 1
                    st["agents"] += b.get("name") == "Agent"
                elif bt in ("thinking", "redacted_thinking"):
                    st["thinking"] += 1
                elif bt == "image":
                    items.append(Item(ts, "*[изображение опущено]*\n", "notice"))
        elif t == "system" and r.get("subtype") == "compact_boundary":
            items.append(Item(ts, f"\n---\n\n*[{kyiv(ts)} — контекст сжат (compact); дальше продолжение той же сессии]*\n\n---\n", "notice"))
        else:
            st["service"] += 1
    st["user"] = sum(1 for it in items if it.kind == "user")
    sess.items = items


def layout(sess, name_fn):
    size = sum(len(it.md.encode()) + 1 for it in sess.items)
    if size <= SPLIT_BYTES:
        groups = {None: sess.items}
    else:
        groups, day = {}, kyiv(sess.start, "%Y-%m-%d")
        for it in sess.items:
            day = kyiv(it.ts, "%Y-%m-%d") if it.ts else day
            groups.setdefault(day, []).append(it)
    sess.parts = [(day, items, name_fn(day)) for day, items in groups.items()]
    for _, items, fname in sess.parts:
        for it in items:
            if it.anchor:
                sess.anchor_file[it.anchor] = fname


def write_session(sess, outdir):
    st, n, sub = sess.stats, len(sess.parts), sess.parent is not None
    written = []
    for i, (day, items, fname) in enumerate(sess.parts, 1):
        title = f"# Субагент: {sess.title}" if sub else f"# Claude Code · сессия {sess.short}" + (f": {sess.title}" if sess.title else "")
        if n > 1:
            title += f" — часть {i}/{n} ({day})"
        h = [title, ""]
        if sub:
            p, tid = sess.parent, sess.meta.get("toolUseId") or ""
            anc = f"t-{tid[-12:]}"
            back = f"../{p.anchor_file[anc]}#{anc}" if anc in p.anchor_file else f"../{p.parts[0][2]}"
            h.append(f"- **Агент:** `{sess.sid}` ({sess.meta.get('agentType', '?')}), запущен из сессии [{p.short}]({back})")
            who = f"задания и сообщения основного агента — {st['user']}, ответы субагента — {st['assistant']}"
        else:
            h.append(f"- **ID сессии:** `{sess.sid}`")
            who = f"пользователь — {st['user']}, ассистент — {st['assistant']}"
        h.append(f"- **Период (UTC):** {utc(sess.start)} → {utc(sess.end)}")
        h.append(f"- **Период (Киев):** {kyiv(sess.start)} → {kyiv(sess.end)}")
        h.append(f"- **Сообщений:** {st['user'] + st['assistant']} ({who}); вызовов инструментов — {st['tools']}"
                 + (f"; запущено субагентов — {st['agents']}" if st["agents"] else ""))
        if n > 1:
            links = " · ".join(f"**{d}**" if j == i else f"[{d}]({f})" for j, (d, _, f) in enumerate(sess.parts, 1))
            h.append(f"- **Части по дням (Киев):** {links}")
        h.append(f"- **Исходный JSONL:** `{sess.raw_ref}`")
        h += ["", "> Служебные вставки (`<system-reminder>`, вложения с окружением и контекстом IDE, мета-сообщения — "
              f"{st['service']} записей) и блоки рассуждений (thinking — {st['thinking']}) сюда не включены: они есть "
              "в исходном JSONL. Время — киевское. Вызовы инструментов свёрнуты; аргументы обрезаны до 2000 символов, "
              "результаты — до 3000. Токен alerts.in.ua и email автора заменены на `[REDACTED_TOKEN]` / `[REDACTED_EMAIL]`.",
              "", "---", ""]
        path = outdir / fname
        path.write_text("\n".join(h) + "\n" + "\n".join(it.md for it in items), encoding="utf-8", newline="\n")
        written.append(path)
    return written


# ---------- README ----------

def pick(lst, n):
    if len(lst) <= n:
        return lst
    return [lst[round(i * (len(lst) - 1) / (n - 1))] for i in range(n)]


def snippet(text, m):
    s = max(0, m.start() - 60)
    quote = cell(one_line(("…" if s else "") + text[s:m.end() + 100], 170))
    return quote.replace("[", "\\[").replace("]", "\\]").replace("`", "'")  # цитата, а не ссылки и код


AG_TAGS_RE = re.compile(r"<(ADDITIONAL_METADATA|USER_SETTINGS_CHANGE)\b[^>]*>.*?</\1>", re.S)


def ext_chat(jsonl, md, red):
    """Чат не из Claude Code (claude.ai или Antigravity): только для таблицы и кандидатов, файлы не меняются."""
    msgs, first_any = [], ""
    for line in open(jsonl, encoding="utf-8"):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "role" in r:  # claude.ai
            role, ts = r.get("role"), parse_ts(r.get("timestamp"))
        else:  # Antigravity
            role = {"USER_INPUT": "user", "PLANNER_RESPONSE": "assistant"}.get(r.get("type"))
            ts = parse_ts(r.get("created_at"))
        text = re.sub(r"</?[A-Z_]+>", " ", AG_TAGS_RE.sub("", text_of(r.get("content")))).strip()
        first_any = first_any or text
        if role in ("user", "assistant") and text:
            msgs.append((ts, role, red(text)))
    ts = [m[0] for m in msgs if m[0]]
    users = [m for m in msgs if m[1] == "user"]
    first = users[0][2] if users else red(first_any)
    return {"md": md.relative_to(LOGS).as_posix(), "start": min(ts) if ts else None, "end": max(ts) if ts else None,
            "n": len(msgs), "first": one_line(first, 100) + ("" if users else " *(задание агенту)*"), "msgs": msgs}


def ext_groups(red, ai_jsonl):
    groups = []
    if ai_jsonl and ai_jsonl.exists():
        groups.append(("claude.ai — чат планирования", [ext_chat(ai_jsonl, OUT_AI / f"{ai_jsonl.stem}.md", red)]))
    if (AG / "raw" / "main_dialogue.jsonl").exists():
        groups.append(("Antigravity — основной чат", [ext_chat(AG / "raw" / "main_dialogue.jsonl", AG / "main_dialogue.md", red)]))
    stage1 = [ext_chat(p, next((p.parent.parent / n for n in ("chat.md", "main_dialogue.md") if (p.parent.parent / n).exists()),
                               p.parent.parent / "chat.md"), red)
              for p in sorted(AG.glob("stage1_agents/*/raw/transcript.jsonl"))]
    if stage1:
        groups.append(("Antigravity — агенты этапа 1", stage1))
    reviews = [ext_chat(p, p.parent.parent / f"{p.stem}.md", red)
               for p in sorted(AG.glob("review_agents/raw/*.jsonl")) if not p.stem.endswith("_full")]
    if reviews:
        groups.append(("Antigravity — агенты ревью (gemini-3.1-pro)", reviews))
    return groups


def readme_blocks(mains, subs, groups, red):
    head = ["| Файл | Период (Киев) | Сообщений | Первая реплика пользователя |", "|---|---|---|---|"]
    rows = []
    for title, chats in groups:
        rows += [f"**{title}**", ""] + head
        rows += [f"| [{c['md']}]({c['md']}) | {kyiv(c['start'])} → {kyiv(c['end'])} | {c['n']} | {cell(c['first'])} |" for c in chats]
        rows.append("")

    def cc_row(s, prefix, label=""):
        files = "<br>".join(f"[{f}]({prefix}{f})" for _, _, f in s.parts)
        first = next((it.text for it in s.items if it.kind == "user"), "")
        return (f"| {label}{files} | {kyiv(s.start)} → {kyiv(s.end)} | {s.stats['user'] + s.stats['assistant']} "
                f"| {cell(one_line(first, 100))} |")

    rows += ["**Claude Code — сессии и агенты ревью**", ""] + head
    for s in sorted(mains, key=lambda s: s.start):
        rows.append(cc_row(s, "claude_code/"))
        rows += [cc_row(ss, "claude_code/review_agents/", "↳ ") for ss in subs if ss.parent is s]
    rows += ["", "Сообщений = реплики пользователя + текстовые ответы ассистента; вызовы инструментов не считаются. "
             "У агентов «пользователь» — тот, кто их запустил: основной агент или первый запрос."]

    # кандидаты: упоминания по ключевым словам
    pool = []
    for s in sorted(mains, key=lambda s: s.start):
        for it in s.items:
            if it.kind in ("user", "assistant"):
                pool.append((it.ts, it.kind, it.text, f"[Claude Code {s.short} · {kyiv(it.ts)}]"
                             f"(claude_code/{s.anchor_file[it.anchor]}#{it.anchor})"))
    ext_pool = [(ts, role, text, f"[{title.split(' — ')[0]} · {kyiv(ts)}]({c['md']})")
                for title, chats in groups for c in chats for ts, role, text in c["msgs"]]
    c = ["Собрано скриптом по ключевым словам; это указатель, а не выводы.", ""]
    counts = Counter()
    for cat, rx in CATEGORIES:
        c.append(f"#### {cat}")
        for label, src, kind, cap in (("Claude Code — реплики пользователя", pool, "user", 15),
                                      ("Claude Code — ответы ассистента", pool, "assistant", 8),
                                      ("claude.ai и Antigravity — реплики пользователя", ext_pool, "user", 10),
                                      ("claude.ai и Antigravity — ответы ассистента", ext_pool, "assistant", 6)):
            hits = [(text, ref, m) for ts, k, text, ref in src if k == kind for m in [rx.search(text)] if m]
            if hits:
                chosen = pick(hits, cap)
                counts[cat] += len(chosen)
                c += ["", f"{label} ({len(chosen)} из {len(hits)}):"]
                c += [f"- {ref} — «{snippet(text, m)}»" for text, ref, m in chosen]
        c.append("")
    c.append("#### D-номера решений (первое упоминание каждого)")
    first = {}
    for ts, _, text, ref in sorted(pool + ext_pool, key=lambda x: x[0] or datetime.min.replace(tzinfo=timezone.utc)):
        for m in D_RE.finditer(text):
            first.setdefault(int(m.group(1)), (ref, text, m))
    counts["D"] = len(first)
    c += [""] + [f"- D{n}: {ref} — «{snippet(text, m)}»" for n, (ref, text, m) in sorted(first.items())]
    return "\n".join(rows), "\n".join(c), counts


def skeleton(old):
    parts = [
        README_MARK,
        "# Логи работы с ИИ-ассистентами",
        "",
        "Выгрузки: [`claude_ai/`](claude_ai/), [`antigravity/`](antigravity/), [`claude_code/`](claude_code/); "
        "сырые файлы — в `raw/` внутри каждой папки. Claude Code и claude.ai выгружены скриптом "
        "[`export_claude_code.py`](export_claude_code.py).",
        "",
        "## Состав",
        "",
        "<!-- AUTO:table -->",
        "<!-- /AUTO:table -->",
        "",
        "## Ключевые моменты",
        "",
        "",
        "### Кандидаты (найдены скриптом по ключевым словам)",
        "",
        "<!-- AUTO:candidates -->",
        "<!-- /AUTO:candidates -->",
        "",
        "## Рефлексия",
        "",
        "",
    ]
    if old.strip():
        parts += ["---", "", "<details><summary>Прежний README выгрузки Antigravity (сделан Gemini)</summary>", "",
                  old.strip(), "", "</details>", ""]
    return "\n".join(parts)


def replace_block(text, name, content):
    pat = re.compile(rf"(<!-- AUTO:{name} -->\n).*?(<!-- /AUTO:{name} -->)", re.S)
    if not pat.search(text):
        print(f"README: метки AUTO:{name} не найдены — блок не обновлён")
        return text
    return pat.sub(lambda m: m.group(1) + content.rstrip() + "\n" + m.group(2), text)


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description="Выгрузка логов Claude Code проекта AAFS")
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC, help="папка с JSONL Claude Code")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    tokens = [l.strip() for l in TOKEN_FILE.read_text("utf-8-sig").splitlines() if l.strip()] if TOKEN_FILE.exists() else []
    if not tokens:
        print("ВНИМАНИЕ: alerts_api/token.txt не найден или пуст — токен заменён не будет", file=sys.stderr)
    red = Redactor(tokens)

    mains, subs = [], []
    for sid, slug in SESSIONS.items():
        lines, recs, bad = load(args.src / f"{sid}.jsonl", red)
        s = Session(sid, sid[:8], lines, recs, bad, raw_name=f"{sid}.jsonl")
        s.slug = slug
        mains.append(s)
        for p in sorted((args.src / sid / "subagents").glob("agent-*.jsonl")):
            meta_p = p.with_suffix(".meta.json")
            meta_raw = red(meta_p.read_text("utf-8")) if meta_p.exists() else ""
            lines, recs, bad = load(p, red)
            agent = p.stem.removeprefix("agent-")
            subs.append(Session(agent, agent, lines, recs, bad, parent=s, meta=json.loads(meta_raw) if meta_raw else {},
                                meta_raw=meta_raw, raw_name=f"subagents/{s.short}_{p.stem}.jsonl"))

    for d in (OUT_MD, OUT_AI):
        if d.exists():
            shutil.rmtree(d)
    OUT_SUB.mkdir(parents=True)
    OUT_RAW.mkdir(parents=True)
    written = []

    # сырые копии
    entries = [(s.raw_name, "".join(s.lines)) for s in mains + subs]
    entries += [(s.raw_name.replace(".jsonl", ".meta.json"), s.meta_raw) for s in subs if s.meta_raw]
    total = sum(len(t.encode("utf-8")) for _, t in entries)
    zipped = total > ZIP_BYTES
    if zipped:
        zp = OUT_RAW / "claude_code_raw.zip"
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for name, text in entries:
                z.writestr(name, text.encode("utf-8"))
        written.append(zp)
    else:
        for name, text in entries:
            p = OUT_RAW / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(text.encode("utf-8"))
            written.append(p)
    for s in mains + subs:
        s.raw_ref = f"ai_logs/claude_code/raw/claude_code_raw.zip → {s.raw_name}" if zipped else f"ai_logs/claude_code/raw/{s.raw_name}"

    # Markdown: сначала субагенты (нужны имена их файлов для ссылок), потом основные сессии
    for ss in subs:
        render(ss, {})
        first = next((it.text for it in ss.items if it.kind == "user"), "")
        ss.title = one_line(ss.meta.get("description") or first or ss.sid, 100)
        ss_prefix = f"{slugify(ss.meta.get('description') or ss.sid)}_{ss.sid[:8]}"
        layout(ss, lambda day, b=ss_prefix: f"{b}_{day}.md" if day else f"{b}.md")
    agent_links = {ss.meta["toolUseId"]: (ss.title, f"review_agents/{ss.parts[0][2]}") for ss in subs if ss.meta.get("toolUseId")}
    for s in mains:
        render(s, agent_links)
        start_day = kyiv(s.start, "%Y-%m-%d")
        layout(s, lambda day, sd=start_day, b=f"{s.slug}_{s.short}": f"{day or sd}_{b}.md")
    for ss in subs:
        written += write_session(ss, OUT_SUB)
    for s in mains:
        written += write_session(s, OUT_MD)

    # claude.ai: очищенные копии
    ai_jsonl = None
    for src in CLAUDE_AI:
        if not src.exists():
            print(f"claude.ai: нет файла {src.name} — пропущен")
            continue
        dst = (OUT_AI if src.suffix == ".md" else OUT_AI / "raw") / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(red(src.read_text("utf-8")), encoding="utf-8", newline="\n")
        written.append(dst)
        if src.suffix == ".jsonl":
            ai_jsonl = dst

    # README: только блоки AUTO
    table, cands, ccounts = readme_blocks(mains, subs, ext_groups(red, ai_jsonl), red)
    old = README.read_text("utf-8") if README.exists() else ""
    text = old if README_MARK in old else skeleton(old)
    text = replace_block(replace_block(text, "table", table), "candidates", cands)
    README.write_text(text, encoding="utf-8", newline="\n")

    # отчёт: только имена, размеры и счётчики
    print(f"Заменено: токен — {red.counts['token']}, email — {red.counts['email']}")
    bad = {s.raw_name: s.bad for s in mains + subs if s.bad}
    if bad:
        print("Нечитаемых строк JSONL (пропущены в Markdown, сохранены в raw):", bad)
    print(f"Сырые JSONL: {total / 1e6:.1f} МБ → {'zip' if zipped else 'копии файлов'}")
    print("Кандидаты в README:", dict(ccounts))
    leaks = Counter()
    for p in written + [README]:
        if p.suffix == ".zip":
            with zipfile.ZipFile(p) as z:
                texts = [z.read(n).decode("utf-8") for n in z.namelist()]
        else:
            texts = [p.read_text("utf-8")]
        for t in texts:
            tok, mail = red.leaks(t)
            leaks["token"] += tok
            leaks["email"] += mail
    print(f"Проверка готовых файлов (включая содержимое zip): следов токена — {leaks['token']}, email — {leaks['email']}")
    print("Файлы:")
    for p in sorted(written) + [README]:
        print(f"  {p.relative_to(REPO).as_posix():70s} {p.stat().st_size / 1024:9.1f} КБ")


if __name__ == "__main__":
    main()
