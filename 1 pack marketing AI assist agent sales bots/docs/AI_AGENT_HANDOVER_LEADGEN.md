# 🚀 Handover: AI Leadgen & WhatsApp Outreach Pipeline

> **Цель документа:** Передача контекста другому агенту (или партнеру) для старта разработки системы лидогенерации, обогащения и WhatsApp-рассылок (Nick Saraev style).

---

## 1. Стратегические Решения (Что обсудили)

### Данные и Парсинг (Конец эры парсинга групп)
*   **Проблема WhatsApp:** С 2024 года в Сообществах и новых группах скрыты номера пользователей. Парсинг через Evolution API (Baileys) возвращает мертвые алиасы (`@lid`), на которые нельзя делать холодные рассылки без жестких банов.
*   **Решение:** Мы берем лиды из **внешних B2B баз**. Для тестов (ниша Логистика) используются: Госзакупки (`goszakup.gov.kz`), 2ГИС, HH.ru, Adata.kz.
*   **Логгирование:** В Node.js используем `pino`, в Python — `loguru`. Логи пишем не на каждую строчку, а только на статусы (добавлен лид, отправлено, ошибка).

### База Данных (Архитектура)
*   **Supabase (PostgreSQL 500MB Free):** Главное, вечное хранилище (сырые лиды, логи отправок, статусы и черные списки). 500 МБ хватит на полмиллиона строк. n8n раз в 3 дня делает 'пинг', чтобы база не уснула.
*   **n8n Data Tables (Лимит 50MB):** Используем **только** как оперативную очередь на сегодня. Залили 50 лидов на день → разослали → назавтра очистили.
*   **Google Sheets:** Только для выгрузки ГОРЯЧИХ (ответивших) лидов для менеджера по продажам.

---

## 2. Пайплайн системы (Что строим)

Система разделена на 3 независимых этапа (микросервисная логика):

### Этап 1: Сбор сырых лидов (Парсинг)
*   **Инструмент:** Python-скрипты на VPS (или локально).
*   **Действие:** Скрипт обходит Госзакупки/HH/2ГИС по нужным критериям (например, тендеры на экспедиторские услуги).
*   **Слив данных:** Сохраняет результаты (Название компании, Отрасль, Телефон/Сайт) напрямую в таблицу `leads_raw` в Supabase.

### Этап 2: Обогащение баз (n8n + AI)
*   **Инструмент:** n8n Workflow.
*   **Действие:** n8n берет порцию (batch) сырых лидов из Supabase.
*   **Поиск инфы:** Через Perplexity/Tavily (или веб-скраппинг) AI изучает сайт компании или ее вакансии, чтобы понять "что у них болит".
*   **Генерация:** AI (Claude/Gemini) пишет **первое персональное сообщение** (Nick Saraev style) на основе данных компании. Текст сохраняется в БД `leads_enriched`.

### Этап 3: Умная рассылка (WhatsApp Evolution API)
*   **Инструмент:** n8n Workflow + Evolution API.
*   **Очередь:** n8n забирает 30-50 лидов на день из `leads_enriched` в свои внутренние Data Tables (для быстрой обработки очереди).
*   **Безопасность (Анти-бан):**
    *   **Задержки:** Случайные паузы от 30 до 120 секунд между отправками.
    *   **Ротация:** Шлем 30 сообщений с Номера №1 → 30 с Номера №2 → 30 с Номера №3 (до 90 уников/день).
    *   **Уникализация:** AI уже сгенерировал уникальный текст для каждого.
    *   **СТОП-слово:** Всегда даем кнопку или фразу для легкой отписки (если юзер пишет СТОП → Evolution Webhook ловит ответ → ставим статус `blacklisted` в Supabase).

---

## 3. План Действий (Next Steps для Агента)

Новый агент должен идти строго по этому алгоритму:

### 🔴 Спринт 1: Инфраструктура
1.  **Починить n8n-mcp связь (Блокер):** Текущему пользователю нужно в настройках редактора (MCP config) исправить ссылку на `https://n8n.aiconicvibe.store` и добавить API-ключ. Агент должен проверить, ушла ли 404 ошибка (tool: `n8n_health_check`).
2.  **Supabase:** Создать проект, настроить 3 таблицы: `leads`, `campaigns`, `messages`.

### 🟠 Спринт 2: Первый парсер (Хардкод)
1.  Написать Python-модуль для сбора компаний-заказчиков на транспортные услуги с портала Госзакупок (либо через 2ГИС демо-ключ).
2.  Написать функцию вставки этих данных в Supabase (PostgreSQL).

### 🟡 Спринт 3: Сборка в n8n
1.  Сделать n8n workflow обогащения через Tavily/OpenAI.
2.  Сделать n8n workflow рассылки:
    *   Trigger: Очередь или Cron
    *   Node: Evolution API (отправка сообщения)
    *   Logic: Sleep (30-120s) -> Переход к следующему номеру.
3.  Настроить Webhook от Evolution API обратно в n8n для трекинга ответов.

> 💡 **Файлы контекста в репозитории:** 
> - `KANBAN.md` (все задачи системы разложены по этапам)
> - `.clinerules` (лимиты отправок WhatsApp и правила кода)
> - `docs/WHATSAPP_PARSING_RULES.md` (документация: почему сбор номеров из групп больше не работает из-за LIDs).

---

## 4. Обновление от 2026-06-29 (Результаты и Решенные Проблемы)

