# PROGRESS
Отслеживание новых фич и завершенных модулей в проекте.

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
