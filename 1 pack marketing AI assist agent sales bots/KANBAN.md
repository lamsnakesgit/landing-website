# 📋 KANBAN — AI Outreach & Sales System

> Последнее обновление: 2026-04-15
> Правило: Cline/агент ПЕРЕД работой берёт 1 задачу → In Progress → по завершении → Done

---

## 🔴 Backlog

### Инфраструктура
- [ ] `INFRA-01` Проверить/починить n8n инстанс на VPS (404 ошибка)
- [ ] `INFRA-02` Настроить SSH + tmux на VPS для мобильной работы
- [ ] `INFRA-03` Установить Cline CLI на VPS
- [ ] `INFRA-04` Проверить Evolution API инстансы (3 шт), подключённые номера
- [x] `INFRA-05` Настроить Supabase: таблицы leads, messages, campaigns + RLS — Завершено: 2026-04-19

### Парсинг лидов
- [ ] `PARSE-01` Зарегать демо-ключ 2ГИС API (platform.2gis.ru)
- [ ] `PARSE-02` Python парсер: 2ГИС → логистика/грузоперевозки (Алматы)
- [ ] `PARSE-03` Зарегать приложение HH.ru API (dev.hh.ru)
- [ ] `PARSE-04` Python парсер: HH.ru → компании ищущие маркетологов/РОП
- [ ] `PARSE-05` Интеграция Adata.kz — проверка размера компании, налоги
- [ ] `PARSE-06` WA группы → извлечь участников через Evolution API (findGroupMembers)
- [ ] `PARSE-07` Фильтрация участников групп по описанию/категориям (AI)

### Обогащение
- [ ] `ENRICH-01` n8n workflow: новый лид → Tavily/Perplexity → AI анализ → Supabase
- [ ] `ENRICH-02` Скоринг лидов (AI score 1-10 по релевантности)
- [ ] `ENRICH-03` Генерация персонализированных первых сообщений (Nick Saraev стиль)

### Рассылка WhatsApp
- [ ] `WA-02` Цепочка follow-up (день 0, +1, +3, +7)
- [ ] `WA-04` Обработка статусов: СТОП / отписка → не слать больше
- [ ] `WA-05` Webhook трекинг: delivered/read/reply → Supabase

### Аналитика
- [ ] `DASH-01` Простой dashboard: воронка отправлено→доставлено→прочитано→ответ
- [ ] `DASH-02` Канбан статусов лидов (new/contacted/replied/qualified/dead)
- [ ] `DASH-03` AI auto-research: еженедельный анализ конверсий
- [ ] `DASH-04` Telegram уведомления: ответы, ошибки, конверсия за день

### B2B продажи (своих решений)
- [ ] `B2B-01` Сформулировать 1 чёткий оффер (OKK + AI + автоматизация)
- [ ] `B2B-02` Парсинг целевых компаний с HH.ru (средние, 50-500 чел)
- [ ] `B2B-03` Первые 10 персонализированных сообщений вручную
- [ ] `B2B-04` Скрипт для себя: автоматизация B2B аутрича

### Контент / Медиа
- [ ] `MEDIA-01` Шаблоны картинок для цепочек (инфографика, кейсы)
- [ ] `MEDIA-02` Carousel generator workflow (Gemini) — дофиксить

---

## 🟡 In Progress

<!-- Агент берёт задачу отсюда, переносит из Backlog -->
<!-- Формат: - [/] `ID` Описание — Начато: YYYY-MM-DD -->

- [/] `HERMES-01` Архитектура Hermes Telegram Assistant (личный + бизнес ассистент с памятью, мультимодальностью и интеграциями) — Начато: 2026-05-16
- [/] `INFRA-07` Установить и подключить MCP servers для Cline (Vapi / Exa / GitHub / Context7) — Начато: 2026-05-14

### Прогресс по активным задачам
- `HERMES-01`: проведён быстрый аудит существующих Telegram / Fathom / memory / summary артефактов в репозитории; подтверждено, что лучший путь — Hermes как Telegram-facing ассистент, n8n как orchestration/integration слой, Supabase как память и база артефактов — Обновлено: 2026-05-16
- `INFRA-07`: подключён Exa MCP server (`github.com/exa-labs/exa-mcp-server`) в `cline_mcp_settings.json`, создана локальная папка `/Users/higherpower/Documents/Cline/MCP/github.com/exa-labs/exa-mcp-server`, выполнен тест инструмента Exa search — Обновлено: 2026-05-14
- `INFRA-07`: добавлены `github.com/github/github-mcp-server` и `github.com/upstash/context7` в `cline_mcp_settings.json`, созданы локальные директории под оба MCP, GitHub token убран из JSON и переведён на runtime-чтение через `gh auth token`, Context7 smoke test успешен, GitHub MCP требует запущенный Docker daemon — Обновлено: 2026-05-15
- [/] `N8N-03` Telegram Meeting Assistant MVP workflow (text + voice + audio + m4a) — Начато: 2026-04-15
- [/] `WA-01/WA-03` Модуль Умной Рассылки Python (Очередь + Ротация) — Начато: 2026-04-18
- [/] `WA-05` Webhook трекинг: delivered/read/reply → Supabase — Начато: 2026-05-14
- [/] `INFRA-06` Remote Sync & Smart Fortress VPS Setup — Начато: 2026-04-19
- [/] `POS-01` Личная Операционная Система (Personal OS) — Начато: 2026-05-14
- [/] `COP-02` AI Sales Copilot 2.0 (TG Userbot + Voice) — Начато: 2026-05-14

---

## 🟢 Done

<!-- Формат: - [x] `ID` Описание — Завершено: YYYY-MM-DD -->
- [x] `PLAN-01` Стратегический план Outreach Pipeline — Завершено: 2026-04-15
- [x] `N8N-04` Копирование воркфлоу Zoom Call Summary и интеграция Telegram-бота с Whisper STT — Завершено: 2026-05-23
- [x] `PLAN-02` Глоссарий AI-концепций (Specs/API/MCP/Skills/Workflows/Rules/Subagents) — Завершено: 2026-04-15
- [x] `PLAN-03` Создание KANBAN.md — Завершено: 2026-04-15
- [x] `STRUCT-01` Реструктуризация проекта на 6 доменов — Завершено: 2026-04-12
- [x] `N8N-01` tg_to_whatsapp.json workflow — Завершено: 2026-04-12
- [x] `N8N-02` gemini_carousel_generator.json — Завершено: 2026-04-12
- [x] `INFRA-05` Настройка Supabase (SQL схемы + Smoke Test) — Завершено: 2026-04-19

---

## 📊 Приоритеты

| Приоритет | Задачи | Почему |
|:---|:---|:---|
| 🔴 Сейчас | INFRA-01, INFRA-04, PARSE-01, PARSE-06 | Без инфры и данных ничего не работает |
| 🟠 Эта неделя | INFRA-05, ENRICH-01, WA-01 | Первый рабочий pipeline |
| 🟡 След. неделя | WA-02, WA-05, DASH-01, B2B-01 | Аналитика + продажи |
| 🟢 Позже | B2B-02, DASH-03, MEDIA-01 | Масштабирование |