### Победы (Wins):
1. **Успешный запуск пайплайна:** Пайплайн лидогенерации `daily_leadgen.py` успешно завершил обработку всех **79 лидов** (с hh.ru, hh.kz, adata.kz, threads.net).
2. **Интеграция ИИ и создание предложений:** Все лиды успешно обогащены персонализированными предложениями и драфтами сообщений (по Nick Saraev Outreach Strategy). Результаты сохранены в [leads_report.md](file:///Users/higherpower/Desktop/1_Active_Projects/2%20Ai_agents/1%20pack%20marketing%20AI%20assist%20agent%20sales%20bots/03_Marketing_and_Sales/daily_leads/2026-06-29/leads_report.md) и [leads_summary.csv](file:///Users/higherpower/Desktop/1_Active_Projects/2%20Ai_agents/1%20pack%20marketing%20AI%20assist%20agent%20sales%20bots/03_Marketing_and_Sales/daily_leads/2026-06-29/leads_summary.csv). Папка с детализированными офферами: [details](file:///Users/higherpower/Desktop/1_Active_Projects/2%20Ai_agents/1%20pack%20marketing%20AI%20assist%20agent%20sales%20bots/03_Marketing_and_Sales/daily_leads/2026-06-29/details).
3. **Отправка отчета:** Итоговый отчет об успешном запуске и собранной статистике успешно отправлен в Telegram.

### Проблемы и Решения (Issues & Solutions):
* **Проблема:** AIHubMix API выдал ошибку `403 insufficient_user_quota` (баланс аккаунта исчерпан). Пайплайн автоматически переключился на фоллбэк Vertex AI (Gemini 2.5 Flash), однако gRPC-клиент Vertex AI зависал бесконечно при некоторых запросах из-за отсутствия сетевых таймаутов, что останавливало весь пайплайн.
* **Решение:** 
  1. Вызов Vertex AI SDK был заменен на прямые HTTP-запросы через библиотеку `requests` с жестким таймаутом `timeout=25`.
  2. Проведена оптимизация: авторизация, генерация токена Google Cloud OAuth2, URL и заголовки теперь кэшируются на уровне модуля при первом вызове. Это убрало оверхед на повторный рефреш токенов для каждого лида, ускорив ИИ-анализ в несколько раз и предотвратив повторные зависания.

---

## 4. Update from 2026-06-29 (Results and Solved Issues) - English Translation

### Wins:
1. **Successful Pipeline Run:** The lead generation pipeline `daily_leadgen.py` completed successfully, processing all **79 leads** (from hh.ru, hh.kz, adata.kz, threads.net).
2. **AI Enrichment & Pitch Generation:** All leads were successfully enriched with personalized hooks and service pitches (Nick Saraev style). Output saved in [leads_report.md](file:///Users/higherpower/Desktop/1_Active_Projects/2%20Ai_agents/1%20pack%20marketing%20AI%20assist%20agent%20sales%20bots/03_Marketing_and_Sales/daily_leads/2026-06-29/leads_report.md) and [leads_summary.csv](file:///Users/higherpower/Desktop/1_Active_Projects/2%20Ai_agents/1%20pack%20marketing%20AI%20assist%20agent%20sales%20bots/03_Marketing_and_Sales/daily_leads/2026-06-29/leads_summary.csv). Detailed files located in: [details](file:///Users/higherpower/Desktop/1_Active_Projects/2%20Ai_agents/1%20pack%20marketing%20AI%20assist%20agent%20sales%20bots/03_Marketing_and_Sales/daily_leads/2026-06-29/details).
3. **Notification Sent:** A summary notification was successfully delivered via Telegram Bot API.

### Issues & Solutions:
* **Issue:** OpenAI/AIHubMix API returned a `403 insufficient_user_quota` (exhausted balance). The pipeline automatically fell back to Vertex AI (Gemini 2.5 Flash), but the Vertex AI gRPC SDK got stuck indefinitely on certain requests due to missing network timeouts, halting the pipeline.
* **Solution:**
  1. Replaced the Vertex AI SDK client with direct HTTP requests using the `requests` library and a strict `timeout=25` seconds.
  2. Optimized HTTP authentication: credentials generation, Google Cloud OAuth2 token refreshing, target URL, and headers are now cached at the module level on the first call. This eliminates token refresh overhead for subsequent leads, making the enrichment process multiple times faster and highly stable.

---

## 5. Обновление от 2026-07-13 (Восстановление стабильности и Тестирование)

### Победы (Wins):
1. **Защита от зависания сети:** Добавлен глобальный таймаут сокета (`socket.setdefaulttimeout(35)`) на уровне Python, что исключило бесконечное ожидание при сетевых сбоях на этапе ИИ-обогащения.
2. **Pre-flight проверка ключей OpenAI:** Скрипт `daily_leadgen.py` теперь автоматически тестирует ключ OpenAI/AIHubMix при запуске. Если ключ невалиден (ошибка 401), происходит моментальный переход на Vertex AI.
3. **Восстановление Playwright:** В виртуальное окружение установлены недостающие исполняемые файлы браузеров Playwright Chromium.
4. **Удобный отладочный режим:** Внедрен флаг `--quick` (ограничение запросов и лидов) во все скраперы и оркестратор, позволяющий совершать быструю сквозную отладку.
5. **Сквозной тест:** Полный запуск пайплайна (`run_pipeline.py --force --quick`) успешно отработал за 2 минуты: лиды собраны, обогащены по Vertex AI, отчет отправлен в Telegram.

### Issues & Solutions:
* **Проблема:** Пайплайн зависал из-за отсутствия сетевых таймаутов, а скрапер падал из-за отсутствия браузеров в Playwright.
* **Решение:** Прописаны глобальные сокет-таймауты в Python, в requests.post добавлен таймаут 25с, выполнена переустановка браузеров Playwright Chromium.
