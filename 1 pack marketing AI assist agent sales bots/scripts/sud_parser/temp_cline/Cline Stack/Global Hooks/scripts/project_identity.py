#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path

PROJECT_RE = re.compile(r'^\s*Проект:\s*(.+?)\s*$')


def resolve_realpath(path_value: str) -> str:
    if not path_value:
        return ""
    path = Path(path_value).expanduser()
    if path.exists():
        return str(path.resolve())
    return os.path.abspath(os.path.expanduser(path_value))


def clean_label(value: str) -> str:
    text = (value or "").strip()
    if text.startswith('`') and text.endswith('`') and len(text) >= 2:
        text = text[1:-1].strip()
    return text


def extract_project_label(path: Path) -> str:
    try:
        for line in path.read_text(errors='ignore').splitlines():
            match = PROJECT_RE.match(line)
            if match:
                return clean_label(match.group(1))
    except Exception:
        return ""
    return ""


def slugify(value: str) -> str:
    text = clean_label(value)
    if text.endswith('.md'):
        text = text[:-3]
    safe = []
    previous_dash = False
    for char in text.lower():
        if char.isalnum():
            safe.append(char)
            previous_dash = False
        else:
            if not previous_dash:
                safe.append('-')
                previous_dash = True
    slug = ''.join(safe).strip('-')
    return slug or 'workspace'


def main() -> int:
    workspace_arg = sys.argv[1] if len(sys.argv) > 1 else ''
    workspace = Path(workspace_arg).expanduser() if workspace_arg else Path.cwd()
    workspace_realpath = resolve_realpath(str(workspace))
    desktop_realpath = resolve_realpath(str(Path.home() / 'Desktop'))
    is_broad_root = bool(workspace_realpath and workspace_realpath == desktop_realpath)

    result = {
        'workspace': str(workspace),
        'workspaceRealpath': workspace_realpath,
        'isBroadRoot': is_broad_root,
        'projectLabel': '',
        'projectSlug': '',
        'projectIdentitySource': '',
        'projectIdentityPath': '',
        'foundExplicitHeader': False,
        'multipleRuleMarkers': False,
        'ruleMarkerPaths': [],
    }

    candidates = []
    clinerules_dir = workspace / '.clinerules'
    if clinerules_dir.is_dir():
        for path in sorted(clinerules_dir.glob('*.md')):
            label = extract_project_label(path)
            if label:
                candidates.append(('workspace-rule', path, label))
        if candidates:
            result['ruleMarkerPaths'] = [str(path) for _, path, _ in candidates]
            result['multipleRuleMarkers'] = len(candidates) > 1

    if not candidates:
        ordered_files = [
            ('implementation-plan-header', workspace / 'implementation_plan.md'),
            ('project-state-header', workspace / 'cline_docs' / 'project-state.md'),
            ('handoff-header', workspace / 'cline_docs' / 'handoff-summary.md'),
        ]
        for source, path in ordered_files:
            label = extract_project_label(path)
            if label:
                candidates.append((source, path, label))
                break

    if candidates:
        source, path, label = candidates[0]
        result['projectLabel'] = label
        result['projectSlug'] = slugify(label)
        result['projectIdentitySource'] = source
        result['projectIdentityPath'] = str(path)
        result['foundExplicitHeader'] = True
    else:
        fallback = Path(workspace_realpath).name if workspace_realpath else workspace.name
        fallback = fallback or 'workspace'
        result['projectLabel'] = fallback
        result['projectSlug'] = slugify(fallback)
        result['projectIdentitySource'] = 'workspace-basename-fallback'
        result['projectIdentityPath'] = workspace_realpath or str(workspace)

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
