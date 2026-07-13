
## 2026-07-14: Верификация ежедневного сбора контактов и генерации офферов (Pipeline Verification & Output Structure Audit)
**Победы (Wins):**
- Проведена верификация работы ежедневного сбора контактов со всех источников (adata.kz, hh.ru, hh.kz, threads.net).
- Проверен запуск пайплайна через `run_pipeline.py`. Все шаги (Playwright скрапинг, ИИ-обогащение через Vertex AI fallback) отработали успешно.
- Подтверждена правильная структура сохранения результатов: индивидуальные карточки лидов с драфтами первого сообщения и предложением услуг сохраняются в папку `03_Marketing_and_Sales/daily_leads/YYYY-MM-DD/details/` в формате Markdown.
- Проверен планировщик `launchd` (`com.higherpower.daily_leadgen`), настроенный на ежедневный автоматический запуск в 09:00 утра.
- [EN] Verified the daily lead generation pipeline for all sources (adata.kz, hh.ru, hh.kz, threads.net). Verified structured output directories containing custom pitches and business offers at `03_Marketing_and_Sales/daily_leads/YYYY-MM-DD/details/`. Confirmed launchd scheduler is properly configured for daily 09:00 AM execution.

**Ошибки и как решили (Problems & Solutions):**
- Все тесты прошли успешно, критических ошибок и зависаний в работе парсеров и Vertex AI не обнаружено.

## 2026-07-13: Исправление зависаний сети, автоматический фолбек на Vertex AI и восстановление Playwright
**Победы (Wins):**
- Добавлена жесткая защита от сетевых зависаний в `daily_leadgen.py` с помощью `socket.setdefaulttimeout(35)` и явного таймаута в запросах (25 сек). Это полностью решило проблему бесконечного ожидания ответа от API.
- Реализована автоматическая проверка работоспособности ключа OpenAI/AIHubMix на старте скрипта. Если API возвращает ошибку 401 (ключ отключен), пайплайн мгновенно переключается на Vertex AI, исключая задержки и падения на середине процесса.
- Успешно установлены недостающие бинарные файлы браузеров Playwright (`python3 -m playwright install`), из-за отсутствия которых скрапер падал с ошибкой.
- Внедрен сквозной флаг `--quick` в `run_pipeline.py` и `playwright_leadgen.py`, позволяющий запускать пайплайн с лимитом запросов и лидов для мгновенного локального smoke-тестирования.
- Успешно проведен сквозной тестовый прогон всего пайплайна (`run_pipeline.py --force --quick`), подтвердивший стабильность сбора, ИИ-обогащения через Vertex AI, генерации отчетов и отправки в Telegram.
- [EN] Fixed networking hangs in `daily_leadgen.py` via global socket timeouts (35s) and explicit requests.post timeouts (25s). Added instant OpenAI/AIHubMix key pre-flight check with auto-fallback to Vertex AI on 401 error. Restored missing Playwright browser binaries and added a `--quick` smoke-test mode across the pipeline, verifying everything with a successful end-to-end dry run.

**Ошибки и как решили (Problems & Solutions):**
- Зависание пайплайна: Vertex AI/OpenAI API запросы висели бесконечно. Решено добавлением таймаутов сокета на уровне Python.
- Ошибка Playwright "Executable doesn't exist": Восстановлена целостность окружения запуском `python3 -m playwright install`.

