#!/usr/bin/env python3
"""Deep smoke suite для Variant B hooks (task-scoped compaction restore)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

HOOKS_DIR = Path.home() / "Documents" / "Cline" / "Hooks"
PRECOMPACT = HOOKS_DIR / "PreCompact"
SESSIONSTART = HOOKS_DIR / "SessionStart"
COMPACTION_DIR = Path.home() / "Documents" / "Cline" / "Logs" / "compaction"
TASK_MARKER_DIR = COMPACTION_DIR / "by-task"
LEGACY_MARKER = COMPACTION_DIR / "needs_restore.json"
AMBIGUOUS_LOG = Path.home() / "Documents" / "Cline" / "Logs" / "context-guard-ambiguous.log"
TMP_ROOT = Path.home() / 'Documents' / 'Cline' / 'HookSmoke'


def run_hook(path: Path, payload: dict) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(path)], input=json.dumps(payload), text=True, capture_output=True)


def reset_tmp() -> None:
    if TMP_ROOT.exists():
        shutil.rmtree(TMP_ROOT)
    TMP_ROOT.mkdir(parents=True, exist_ok=True)


def clean_markers() -> None:
    TASK_MARKER_DIR.mkdir(parents=True, exist_ok=True)
    for path in TASK_MARKER_DIR.glob('smoke-vb-*.json'):
        path.unlink(missing_ok=True)
    LEGACY_MARKER.unlink(missing_ok=True)
    AMBIGUOUS_LOG.unlink(missing_ok=True)


def make_workspace(name: str) -> Path:
    root = TMP_ROOT / name
    (root / 'cline_docs').mkdir(parents=True, exist_ok=True)
    (root / 'wiki' / 'meta').mkdir(parents=True, exist_ok=True)
    (root / '.clinerules').mkdir(parents=True, exist_ok=True)
    project_label = f'{name}.md'
    (root / '.clinerules' / 'project.local.md').write_text(
        f'Проект: {project_label}\nЗавершённость: [██████████░░░░░] 70% — smoke\n'
    )
    (root / 'implementation_plan.md').write_text(
        f'Проект: {project_label}\nЗавершённость: [██████████░░░░░] 70% — smoke\n\n# Plan for {name}\n\nNext: do-{name}\n'
    )
    (root / 'cline_docs' / 'project-state.md').write_text(
        f'Проект: {project_label}\nЗавершённость: [██████████░░░░░] 70% — smoke\n\n# State for {name}\n\nNext exact step: continue-{name}\n'
    )
    (root / 'cline_docs' / 'handoff-summary.md').write_text(
        f'Проект: {project_label}\nЗавершённость: [██████████░░░░░] 70% — smoke\n\n# Handoff for {name}\n\nresume-{name}\n'
    )
    (root / 'wiki' / 'hot.md').write_text(f'# Hot {name}\n')
    (root / 'wiki' / 'meta' / 'current-focus.md').write_text(f'# Focus {name}\n')
    return root


def marker_path(task_id: str) -> Path:
    safe = ''.join(ch if ch.isalnum() or ch in '._-' else '_' for ch in task_id)
    return TASK_MARKER_DIR / f'{safe}.json'


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def case_single_session_exact_restore() -> str:
    ws = make_workspace('single-a')
    task_id = 'smoke-vb-single-a'
    pre = run_hook(PRECOMPACT, {
        'taskId': task_id,
        'userId': 'user-smoke',
        'workspacePath': str(ws),
        'preCompact': {'estimatedTokens': 1234, 'conversationLength': 12},
    })
    assert_true(pre.returncode == 0, 'PreCompact failed')
    assert_true(marker_path(task_id).exists(), 'Task marker was not created')
    sess = run_hook(SESSIONSTART, {
        'taskId': task_id,
        'userId': 'user-smoke',
        'workspacePath': str(ws),
        'workspaceRoots': [str(ws)],
    })
    assert_true(sess.returncode == 0, 'SessionStart failed')
    assert_true('ВОССТАНОВЛЕНИЕ ПОСЛЕ COMPACTION' in sess.stdout, 'Exact restore did not trigger')
    assert_true(not marker_path(task_id).exists(), 'Task marker was not consumed after restore')
    return 'exact task restore ok'


def case_dual_workspace_isolation() -> str:
    ws_a = make_workspace('dual-a')
    ws_b = make_workspace('dual-b')
    task_a = 'smoke-vb-dual-a'
    task_b = 'smoke-vb-dual-b'
    for task_id, ws in [(task_a, ws_a), (task_b, ws_b)]:
        pre = run_hook(PRECOMPACT, {
            'taskId': task_id,
            'userId': 'user-smoke',
            'workspacePath': str(ws),
            'preCompact': {'estimatedTokens': 2100, 'conversationLength': 21},
        })
        assert_true(pre.returncode == 0, f'PreCompact failed for {task_id}')
    sess_a = run_hook(SESSIONSTART, {'taskId': task_a, 'userId': 'user-smoke', 'workspacePath': str(ws_a)})
    sess_b = run_hook(SESSIONSTART, {'taskId': task_b, 'userId': 'user-smoke', 'workspacePath': str(ws_b)})
    assert_true('dual-a.md' in sess_a.stdout and 'dual-b.md' not in sess_a.stdout, 'Workspace A restore polluted by workspace B')
    assert_true('dual-b.md' in sess_b.stdout and 'dual-a.md' not in sess_b.stdout, 'Workspace B restore polluted by workspace A')
    return 'different workspaces isolated'


def case_same_workspace_two_tasks() -> str:
    ws = make_workspace('same-ws')
    task_a = 'smoke-vb-same-a'
    task_b = 'smoke-vb-same-b'
    for task_id in [task_a, task_b]:
        pre = run_hook(PRECOMPACT, {
            'taskId': task_id,
            'userId': 'user-smoke',
            'workspacePath': str(ws),
            'preCompact': {'estimatedTokens': 3200, 'conversationLength': 32},
        })
        assert_true(pre.returncode == 0, f'PreCompact failed for {task_id}')
    sess_a = run_hook(SESSIONSTART, {'taskId': task_a, 'userId': 'user-smoke', 'workspacePath': str(ws)})
    assert_true('ВОССТАНОВЛЕНИЕ ПОСЛЕ COMPACTION' in sess_a.stdout, 'Task A did not restore')
    assert_true(marker_path(task_b).exists(), 'Task B marker should remain after task A restore')
    sess_b = run_hook(SESSIONSTART, {'taskId': task_b, 'userId': 'user-smoke', 'workspacePath': str(ws)})
    assert_true('ВОССТАНОВЛЕНИЕ ПОСЛЕ COMPACTION' in sess_b.stdout, 'Task B did not restore')
    return 'same workspace different taskId restore ok'


def case_ambiguous_without_taskid() -> str:
    ws = make_workspace('ambiguous-ws')
    task_a = 'smoke-vb-ambiguous-a'
    task_b = 'smoke-vb-ambiguous-b'
    for task_id in [task_a, task_b]:
        pre = run_hook(PRECOMPACT, {
            'taskId': task_id,
            'userId': 'user-smoke',
            'workspacePath': str(ws),
            'preCompact': {'estimatedTokens': 4100, 'conversationLength': 41},
        })
        assert_true(pre.returncode == 0, f'PreCompact failed for {task_id}')
    sess = run_hook(SESSIONSTART, {'workspacePath': str(ws)})
    assert_true('СОСТОЯНИЕ ПРОЕКТА' in sess.stdout, 'Should fall back to project continuity when taskId missing')
    assert_true('ВОССТАНОВЛЕНИЕ ПОСЛЕ COMPACTION' not in sess.stdout, 'Unsafe restore triggered without taskId in ambiguous scenario')
    assert_true('ambiguous' in sess.stderr.lower(), 'Expected ambiguous marker warning in stderr')
    return 'ambiguous same-workspace without taskId safely skipped'


def case_stale_marker_cleanup() -> str:
    ws = make_workspace('stale-ws')
    task_id = 'smoke-vb-stale-a'
    pre = run_hook(PRECOMPACT, {
        'taskId': task_id,
        'userId': 'user-smoke',
        'workspacePath': str(ws),
        'preCompact': {'estimatedTokens': 5100, 'conversationLength': 51},
    })
    assert_true(pre.returncode == 0, 'PreCompact failed')
    marker = marker_path(task_id)
    assert_true(marker.exists(), 'Stale test marker missing')
    old = time.time() - 50000
    os.utime(marker, (old, old))
    sess = run_hook(SESSIONSTART, {'taskId': 'different-task', 'workspacePath': str(ws)})
    assert_true('СОСТОЯНИЕ ПРОЕКТА' in sess.stdout, 'Should fall back to project continuity after stale cleanup')
    assert_true(not marker.exists(), 'Stale marker should be removed during cleanup')
    return 'stale task marker cleanup ok'


def case_ambiguous_logging() -> str:
    ws = make_workspace('ambiguous-log')
    task_a = 'smoke-vb-ambiguous-log-a'
    task_b = 'smoke-vb-ambiguous-log-b'
    for task_id in [task_a, task_b]:
        pre = run_hook(PRECOMPACT, {
            'taskId': task_id,
            'userId': 'user-smoke',
            'workspacePath': str(ws),
            'preCompact': {'estimatedTokens': 7100, 'conversationLength': 71},
        })
        assert_true(pre.returncode == 0, f'PreCompact failed for {task_id}')
    sess = run_hook(SESSIONSTART, {'workspacePath': str(ws)})
    assert_true('СОСТОЯНИЕ ПРОЕКТА' in sess.stdout, 'Expected project continuity fallback')
    assert_true(AMBIGUOUS_LOG.exists(), 'Ambiguous restore log was not created')
    content = AMBIGUOUS_LOG.read_text(errors='ignore')
    assert_true('multiple-candidates-for-workspace' in content, 'Ambiguous restore reason not logged')
    return 'ambiguous restore logging ok'


def case_user_mismatch_guard() -> str:
    ws = make_workspace('user-guard')
    task_id = 'smoke-vb-user-guard-a'
    pre = run_hook(PRECOMPACT, {
        'taskId': task_id,
        'userId': 'user-a',
        'workspacePath': str(ws),
        'preCompact': {'estimatedTokens': 6100, 'conversationLength': 61},
    })
    assert_true(pre.returncode == 0, 'PreCompact failed')
    sess = run_hook(SESSIONSTART, {'taskId': task_id, 'userId': 'user-b', 'workspacePath': str(ws)})
    assert_true('СОСТОЯНИЕ ПРОЕКТА' in sess.stdout, 'Should fall back when userId mismatches')
    assert_true('ВОССТАНОВЛЕНИЕ ПОСЛЕ COMPACTION' not in sess.stdout, 'Unsafe restore triggered on user mismatch')
    return 'user mismatch guard ok'


def case_prefixed_recovery_and_handoff() -> str:
    ws = make_workspace('prefix-handoff')
    task_id = 'smoke-vb-prefix-handoff'
    pre = run_hook(PRECOMPACT, {
        'taskId': task_id,
        'userId': 'user-smoke',
        'workspacePath': str(ws),
        'preCompact': {'estimatedTokens': 8100, 'conversationLength': 81},
    })
    assert_true(pre.returncode == 0, 'PreCompact failed')
    marker = marker_path(task_id)
    data = json.loads(marker.read_text())
    summary_path = Path(data.get('recoverySummaryPath', ''))
    assert_true(data.get('projectLabel') == 'prefix-handoff.md', 'Project label metadata missing in marker')
    assert_true(summary_path.exists(), 'Recovery summary file missing')
    assert_true(summary_path.name.startswith('prefix-handoff__precompact-'), 'Recovery summary is not prefixed with project slug')
    sess = run_hook(SESSIONSTART, {'taskId': task_id, 'userId': 'user-smoke', 'workspacePath': str(ws)})
    assert_true('prefix-handoff.md / cline_docs/handoff-summary.md' in sess.stdout, 'Handoff block not present in restored continuity')
    assert_true('resume-prefix-handoff' in sess.stdout, 'Handoff content missing in restored continuity')
    return 'prefixed recovery artifact and handoff continuity ok'


def main() -> int:
    reset_tmp()
    clean_markers()
    cases = [
        ('single-session exact restore', case_single_session_exact_restore),
        ('dual-window different workspace', case_dual_workspace_isolation),
        ('same workspace different taskId', case_same_workspace_two_tasks),
        ('ambiguous without taskId', case_ambiguous_without_taskid),
        ('stale marker cleanup', case_stale_marker_cleanup),
        ('ambiguous logging', case_ambiguous_logging),
        ('user mismatch guard', case_user_mismatch_guard),
        ('prefixed recovery and handoff', case_prefixed_recovery_and_handoff),
    ]

    results = []
    failed = False
    for name, fn in cases:
        clean_markers()
        try:
            details = fn()
            results.append((name, 'PASS', details))
        except Exception as exc:
            failed = True
            results.append((name, 'FAIL', str(exc)))

    print('# Variant B Smoke Suite')
    print()
    for name, status, details in results:
        icon = '✅' if status == 'PASS' else '❌'
        print(f'- {icon} {name}: {details}')
    print()
    print(f'Итог: {sum(1 for _, s, _ in results if s == "PASS")}/{len(results)} PASS')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
