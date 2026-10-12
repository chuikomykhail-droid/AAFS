"""Convert transcript.jsonl to human-readable Markdown dialogue."""
import json
import sys
import re
import os

INPUT = sys.argv[1]
OUTPUT = sys.argv[2]

with open(INPUT, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]

steps = []
for line in lines:
    try:
        steps.append(json.loads(line))
    except json.JSONDecodeError:
        continue

md = []
md.append("# Діалог сесії Claude Opus — Air Alerts Forecast (Етап 0+1)\n")
md.append("> **Модель:** Claude Opus 4.6 (Thinking)  ")
md.append("> **Дата сесії:** 2026-10-10  ")
md.append("> **Гілка:** claude-opus  ")
md.append("> **Завдання:** Етап 0 (каркас) + Етап 1 (EDA розвідка структури даних)\n")
md.append("---\n")

def escape_md(text):
    """Minimal escaping for content inside details blocks."""
    if not text:
        return ""
    return text

def format_tool_calls(tool_calls):
    """Format tool calls into a readable summary."""
    if not tool_calls:
        return ""
    parts = []
    for tc in tool_calls:
        name = tc.get("name", "unknown")
        args = tc.get("args", {})
        summary = args.get("toolSummary", "").strip('"')
        action = args.get("toolAction", "").strip('"')

        if name == "run_command":
            cmd = args.get("CommandLine", "").strip('"')
            # Truncate very long commands
            if len(cmd) > 200:
                cmd = cmd[:200] + "..."
            parts.append(f"**`run_command`**: `{cmd}`")
        elif name == "write_to_file":
            target = args.get("TargetFile", "").strip('"')
            # Shorten paths
            target = target.replace("d:\\\\Flash\\\\golova\\\\KSE_AI\\\\AAFS_claude_opus\\\\", "")
            target = target.replace("d:\\Flash\\golova\\KSE_AI\\AAFS_claude_opus\\", "")
            desc = args.get("Description", "").strip('"')
            parts.append(f"**`write_to_file`**: `{target}` — {desc}")
        elif name == "view_file":
            path = args.get("AbsolutePath", "").strip('"')
            path = path.replace("d:\\\\Flash\\\\golova\\\\KSE_AI\\\\AAFS_claude_opus\\\\", "")
            path = path.replace("d:\\Flash\\golova\\KSE_AI\\AAFS_claude_opus\\", "")
            parts.append(f"**`view_file`**: `{path}`")
        elif name == "replace_file_content":
            target = args.get("TargetFile", "").strip('"')
            target = target.replace("d:\\\\Flash\\\\golova\\\\KSE_AI\\\\AAFS_claude_opus\\\\", "")
            parts.append(f"**`replace_file_content`**: `{target}`")
        elif name == "schedule":
            prompt = args.get("Prompt", "").strip('"')
            dur = args.get("DurationSeconds", "?")
            parts.append(f"**`schedule`**: timer {dur}s — {prompt}")
        elif name == "manage_task":
            action_val = args.get("Action", "").strip('"')
            tid = args.get("TaskId", "").strip('"')
            parts.append(f"**`manage_task`**: {action_val} on `{tid}`")
        else:
            parts.append(f"**`{name}`**: {summary or action}")
    return "\n".join(f"- {p}" for p in parts)

for step in steps:
    source = step.get("source", "")
    stype = step.get("type", "")
    content = step.get("content", "")
    thinking = step.get("thinking", "")
    tool_calls = step.get("tool_calls", [])
    created = step.get("created_at", "")
    status = step.get("status", "")
    error = step.get("error", "")

    # User message
    if source == "USER_EXPLICIT" and stype == "USER_INPUT":
        # Extract the actual user request from XML tags
        user_text = content
        match = re.search(r"<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>", content, re.DOTALL)
        if match:
            user_text = match.group(1).strip()
        md.append(f"\n## 👤 Користувач *({created})*\n")
        md.append(user_text)
        md.append("")

    # Model response
    elif source == "MODEL" and stype == "PLANNER_RESPONSE":
        if content or thinking or tool_calls:
            md.append(f"\n## 🤖 Асистент *({created})*\n")

            # Main content (visible)
            if content:
                md.append(content)
                md.append("")

            # Thinking (hidden)
            has_hidden = thinking or tool_calls
            if has_hidden:
                md.append("<details>")
                summary_parts = []
                if thinking:
                    summary_parts.append("хід думок")
                if tool_calls:
                    summary_parts.append(f"{len(tool_calls)} виклик(ів) інструментів")
                md.append(f"<summary>🔧 {' / '.join(summary_parts)}</summary>\n")

                if thinking:
                    md.append(f"**Thinking:** {thinking}\n")

                if tool_calls:
                    formatted = format_tool_calls(tool_calls)
                    md.append(formatted)
                    md.append("")

                md.append("</details>\n")

    # Tool output (summarize, don't show full output)
    elif source == "MODEL" and stype == "GENERIC":
        if content and len(content) > 50:
            # Only show significant tool outputs
            if "exited with code" in content or "Created file" in content:
                # Very brief summary
                if "exited with code 0" in content:
                    short = "✅ Команда виконана успішно"
                elif "exited with code 1" in content:
                    short = "❌ Команда завершилася з помилкою"
                elif "Created file" in content:
                    match = re.search(r"Created file file:///(.+?) with", content)
                    if match:
                        fpath = match.group(1).replace("d:/Flash/golova/KSE_AI/AAFS_claude_opus/", "")
                        short = f"📄 Створено файл: `{fpath}`"
                    else:
                        short = "📄 Файл створено"
                else:
                    short = None

                if short:
                    md.append(f"> {short}\n")

    # System messages
    elif source == "SYSTEM" and stype == "SYSTEM_MESSAGE":
        if "task-" in content and "finished" in content:
            match = re.search(r"task-(\d+).*?finished", content)
            if match:
                md.append(f"> ⚙️ Фонова задача task-{match.group(1)} завершена\n")

    # Errors
    elif source == "SYSTEM" and stype == "ERROR_MESSAGE":
        if error:
            md.append(f"\n> ⚠️ **Системна помилка:** `{error[:120]}...`\n")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print(f"Written {len(md)} lines to {OUTPUT}")