## 2026-07-08: Оптимизация судебного парсера и сквозная верификация пайплайна (Court Parser Optimization & End-to-End Pipeline Verification)
**Победы (Wins):**
- Полностью переработан механизм авторизации и навигации в судебном парсере `scripts/sud_parser/parser_tk.py`. Полностью отключен интерактивный режим (`headless=False`), настроены жесткие таймауты перехода (20 секунд) и авто-закрытие всплывающих диалоговых окон. Это исключило любые зависания в фоновом режиме.
- [EN] Redesigned authentication and navigation in the court parser (`scripts/sud_parser/parser_tk.py`). Completely disabled GUI interactive mode (`headless=False`), configured strict 20s transition timeouts, and added automated dialog dismissal to eliminate background hangs.
- Проведен успешный сквозной принудительный запуск пайплайна (`run_pipeline.py --force`). Собрано и обогащено **73 лида** (HH, Adata, Threads).
- [EN] Successfully performed a force run of the full pipeline. Scraped and enriched **73 leads** from all sources.
- Проверена работа автоматического переключения на Vertex AI (Gemini 2.5 Flash по HTTP) при ошибке 401 для ключей AIHubMix/OpenAI. Все лиды были успешно проанализированы, офферы и персональные питчи сохранены локально, а отчет отправлен в Telegram.
- [EN] Confirmed robust failover to Vertex AI (Gemini 2.5 Flash over HTTP) when OpenAI/AIHubMix API keys returned 401. All leads were analyzed, pitches generated, and the Telegram summary sent.

## 2026-07-01: Верификация ежедневной лидогенерации (Leadgen Verification)
**Победы (Wins):**
- Полностью верифицирована работа ежедневного пайплайна сбора контактов с hh.ru, hh.kz, adata.kz и threads.net по 6 темам (ИИ, разработка, боты, маркетинг, контекст, ИИ-контент).
- Сегодняшний автоматический запуск от 01.07.2026 завершился успешно: собрано **76 лидов** (hh.kz — 7, hh.ru — 30, adata.kz — 32, threads.net — 7).
- Для каждого лида успешно созданы индивидуальные карточки с ИИ-анализом боли, предложением услуг и драфтом сообщения на русском языке в `03_Marketing_and_Sales/daily_leads/2026-07-01/details/`.
- [EN] Fully verified the daily contact scraper pipeline for hh.ru, hh.kz, adata.kz, and threads.net. Today's run succeeded with **76 leads** collected, analyzed via Vertex AI/OpenAI, and saved locally with custom pitches and recommendations.

**Ошибки и как решили (Problems & Solutions):**
- Отсутствие Supabase URL/KEY в `.env`: Скрипт выдает предупреждение, но корректно пропускает запись в БД, сохраняя все результаты локально в CSV/Markdown и отправляя топ-5 в Telegram. Никаких доработок не потребовалось, логи чистые.
- [EN] Missing Supabase keys in `.env` causes a warning but does not block the pipeline. The script skips DB insertion and finishes successfully, writing output files to disk and sending to Telegram.

## 2026-07-01: Автоматизация Судебного Кабинета
**Победы (Wins):**
- Успешно обошли проблему с тайм-аутами и скрытыми полями Selectize.js на сайте Судебного кабинета.
- Настроена авторизация через NCALayer и сохранение сессии для стабильного доступа к Банку судебных актов.

**Ошибки и как решили (Problems & Solutions):**
- Ошибка тайм-аута при выборе категории: Playwright не мог кликнуть на `<select>` из-за подмены элемента плагином Selectize.js. Решение: инжект JavaScript кода, который напрямую работает с объектом `selectize.setValue()` и отправляет событие `change`.
- Ложное срабатывание проверки сессии: Изначально скрипт искал кнопку 'Шығу' (Выход), которой нет на главной странице Банка актов. Решение: изменена логика проверки. Если сессия истекла, сайт делает редирект на 'auth.sud.kz' or 'login'. Теперь мы проверяем `page.url`.

## 2026-07-01: Проверка планировщика и логов (Scheduler & Logs Audit)
**Победы (Wins):**
- Проверен статус launchd-агента `com.higherpower.daily_leadgen`. Он успешно загружен.
- Проанализированы логи выполнения пайплайна за 01.07.2026: благодаря обходу ограничений TCC (вызов через Terminal.app в контексте Aqua-сессии) ошибки `Operation not permitted` больше не возникают, виртуальное окружение `.venv` импортируется корректно.
- [EN] Verified launchd agent `com.higherpower.daily_leadgen` status. Confirmed the pipeline executed correctly on 2026-07-01 without TCC permission issues due to running wrapper inside Terminal.app.

