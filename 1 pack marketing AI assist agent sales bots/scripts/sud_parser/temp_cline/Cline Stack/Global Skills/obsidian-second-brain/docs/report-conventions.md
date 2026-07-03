# Obsidian Second Brain — Report Conventions

Этот файл задаёт единый стиль служебных отчётов в `wiki/meta/`.

## 1. Lint report
Файл: `wiki/meta/lint-report-YYYY-MM-DD.md`

Минимальные секции:
- Summary
- Errors
- Warnings
- Info
- Safe fixes applied
- Suggested manual fixes

## 2. Ingest report
Файл: `wiki/meta/ingest-report-YYYY-MM-DD.md`

Используй для батчевого ingest, когда обработано несколько источников.

Минимальные секции:
- Batch summary
- Sources processed
- Pages created
- Pages updated
- New entities
- New concepts
- Contradictions / gaps

## 3. Save report
Файл: `wiki/meta/save-report-YYYY-MM-DD.md`

Используй, когда save-back затрагивает несколько knowledge artifacts.

Минимальные секции:
- What was saved
- Pages created
- Pages updated
- Why it matters

## Общие правила
- отчёты должны быть короткими и reviewable;
- это operational artifacts, а не knowledge pages;
- отчёты не заменяют `wiki/log.md`, а дополняют его;
- если отчёт не нужен, не создавай его формально.
