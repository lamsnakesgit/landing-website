# PROGRESS
Отслеживание новых фич и завершенных модулей в проекте.

## 2026-05-25
- [x] Переписана стратегия `smm_brand_ai/plan.md`: фокус смещён с одного AI-сериала на общую систему роста блога, удержания аудитории и монетизации через платформы, бренды, клиентов, продукты и услуги.
- [x] Обновлён `smm_brand_ai/storyboard_plan.md`: вместо storyboard под отдельный сериал зафиксирован 7-дневный план контент-системы с охватным, удерживающим и коммерческим слоями.
- [x] Проверено, что в новых документах явно отражены ключевые направления: вирусный контент, удержание, платформенная монетизация, B2B-монетизация, бренды, клиенты и быстрые заявки.
- [x] Проведён внешний research через Exa по реальным контент-заводам и viral media моделям: MrBeast / Rohan Kumar, Duolingo TikTok, Liquid Death, Red Bull Media House, Alex Hormozi / GaryVee. Tavily deep research дважды ушёл в timeout, поэтому источником для синтеза стали Exa-результаты.
- [x] Усилены `smm_brand_ai/plan.md` и `smm_brand_ai/storyboard_plan.md`: добавлены референсные модели, алгоритмическая структура серии, 5 запусковых серий, шаблон выпуска 0–45 секунд, матрица проверки ролика и коммерческие мосты к услугам/продуктам.
- [x] Доработана первая серия `smm_brand_ai/content_series/episode_1_counter_bake.md` до production-ready storyboard: кризис с арендой СТО, Баке ставит дедлайн на 1 млн ₸, Макс запускает AI-коллектора, деньги приходят, Баке повышает ставку до 2 млн ₸. Добавлены 5 сцен, реплики, экранные тексты, SFX, промпты Flux/NanoBanana, промпты Google Veo и монтажные указания.

## 2026-04-12
- [x] Реструктуризация рабочей директории: созданы `01_AI_Agents_and_Bots`, `02_Web_Projects`, `03_Marketing_and_Sales`, `04_Design_and_Media`, `05_N8N_Automations`, `06_Scripts_and_Tools`. Код, скрипты и документация распределены по папкам.
- [x] Создан новый n8n workflow: `tg_to_whatsapp.json` с использованием Evolution API и конвертацией медиа.

## 2026-04-15
- [x] Создан новый n8n workflow-шаблон: `05_N8N_Automations/n8n_templates/telegram_meeting_assistant_mvp.json`.
- [x] В workflow заложен Telegram intake для `text`, `voice`, `audio`, `document audio` (`.m4a/.mp3/.wav/.aac/.ogg`).
- [x] Добавлена цепочка из 3 AI-блоков: `Meeting Structurer` → `Sales Analyst` → `Content Repurposer`.
- [x] Добавлен Whisper STT шаг для голосовых и аудиофайлов.
- [x] Шаблон подготовлен как MVP-основа под дальнейшее расширение до `video/video_note` и `Fathom webhook`.

## 2026-05-14
- [x] Найден и частично исправлен шаблон `n8n_templates/WhatsApp_Summary_Agent_Evolution_API.json`.
- [x] Для webhook-ноды `Evolution Webhook` добавлен явный `httpMethod: POST`, чтобы входящие события от Evolution API корректно принимались n8n.
- [x] Подготовлен минимальный фикс под проблему "webhook не триггерится на сообщения".
- [x] Добавлена поддержка обычных текстовых сообщений из групп через новую ветку `Extract Text Message`.
- [x] Установлен и подключён Exa MCP server с именем `github.com/exa-labs/exa-mcp-server` для Cline.
- [x] Сохранён существующий MCP-конфиг без перезаписи сервера Vapi, добавлен новый сервер в `cline_mcp_settings.json`.
- [x] Создана локальная директория `/Users/higherpower/Documents/Cline/MCP/github.com/exa-labs/exa-mcp-server` под новый MCP.
- [x] Подтверждена работоспособность Exa через тестовый вызов инструмента `web_search_exa`.
- [x] OpenClaw не выбрасывать, но держать как отдельную future-ветку под swarm, chat-monitoring, dashboards или multi-agent routing, если Hermes Core станет узким местом.

## 2026-05-15
- [x] В `cline_mcp_settings.json` добавлены MCP servers `github.com/github/github-mcp-server` и `github.com/upstash/context7` без перезаписи уже существующих Vapi / Exa / Tavily.
- [x] Созданы локальные директории `/Users/higherpower/Documents/Cline/MCP/github.com/github/github-mcp-server` и `/Users/higherpower/Documents/Cline/MCP/github.com/upstash/context7`.
- [x] Для GitHub MCP выбран запуск через Docker с runtime-получением токена из `gh auth token`, чтобы не хранить GitHub token открыто в JSON-конфиге.
- [x] Для Context7 выбран локальный запуск через `npx -y @upstash/context7-mcp` без API key на первом этапе.
- [x] Подтверждён smoke test Context7 через вывод `--help`.
- [x] Выявлено ограничение GitHub MCP: Docker установлен, но локальный Docker daemon не был запущен во время проверки.