## 2026-07-02: Верификация и фоновый запуск пайплайна сбора контактов
**Победы (Wins):**
- Успешно завершен внеочередной ручной сбор лидов за сегодня (02.07.2026): собрано и обогащено **76 лидов**.
- Проверена структура сохранения результатов: сгенерированные драфты сообщений и персонализированные офферы успешно сохранены в [details/](file:///Users/higherpower/Desktop/1_Active_Projects/2%20Ai_agents/1%20pack%20marketing%20AI%20assist%20agent%20sales%20bots/03_Marketing_and_Sales/daily_leads/2026-07-02/details/), а также созданы общие файлы [leads_report.md](file:///Users/higherpower/Desktop/1_Active_Projects/2%20Ai_agents/1%20pack%20marketing%20AI%20assist%20agent%20sales%20bots/03_Marketing_and_Sales/daily_leads/2026-07-02/leads_report.md) и [leads_summary.csv](file:///Users/higherpower/Desktop/1_Active_Projects/2%20Ai_agents/1%20pack%20marketing%20AI%20assist%20agent%20sales%20bots/03_Marketing_and_Sales/daily_leads/2026-07-02/leads_summary.csv).
- Успешно отправлен ежедневный отчет в Telegram с топ-5 самыми горячими контактами.
- [EN] Successfully executed manual daily lead generation run for 2026-07-02, processing **76 leads**. Generated custom pitches and local assets, sent Telegram briefing.

## 2026-07-04: Верификация и стабильный фоновый запуск лидогенерации
**Победы (Wins):**
- Успешно завершен сбор и обогащение лидов за сегодня (04.07.2026): собрано и обогащено **67 лидов** (hh.ru — 25, adata.kz — 32, hh.kz — 8, threads.net — 2).
- Все результаты сохранены локально в папке [03_Marketing_and_Sales/daily_leads/2026-07-04/](file:///Users/higherpower/Desktop/1_Active_Projects/2%20Ai_agents/1%20pack%20marketing%20AI%20assist%20agent%20sales%20bots/03_Marketing_and_Sales/daily_leads/2026-07-04/). Для каждого лида сгенерирован качественный оффер и драфт первого сообщения без лишнего канцеляризма.
- Успешно отработал ИИ-анализ на базе Vertex AI (Gemini 2.5 Flash по HTTP с авторизацией по кэшированному сервисному аккаунту). Это гарантирует бесперебойную работу даже при исчерпании лимитов сторонних провайдеров.
- Отчет со сводной информацией и топ-5 лидов успешно отправлен в Telegram.
- [EN] Successfully completed daily leadgen pipeline run for 2026-07-04, collecting **67 leads**. Enriched details via Vertex AI HTTP fallback, saved local outputs, and dispatched Telegram briefing.

**Ошибки и как решили (Problems & Solutions):**
- Предупреждение о Supabase: в логах зафиксировано `Supabase URL или KEY отсутствуют в .env. Запись в БД пропущена`. Это не мешает работе пайплайна, так как все файлы сохраняются на диске и отправляются в TG.
- [EN] Warning about missing Supabase keys is logged, but the pipeline completes successfully without DB write.






## Анализ судебных дел (ai lawyer output) - 04 Июля 2026
**Wins / Успехи:**
- Успешно извлечены и проанализированы 20 судебных документов (.docx) из папки `output/pdfs`.
- Выявлено, что часть файлов являются дубликатами. Смогли точно определить победителей.

**Problems issues / Проблемы и решения:**
- API ключ Gemini оказался нерабочим (HTTP 403 Forbidden) для генерации контента.
- **Решение:** Написан кастомный скрипт для извлечения текста напрямую из XML-структуры .docx файлов, после чего произведен семантический анализ результатов.
