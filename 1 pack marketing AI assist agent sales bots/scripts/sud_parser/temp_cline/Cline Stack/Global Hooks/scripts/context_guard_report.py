#!/usr/bin/env python3
"""Короткий diagnostics report по context guard / continuity hooks."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

BASE = Path.home() / "Documents" / "Cline" / "Logs"
CONTEXT_GUARD = BASE / "context-guard"
COMPACTION = BASE / "compaction"
TOOL_LOG = BASE / "tool-usage.log"
LEGACY_MARKER = COMPACTION / "needs_restore.json"
TASK_MARKER_DIR = COMPACTION / "by-task"
AMBIGUOUS_LOG = BASE / "context-guard-ambiguous.log"


def human_age(seconds: float) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}с"
    if seconds < 3600:
        return f"{seconds // 60}м {seconds % 60}с"
    return f"{seconds // 3600}ч {(seconds % 3600) // 60}м"


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def legacy_marker_section() -> str:
    lines = ["## Legacy restore marker"]
    if not LEGACY_MARKER.exists():
        lines.append("- Статус: отсутствует")
        return "\n".join(lines)

    data = load_json(LEGACY_MARKER) or {}
    age = human_age(time.time() - LEGACY_MARKER.stat().st_mtime)
    lines.extend([
        "- Статус: найден (legacy fallback)",
        f"- Возраст: {age}",
        f"- taskId: {data.get('taskId', '') or '—'}",
        f"- workspace: {data.get('workspace', '') or '—'}",
        f"- workspaceRealpath: {data.get('workspaceRealpath', '') or '—'}",
        f"- userId: {data.get('userId', '') or '—'}",
        f"- riskLevel: {data.get('riskLevel', '') or '—'}",
    ])
    return "\n".join(lines)


def task_marker_section(limit: int) -> str:
    lines = ["## Task-scoped restore markers"]
    if not TASK_MARKER_DIR.exists():
        lines.append("- Папка отсутствует")
        return "\n".join(lines)

    markers = sorted(TASK_MARKER_DIR.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    if not markers:
        lines.append("- Marker files не найдены")
        return "\n".join(lines)

    for path in markers:
        data = load_json(path) or {}
        age = human_age(time.time() - path.stat().st_mtime)
        lines.extend([
            f"### {path.name}",
            f"- taskId: {data.get('taskId', '') or '—'}",
            f"- userId: {data.get('userId', '') or '—'}",
            f"- workspaceRealpath: {data.get('workspaceRealpath', '') or data.get('workspace', '') or '—'}",
            f"- riskLevel: {data.get('riskLevel', '') or '—'}",
            f"- Возраст: {age}",
            f"- recoverySummaryPath: {data.get('recoverySummaryPath', '') or '—'}",
            "",
        ])
    return "\n".join(lines).rstrip()




def pulse_section() -> str:
    lines = ["## Pulse summary"]
    marker_count = len(list(TASK_MARKER_DIR.glob('*.json'))) if TASK_MARKER_DIR.exists() else 0
    lines.append(f"- Active task markers: {marker_count}")

    ambiguous_count = 0
    recent_ambiguous = []
    if AMBIGUOUS_LOG.exists():
        entries = AMBIGUOUS_LOG.read_text(errors='ignore').splitlines()
        ambiguous_count = len(entries)
        recent_ambiguous = entries[-3:]
    lines.append(f"- Ambiguous restore skips logged: {ambiguous_count}")

    states = sorted(CONTEXT_GUARD.glob('*/state.json'), key=lambda p: p.stat().st_mtime, reverse=True) if CONTEXT_GUARD.exists() else []
    high_risk = []
    for path in states[:20]:
        data = load_json(path) or {}
        risk = data.get('riskLevel', 'low')
        if risk in {'high', 'critical'}:
            high_risk.append(f"{path.parent.name}:{risk}:{data.get('cumulativeEstimatedTokens', '—')}")
    lines.append(f"- High-risk task states: {', '.join(high_risk[:5]) or 'none'}")

    if recent_ambiguous:
        lines.append('- Recent ambiguous restore events:')
        for entry in recent_ambiguous:
            lines.append(f"  - {entry}")

    return "\n".join(lines)

def latest_states(limit: int) -> str:
    lines = ["## Последние task state"]
    if not CONTEXT_GUARD.exists():
        lines.append("- Папка context-guard отсутствует")
        return "\n".join(lines)

    states = sorted(CONTEXT_GUARD.glob('*/state.json'), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    if not states:
        lines.append("- state.json не найдены")
        return "\n".join(lines)

    for path in states:
        data = load_json(path) or {}
        lines.extend([
            f"### {path.parent.name}",
            f"- updatedAt: {data.get('updatedAt', '—')}",
            f"- riskLevel: {data.get('riskLevel', '—')}",
            f"- toolCalls: {data.get('toolCalls', '—')}",
            f"- cumulativeEstimatedTokens: {data.get('cumulativeEstimatedTokens', '—')}",
            f"- lastTool: {data.get('lastTool', '') or '—'}",
            f"- thresholdsCrossed: {', '.join(data.get('thresholdsCrossed', [])) or 'none'}",
            f"- lastOversizedArtifact: {data.get('lastOversizedArtifact', '') or '—'}",
            "",
        ])
    return "\n".join(lines).rstrip()


def tool_log_section(lines_limit: int) -> str:
    lines = ["## Последние записи tool-usage.log"]
    if not TOOL_LOG.exists():
        lines.append("- Лог отсутствует")
        return "\n".join(lines)

    tail = TOOL_LOG.read_text(errors='ignore').splitlines()[-lines_limit:]
    if not tail:
        lines.append("- Лог пуст")
        return "\n".join(lines)

    lines.append("```text")
    lines.extend(tail)
    lines.append("```")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnostics report по context guard / continuity hooks")
    parser.add_argument('--limit', type=int, default=5, help='Сколько последних state.json/markers показывать')
    parser.add_argument('--tool-log-lines', type=int, default=10, help='Сколько последних строк tool-usage.log показывать')
    args = parser.parse_args()

    parts = [
        '# Context Guard Diagnostics Report',
        '',
        pulse_section(),
        '',
        legacy_marker_section(),
        '',
        task_marker_section(args.limit),
        '',
        latest_states(args.limit),
        '',
        tool_log_section(args.tool_log_lines),
    ]
    print('\n'.join(parts))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
