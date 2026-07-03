#!/usr/bin/env python3
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path.home() / "Documents" / "Cline" / "Logs" / "context-guard"
BASE_DIR.mkdir(parents=True, exist_ok=True)

THRESHOLDS = [
    (20000, "early"),
    (50000, "medium"),
    (100000, "high"),
]

OVERSIZED_RESULT_CHARS = 80000
OVERSIZED_RESULT_TOKENS = 20000
PREVIEW_CHARS = 4000
BROAD_ROOTS = {
    str(Path.home()),
    str(Path.home() / "Desktop"),
    "/",
}
GENERIC_REGEXES = {".*", ".+", ".", "^.*$", ".*?", r"\w+", r"\w*"}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(value: str) -> str:
    safe = []
    for ch in (value or "").lower():
        if ch.isalnum():
            safe.append(ch)
        elif ch in ("-", "_", "."):
            safe.append(ch)
        else:
            safe.append("-")
    text = "".join(safe).strip("-")
    return text or "tool"


def project_slug_prefix() -> str:
    slug = slugify(os.getenv("CLINE_PROJECT_SLUG", "").strip())
    return f"{slug}__" if slug else ""


def project_label() -> str:
    return os.getenv("CLINE_PROJECT_LABEL", "").strip()


def to_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False, indent=2)
    except Exception:
        return str(value)


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, len(text) // 4)


def get_task_dir(task_id: str) -> Path:
    task_path = BASE_DIR / task_id
    (task_path / "raw").mkdir(parents=True, exist_ok=True)
    (task_path / "recovery").mkdir(parents=True, exist_ok=True)
    return task_path


def load_state(state_path: Path) -> dict:
    if state_path.exists():
        try:
            return json.loads(state_path.read_text())
        except Exception:
            pass
    return {
        "taskId": state_path.parent.name,
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
        "toolCalls": 0,
        "cumulativeChars": 0,
        "cumulativeEstimatedTokens": 0,
        "largeReads": 0,
        "largeOutputs": 0,
        "riskLevel": "low",
        "thresholdsCrossed": [],
        "lastTool": "",
        "lastLargeSource": "",
        "lastOversizedArtifact": "",
    }


def save_state(state_path: Path, state: dict) -> None:
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def calculate_risk(total_tokens: int) -> str:
    if total_tokens >= 100000:
        return "critical"
    if total_tokens >= 50000:
        return "high"
    if total_tokens >= 20000:
        return "medium"
    return "low"


def write_threshold_digest(task_path: Path, state: dict, label: str, prefix: str = "") -> None:
    digest_path = task_path / "recovery" / f"{prefix}threshold-{label}.md"
    if digest_path.exists():
        return
    project_line = f"- Project: {project_label()}\n" if project_label() else ""
    content = (
        f"# Threshold digest: {label}\n\n"
        f"- Time: {now_iso()}\n"
        f"- Task ID: {state.get('taskId', 'unknown')}\n"
        f"{project_line}"
        f"- Risk level: {state.get('riskLevel', 'low')}\n"
        f"- Tool calls: {state.get('toolCalls', 0)}\n"
        f"- Cumulative estimated tokens: {state.get('cumulativeEstimatedTokens', 0)}\n"
        f"- Large reads: {state.get('largeReads', 0)}\n"
        f"- Large outputs: {state.get('largeOutputs', 0)}\n"
        f"- Last tool: {state.get('lastTool', '')}\n"
        f"- Last large source: {state.get('lastLargeSource', '')}\n\n"
        "Рекомендация: использовать preview-first, chunked read и quarantine для больших выводов.\n"
    )
    digest_path.write_text(content)


def is_risk_tool(tool: str) -> bool:
    tool_lower = (tool or "").lower()
    markers = ["tavily", "exa", "mcp", "browser", "crawl", "extract"]
    return any(marker in tool_lower for marker in markers)


