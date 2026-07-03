#!/usr/bin/env bash
        # Скрипт создаёт минимальную структуру Obsidian second brain vault под Cline + mcp-obsidian.

        set -euo pipefail

        VAULT_PATH="${1:-}"
        if [[ -z "$VAULT_PATH" ]]; then
          echo "Usage: scaffold_vault.sh /absolute/path/to/vault" >&2
          exit 1
        fi

        VAULT_PATH="$(python3 - <<'INNERPY' "$VAULT_PATH"
import os, sys
print(os.path.abspath(os.path.expanduser(sys.argv[1])))
INNERPY
)"

        SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
        TODAY="$(date +%F)"
        NOW="$(date +%FT%T)"
        VAULT_NAME="$(basename "$VAULT_PATH")"

        mkdir -p "$VAULT_PATH/raw/assets"
        mkdir -p "$VAULT_PATH/wiki/sources"
        mkdir -p "$VAULT_PATH/wiki/entities"
        mkdir -p "$VAULT_PATH/wiki/concepts"
        mkdir -p "$VAULT_PATH/wiki/comparisons"
        mkdir -p "$VAULT_PATH/wiki/questions"
        mkdir -p "$VAULT_PATH/wiki/meta"
        mkdir -p "$VAULT_PATH/output"

        copy_if_missing() {
          local src="$1"
          local dst="$2"
          if [[ ! -f "$dst" ]]; then
            mkdir -p "$(dirname "$dst")"
            cp "$src" "$dst"
          fi
        }

        copy_if_missing "$SKILL_DIR/templates/vault/wiki/index.md" "$VAULT_PATH/wiki/index.md"
        copy_if_missing "$SKILL_DIR/templates/vault/wiki/log.md" "$VAULT_PATH/wiki/log.md"
        copy_if_missing "$SKILL_DIR/templates/vault/wiki/hot.md" "$VAULT_PATH/wiki/hot.md"
        copy_if_missing "$SKILL_DIR/templates/vault/wiki/overview.md" "$VAULT_PATH/wiki/overview.md"
        copy_if_missing "$SKILL_DIR/templates/vault/wiki/meta/current-focus.md" "$VAULT_PATH/wiki/meta/current-focus.md"
        copy_if_missing "$SKILL_DIR/templates/vault/wiki/meta/lint-report-template.md" "$VAULT_PATH/wiki/meta/lint-report-template.md"
        copy_if_missing "$SKILL_DIR/templates/vault/wiki/meta/ingest-report-template.md" "$VAULT_PATH/wiki/meta/ingest-report-template.md"
        copy_if_missing "$SKILL_DIR/templates/vault/wiki/meta/save-report-template.md" "$VAULT_PATH/wiki/meta/save-report-template.md"
        copy_if_missing "$SKILL_DIR/templates/vault/wiki/sources/_template.md" "$VAULT_PATH/wiki/sources/_template.md"
        copy_if_missing "$SKILL_DIR/templates/vault/wiki/entities/_template.md" "$VAULT_PATH/wiki/entities/_template.md"
        copy_if_missing "$SKILL_DIR/templates/vault/wiki/concepts/_template.md" "$VAULT_PATH/wiki/concepts/_template.md"
        copy_if_missing "$SKILL_DIR/templates/vault/wiki/questions/_template.md" "$VAULT_PATH/wiki/questions/_template.md"
        copy_if_missing "$SKILL_DIR/templates/vault/wiki/comparisons/_template.md" "$VAULT_PATH/wiki/comparisons/_template.md"

        if [[ ! -f "$VAULT_PATH/CLAUDE.md" ]]; then
          python3 - <<'INNERPY' "$SKILL_DIR/templates/vault/CLAUDE.md" "$VAULT_PATH/CLAUDE.md" "$VAULT_NAME" "$TODAY"
from pathlib import Path
import sys
src = Path(sys.argv[1]).read_text()
out = src.replace('{{VAULT_NAME}}', sys.argv[3]).replace('{{PURPOSE}}', 'TODO: describe vault purpose').replace('{{DATE}}', sys.argv[4])
Path(sys.argv[2]).write_text(out)
INNERPY
        fi

        python3 - <<'INNERPY' "$VAULT_PATH/wiki/index.md" "$VAULT_PATH/wiki/log.md" "$VAULT_PATH/wiki/hot.md" "$VAULT_PATH/wiki/overview.md" "$VAULT_PATH/wiki/meta/current-focus.md" "$TODAY" "$NOW"
from pathlib import Path
import sys
replacements = [
    ('YYYY-MM-DDTHH:MM:SS', sys.argv[7]),
    ('YYYY-MM-DD', sys.argv[6]),
]
for file_path in sys.argv[1:6]:
    p = Path(file_path)
    text = p.read_text()
    for old, new in replacements:
        text = text.replace(old, new)
    p.write_text(text)
INNERPY

        echo "Vault scaffolded at: $VAULT_PATH"
        echo "Next steps:"
        echo "1. Fill in CLAUDE.md purpose and domain specifics"
        echo "2. Point mcp-obsidian to this vault"
        echo "3. Drop sources into raw/ and start ingest"
