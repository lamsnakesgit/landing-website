# Анализ ролика sen sulu

- Сохранен в файле: /Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 content factory audio/sen_sulu_analysis.md
## Изменения
- Проанализировано рекламное видео 'sen sulu' (Контуринг-стик / Бронзер).
- Создана детальная раскадровка и промпты для воссоздания сцен видео.
- Результаты анализа сохранены в `sen_sulu_analysis.md`.

## Успехи
- Успешно извлечены кадры из видео с помощью FFmpeg для проведения детального анализа визуального стиля и композиции.
- Составлены точные промпты для генеративных нейросетей (Midjourney/Stable Diffusion/Sora/Runway/Luma и т.д.) для воссоздания 1 в 1.

## Возможные проблемы / Issues
* **Forbidden Models (Do Not Use)**:
    - `gemini-1.5-flash`: Returns 404 in `v1beta` endpoint.
    - `gemini-2.0-flash`: Restricted for new users/specific regions, causes 403/404.
    - `gemini-2.0-flash-lite-preview-02-05`: Unstable or missing in current SDK version.
* **Working Models (Verified 2026-04-07)**:
    - `gemini-2.5-flash`
    - `gemini-2.5-pro`
    - `gemini-flash-latest`
    - `nano-banana-pro-preview` (for images)

## Настройка Cline (Professional Setup)
- Создана структура навыков в `.cline/skills/`.
- Добавлен навык `supabase-integration` для безопасной работы с БД.
- Добавлен навык `n8n-workflow-patterns` для стандартизации автоматизаций.
- Добавлен навык `systematic-debugging` для системного поиска багов.
- Настроен Hook `TaskStart` для автоматического чтения `docs/log.md` при старте задачи.
- Подготовлены рекомендации по настройке MCP (Postgres, Sequential Thinking, n8n).

## Duplicate in Russian
Все описанные успехи и изменения выполнены. Настройка Cline завершена.

## Update 2026-04-12
- Added `docs/N8N_AI_DEBUG_GUIDE.md` with a practical guide for debugging n8n Telegram AI assistants and AI agents.
- Documented a step-by-step workflow for inspecting raw LLM output, normalizing final text, and preventing reasoning/debug leakage into Telegram replies.

## Update 2026-04-14
- Added `docs/OPEN_NOTEBOOK_MINDMAP_PLAN_RU.md` with a practical recommendation for choosing a prompt-driven mind map workflow.
- Documented why NotebookLM is useful as a research layer, but recommended LLM + Markmap/Mermaid/XMind as the main solution for custom mind maps by prompt.

## Update 2026-04-16 (Carousel Bot MVP)
- Started development of Carousel Bot MVP (AI Carousel Generator via Telegram).
- Created `docs/CAROUSEL_BOT_PLAN.md` with architecture, database strategy (trial, limits) and force-subscribe monetization plan.
- Initialized `carousel_bot/` structure.