def build_preview(text: str, max_chars: int = PREVIEW_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    head = text[:half]
    tail = text[-half:]
    return (
        "# Oversized result preview\n\n"
        "Полный результат слишком большой и сохранён отдельно.\n\n"
        f"## Head\n{head}\n\n"
        f"## Tail\n{tail}\n"
    )


def write_oversized_artifacts(task_path: Path, tool: str, result_text: str, prefix: str = ""):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    tool_slug = slugify(tool)
    raw_path = task_path / "raw" / f"{prefix}{stamp}-{tool_slug}.txt"
    preview_path = task_path / "recovery" / f"{prefix}{stamp}-{tool_slug}-preview.md"
    raw_path.write_text(result_text)
    preview_path.write_text(build_preview(result_text))
    return raw_path, preview_path


def normalize_path(path_value: str) -> str:
    if not path_value:
        return ""
    path = Path(path_value).expanduser()
    return str(path.resolve()) if path.exists() else os.path.abspath(os.path.expanduser(path_value))


def is_broad_root(path_value: str) -> bool:
    normalized = normalize_path(path_value)
    if not normalized:
        return False
    if normalized in BROAD_ROOTS:
        return True
    home_desktop = str((Path.home() / "Desktop").resolve())
    return normalized == home_desktop


def classify_large_input(path_value: str, size_threshold_bytes: int = 200000):
    if not path_value:
        return None
    try:
        path = Path(path_value)
        if not path.exists() or not path.is_file():
            return None
        size = path.stat().st_size
        if size > size_threshold_bytes:
            return {
                "decision": "block",
                "reason": (
                    f"Файл слишком большой для полного чтения ({size} байт). "
                    "Используй preview-first, chunked read или targeted extraction."
                ),
                "sizeBytes": size,
                "path": str(path),
            }
        return {
            "decision": "allow",
            "sizeBytes": size,
            "path": str(path),
        }
    except Exception as exc:
        return {"decision": "allow", "error": str(exc)}


def classify_list_files(path_value: str, recursive: bool):
    if not recursive:
        return {"decision": "allow"}
    if is_broad_root(path_value):
        return {
            "decision": "block",
            "reason": (
                "Рекурсивный list_files по широкому workspace/root может вернуть слишком большой объём контекста. "
                "Сузь путь до конкретного проекта или отключи recursive."
            ),
            "path": normalize_path(path_value),
        }
    return {"decision": "allow"}


def classify_search_files(path_value: str, regex: str, file_pattern: str):
    regex = (regex or "").strip()
    file_pattern = (file_pattern or "").strip()
    if is_broad_root(path_value) and (regex in GENERIC_REGEXES or len(regex) < 3 or not file_pattern):
        return {
            "decision": "block",
            "reason": (
                "Слишком широкий search_files по root/широкому workspace. "
                "Сузь path, уточни regex и добавь file_pattern."
            ),
            "path": normalize_path(path_value),
            "regex": regex,
            "filePattern": file_pattern,
        }
    return {"decision": "allow"}


def classify_command(command: str, size_threshold_bytes: int = 200000):
    command = (command or "").strip()
    if not command:
        return {"decision": "allow"}

    if command.startswith("docker logs") and "--tail" not in command:
        return {
            "decision": "block",
            "reason": "Команда `docker logs` без `--tail` может выдать гигантский вывод. Используй `docker logs <container> --tail 100`.",
            "command": command,
        }

    parts = command.split()
    if len(parts) == 2 and parts[0] == "cat":
        target = parts[1]
        try:
            path = Path(target)
            if path.exists() and path.is_file():
                size = path.stat().st_size
                if size > size_threshold_bytes:
                    return {
                        "decision": "block",
                        "reason": (
                            f"Команда `cat` пытается вывести большой файл ({size} байт). "
                            "Используй `head`, `tail`, `grep` или chunked read."
                        ),
                        "path": str(path),
                        "sizeBytes": size,
                        "command": command,
                    }
                return {"decision": "allow", "path": str(path), "sizeBytes": size}
        except Exception as exc:
            return {"decision": "allow", "error": str(exc)}

    if re.match(r"^git\s+diff(\s|$)", command) and "--stat" not in command and "--name-only" not in command and " -- " not in command:
        return {
            "decision": "block",
            "reason": "Широкий `git diff` может вернуть слишком большой вывод. Используй `git diff --stat`, `git diff --name-only` или `git diff -- <path>`.",
            "command": command,
        }

    if re.match(r"^git\s+log\b", command) and (" -p" in command or " --patch" in command) and not re.search(r"(--max-count|-n)\s*\d+", command):
        return {
            "decision": "block",
            "reason": "`git log -p` без лимита может вернуть гигантский вывод. Добавь `-n <count>` или используй `--stat`/конкретный path.",
            "command": command,
        }

    return {"decision": "allow"}


def handle_pre_tool_use(payload: dict) -> int:
    pre = payload.get("preToolUse", {})
    tool = str(pre.get("tool") or "")
    params = pre.get("parameters", {}) or {}

    if tool == "read_file":
        path_value = params.get("path") or params.get("absolutePath") or ""
        result = classify_large_input(path_value)
        print(json.dumps(result or {"decision": "allow"}, ensure_ascii=False))
        return 0

    if tool == "list_files":
        path_value = params.get("path") or ""
        recursive = bool(params.get("recursive") or False)
        print(json.dumps(classify_list_files(path_value, recursive), ensure_ascii=False))
        return 0

    if tool == "search_files":
        path_value = params.get("path") or ""
        regex = str(params.get("regex") or "")
        file_pattern = str(params.get("file_pattern") or params.get("filePattern") or "")
        print(json.dumps(classify_search_files(path_value, regex, file_pattern), ensure_ascii=False))
        return 0

    if tool == "execute_command":
        command = str(params.get("command") or "")
        result = classify_command(command)
        print(json.dumps(result, ensure_ascii=False))
        return 0

    print(json.dumps({"decision": "allow"}, ensure_ascii=False))
    return 0


def handle_post_tool_use(payload: dict) -> int:
    post = payload.get("postToolUse", {})
    task_id = str(payload.get("taskId") or "unknown")
    tool = str(post.get("tool") or post.get("toolName") or "")
    result_text = to_text(post.get("result"))
    chars = len(result_text)
    lines = result_text.count("\n") + (1 if result_text else 0)
    byte_count = len(result_text.encode("utf-8"))
    estimated_tokens = estimate_tokens(result_text)
    prefix = project_slug_prefix()

    task_path = get_task_dir(task_id)
    state_path = task_path / "state.json"
    state = load_state(state_path)
    state["updatedAt"] = now_iso()
    state["toolCalls"] = int(state.get("toolCalls", 0)) + 1
    state["cumulativeChars"] = int(state.get("cumulativeChars", 0)) + chars
    state["cumulativeEstimatedTokens"] = int(state.get("cumulativeEstimatedTokens", 0)) + estimated_tokens
    state["lastTool"] = tool

    is_large_read = tool == "read_file" and chars >= 40000
    is_large_output = chars >= 50000 or estimated_tokens >= 12500
    oversized_risk_result = is_risk_tool(tool) and (
        chars >= OVERSIZED_RESULT_CHARS or estimated_tokens >= OVERSIZED_RESULT_TOKENS
    )

    if is_large_read:
        state["largeReads"] = int(state.get("largeReads", 0)) + 1
        state["lastLargeSource"] = tool

    if is_large_output:
        state["largeOutputs"] = int(state.get("largeOutputs", 0)) + 1
        state["lastLargeSource"] = tool

    artifact_path = ""
    preview_path = ""
    warning_message = ""
    if oversized_risk_result and result_text:
        raw_path, preview_file = write_oversized_artifacts(task_path, tool, result_text, prefix=prefix)
        artifact_path = str(raw_path)
        preview_path = str(preview_file)
        state["lastOversizedArtifact"] = artifact_path
        state["lastLargeSource"] = tool
        warning_message = (
            f"⚠️ Хук: результат инструмента {tool} слишком большой. "
            f"Сырой вывод сохранён в артефакт: {artifact_path}. "
            "Опирайся на preview/summary и избегай повторного полного чтения."
        )

    state["riskLevel"] = calculate_risk(int(state.get("cumulativeEstimatedTokens", 0)))

    crossed = set(state.get("thresholdsCrossed", []))
    total_tokens = int(state.get("cumulativeEstimatedTokens", 0))
    for threshold, label in THRESHOLDS:
        if total_tokens >= threshold and label not in crossed:
            crossed.add(label)
            write_threshold_digest(task_path, state, label, prefix=prefix)
    state["thresholdsCrossed"] = sorted(crossed)

    save_state(state_path, state)

    print(
        json.dumps(
            {
                "statePath": str(state_path),
                "riskLevel": state["riskLevel"],
                "chars": chars,
                "lines": lines,
                "bytes": byte_count,
                "estimatedTokens": estimated_tokens,
                "oversizedResult": oversized_risk_result,
                "artifactPath": artifact_path,
                "previewPath": preview_path,
                "warningMessage": warning_message,
            },
            ensure_ascii=False,
        )
    )
    return 0


def handle_pre_compact(payload: dict) -> int:
    pre = payload.get("preCompact", {})
    task_id = str(payload.get("taskId") or "unknown")
    task_path = get_task_dir(task_id)
    state_path = task_path / "state.json"
    state = load_state(state_path)
    prefix = project_slug_prefix()
    label = project_label()

    summary_path = task_path / "recovery" / f"{prefix}precompact-{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.md"
    project_line = f"- Project: {label}\n" if label else ""
    summary = (
        "# Context Guard Recovery Bundle\n\n"
        f"- Generated at: {now_iso()}\n"
        f"- Task ID: {task_id}\n"
        f"{project_line}"
        f"- Estimated tokens before compact: {pre.get('estimatedTokens', 'unknown')}\n"
        f"- Conversation length: {pre.get('conversationLength', 'unknown')}\n"
        f"- Risk level: {state.get('riskLevel', 'low')}\n"
        f"- Tool calls: {state.get('toolCalls', 0)}\n"
        f"- Cumulative chars: {state.get('cumulativeChars', 0)}\n"
        f"- Cumulative estimated tokens: {state.get('cumulativeEstimatedTokens', 0)}\n"
        f"- Large reads: {state.get('largeReads', 0)}\n"
        f"- Large outputs: {state.get('largeOutputs', 0)}\n"
        f"- Last tool: {state.get('lastTool', '')}\n"
        f"- Last large source: {state.get('lastLargeSource', '')}\n"
        f"- Last oversized artifact: {state.get('lastOversizedArtifact', '')}\n"
        f"- Thresholds crossed: {', '.join(state.get('thresholdsCrossed', [])) or 'none'}\n\n"
        "## Recovery guidance\n"
        "- После восстановления продолжай с последнего безопасного шага.\n"
        "- Для больших файлов и выводов используй preview-first / chunked read.\n"
        "- Если повторится рост контекста, избегай full-read и сохраняй raw output в артефакты.\n"
    )
    summary_path.write_text(summary)

    print(
        json.dumps(
            {
                "statePath": str(state_path),
                "summaryPath": str(summary_path),
                "riskLevel": state.get("riskLevel", "low"),
            },
            ensure_ascii=False,
        )
    )
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "missing command"}, ensure_ascii=False))
        return 1

    command = sys.argv[1]
    payload = json.load(sys.stdin)

    if command == "pre-tool-use":
        return handle_pre_tool_use(payload)
    if command == "post-tool-use":
        return handle_post_tool_use(payload)
    if command == "pre-compact":
        return handle_pre_compact(payload)

    print(json.dumps({"error": f"unknown command: {command}"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