## 2026-05-16
- [x] Проведён аудит существующих наработок по Telegram assistant, Fathom post-meeting flow, памяти/RAG и интеграциям.
- [x] Зафиксировано целевое решение для Hermes: Telegram как основной интерфейс, n8n как orchestration-слой, Supabase как память и база артефактов.
- [x] Подтверждено, что уже есть хорошие заготовки для MVP: `telegram_meeting_assistant_mvp.json`, `zoom_fathom_assistant_spec.md`, шаблоны summary/audio flows и паттерны chat memory.
- [x] Определено, что мониторинг групп/ЛС лучше выносить в отдельный агентный контур, а не перегружать основной личный поток Hermes.
- [x] Проведён внешний research по Hermes docs / GitHub / community guides и сопоставление с OpenClaw.
- [x] Подтверждено, что Hermes лучше ложится на сценарий личного и бизнес-ассистента с памятью, Telegram, cron, MCP и growth-through-skills.
- [/] `HERMES-SETUP` Подготовка к развёртыванию Hermes на VPS (Личный + Outreach).

- [x] Зафиксировано решение, что tracking стоимости моделей и API должен быть отдельным системным контуром, а не «на глаз» внутри чатов.

## 2026-05-23
- [x] Экспортирован воркфлоу `Zoom call summary AI agent bot vip Copywriter` с сервера через n8n-cli в Docker-контейнере.
- [x] Создана модифицированная копия воркфлоу под Telegram-бота в папке `05_N8N_Automations/n8n_templates/Zoom_call_summary_AI_agent_bot_vip_Copywriter.json` и продублирована в корень `n8n_templates/`.
- [x] Добавлен блок Telegram Trigger для приема текстовых и аудиосообщений напрямую в бота.
- [x] Реализована логика транскрибации входящего аудио (голосовых сообщений и файлов) через официальное Whisper API от OpenAI (`api.openai.com/v1/audio/transcriptions`).
- [x] Настроен динамический Chat ID (`chat_id`), чтобы бот автоматически отвечал конкретному пользователю, написавшему в Telegram, с сохранением дефолтных каналов для вебхуков Fathom.

## 2026-05-24
- [x] Создана папка позиционирования `07_Personal_OS/core/packaging_and_positioning/`.
- [x] Написан стратегический файл `sabri_suby_strategy.md` с декомпозицией целей по воронке под высокий чек.
- [x] Написана методология Серова `serov_high_ticket_bots.md` по упаковке "Виртуальных сотрудников" и "ИИ-ОКК" для высоких чеков.
- [x] Описаны ресторанные гипотезы `restaurant_hypotheses.md` (меню с пикселями ретаргетинга и ИИ-фото блюд).
- [x] Создан Python-скрипт `06_Scripts_and_Tools/telegram_agent_bot.py` для локального запуска Telegram ИИ-агента с поддержкой OpenAI Tool Calling (выполнение команд, чтение/запись файлов, ведение РНП).
- [x] Создан файл логов РНП `07_Personal_OS/management/rnp_log.md`.
- [x] Сгенерирована квалифицированная база из 60 B2B-лидов высокого чека (мебель, дизайн, стоматологии, недвижимость, рестораны) с телефонами, почтами и описанием в форматах JSON и Markdown.
- [x] Проведен аудит сайта `okksalesagentaitrainer.vercel.app`, сгенерированы правдоподобные текстовые скриншоты-переписки ИИ в WhatsApp/Instagram и подготовлен план структуры лендингов по нишам и услугам (файл `landing_pages_and_reviews.md`).
- [x] Проведен глубокий ресерч соцсетей и найдены доп. контакты для 3 ключевых ЛПР: Ника Сараева (email, LinkedIn, X, Skool), Лизы Павлухиной (Telegram-канал `@empathysales`, VK, YouTube) и Кирилла ЗаКомфортом (телефон студии, личный TG).
- [x] Написаны готовые к отправке 4-шаговые рассылки (Персонализация, Идентификация, 3 оффера под разные боли, CTA) в `outreach_campaign_lprs.md`.
- [x] Расширен критический аудит сайта ОКК: описаны проблемы технической верстки (scroll-reveal), отсутствия калькулятора ROI и интерактивного тест-драйва ИИ.
- [x] Адаптирована маркетинговая стратегия (QR-меню и ИИ-фото блюд) под рынок г. Тараз (Казахстан) с ценами в тенге (KZT). Описан пошаговый план прохода к ЛПР через 2ГИС и подготовку ИИ-прототипа. Сформирован оффер ИИ-администратора WhatsApp для местных медицинских клиник и стоматологий.

