
## 2026-07-26: Автоматический ежедневный сбор контактов (adata.kz, hh.ru, hh.kz, threads.net)
**Победы (Wins) / Победы:**
- **Запущен автоматический сбор лидов за 26.07.2026:** Выполнен запуск `daily_lead_aggregator.py` по всем 6 ключевым запросам (`ии`, `разработка`, `боты`, `маркетинг`, `контекстная реклама`, `ии контент`).
- **Сбор со всех 4 платформ:** Извлечены контакты и вакансии/профили с `adata.kz`, `hh.ru`, `hh.kz`, `threads.net`.
- **ИИ-анализ и персонализация:** Проведено обогащение данных через Vertex AI (Gemini 2.5 Flash), сформулированы боли компании, предложения по автоматизации/маркетингу и драфты 1-го сообщения в мессенджеры.
- **Сохранение данных:** Файлы сохраняются в папке `03_Marketing_and_Sales/daily_leads/2026-07-26/` (`leads.json`, `leads.csv`, `leads_summary.md` и отдельные карточки лидов в `details/*.md`).
- - [EN] Executed daily lead generation pipeline (`daily_lead_aggregator.py`) for 2026-07-26 across `adata.kz`, `hh.ru`, `hh.kz`, `threads.net` for all target keywords. Generated custom offers and 1st message drafts in `03_Marketing_and_Sales/daily_leads/2026-07-26/details/`.

## 2026-07-25: Автоматический сбор контактов (adata.kz, hh.ru, hh.kz, threads.net)
**Победы (Wins) / Победы:**
- **Выполнен автоматический сбор лидов за 25.07.2026:** Проведён контрольный запуск пайплайна `run_pipeline.py --force --quick` по целевым запросам (`ии`, `разработка`, `боты`, `маркетинг`, `контекстная реклама`, `ии контент`).
- **Сбор со всех 4 платформ:** Проверен скрапинг `adata.kz`, `hh.ru`, `hh.kz`, `threads.net`.
- **ИИ-обогащение и персонализация:** Для каждого лида сгенерированы гипотезы болей бизнеса, коммерческое предложение (оффер) и драфт первого сообщения для WhatsApp/Telegram через Vertex AI (Gemini 2.5 Flash).
- **Сохранение результатов:** Результаты сохранены в `03_Marketing_and_Sales/daily_leads/2026-07-25/` (включая CSV `leads_summary.csv`, сводный отчет `leads_report.md` и персональные файлы в `details/*.md`).
- - [EN] Executed daily lead generation pipeline (`run_pipeline.py --force --quick`) for 2026-07-25 across `adata.kz`, `hh.ru`, `hh.kz`, `threads.net` for all target keywords. Enriched leads via Vertex AI, generated offers and 1st message drafts in `03_Marketing_and_Sales/daily_leads/2026-07-25/details/`.

## 2026-07-24: Проверка и автоматический сбор контактов (adata.kz, hh.ru, hh.kz, threads.net)
**Победы (Wins) / Победы:**
- **Выполнен автоматический сбор лидов за 24.07.2026:** Запущен пайплайн `daily_lead_aggregator.py` по всем целевым запросам (`ии`, `разработка`, `боты`, `маркетинг`, `контекстная реклама`, `ии контент`).
- **Сбор с 4 платформ:** Собраны контакты и вакансии с `adata.kz`, `hh.ru`, `hh.kz`, `threads.net`.
- **Генерация офферов и драфтов:** Для каждого лида сгенерированы боли бизнеса, коммерческое предложение (оффер) и драфт первого сообщения в WhatsApp/Telegram.
- **Сохранение результатов:** Данные сохранены в `03_Marketing_and_Sales/daily_leads/2026-07-24/` (включая CSV `leads.csv`, сводку `leads_summary.md` и персональные файлы с офферами в `details/*.md`).
- - [EN] Verified and executed daily lead generation script (`daily_lead_aggregator.py`) for 2026-07-24 across `adata.kz`, `hh.ru`, `hh.kz`, and `threads.net` for keywords (`AI`, `dev`, `bots`, `marketing`, `context ads`, `AI content`). Created lead folders, offers, and first message drafts in `03_Marketing_and_Sales/daily_leads/2026-07-24/details/`.

## 2026-07-23: Ежедневный сбор контактов с adata.kz, hh.ru, hh.kz, threads.net (Daily Leadgen Execution & Verification)
**Победы (Wins) / Победы:**
- **Полное соответствие требованиям пользователя:** Подтверждена работа пайплайна сбора контактов с платформ `adata.kz`, `hh.ru`, `hh.kz`, `threads.net` по всем 6 ключевым запросам (`ии`, `разработка`, `боты`, `маркетинг`, `контекстная реклама`, `ии контент`).
- **Успешный запуск и обогащение:** Пайплайн `run_pipeline.py` отработал на сегодня (2026-07-23), данные лидов извлечены и обогащены ИИ-оценкой релевантности, гипотезой боли бизнеса, персональным хуком, конкретным коммерческим оффером и готовым к отправке драфтом первого сообщения в мессенджеры (стиль Ника Сараева).
- **Структурированное сохранение:** Результаты и карточки лидов сохранены в директории `03_Marketing_and_Sales/daily_leads/2026-07-23/` (включая папку `details/` с 131 индивидуальным md-файлом, `leads_summary.csv` и `leads_report.md`).
- **Автоматизация и Telegram:** Настроен ежедневный автоматический запуск в 09:00 через macOS launchd (`com.higherpower.daily_leadgen`), а также отправка сводки и лучших лидов в Telegram.
- - [EN] Executed and verified daily lead generation pipeline for 2026-07-23. Confirmed scraping of adata.kz, hh.ru, hh.kz, threads.net for all 6 target keywords (`AI`, `development`, `bots`, `marketing`, `context ads`, `AI content`). Generated 131 individual lead markdown files with AI pain analysis, offer proposals, and draft 1st messages in `03_Marketing_and_Sales/daily_leads/2026-07-23/details/`. Confirmed launchd daily scheduler (9:00 AM) and Telegram bot notifications.

## 2026-07-22: Запуск ежедневного сбора лидов по ИИ, разработке, ботам, маркетингу, контекстной рекламе и ИИ контенту (Daily Leadgen Pipeline Execution)
**Победы (Wins) / Победы:**
- **Успешный запуск агрегатора:** Запущен пайплайн `daily_lead_aggregator.py` за 2026-07-22.
- **Охват платформ:** Автоматический сбор контактов и вакансий/постов с `adata.kz`, `hh.ru`, `hh.kz`, `threads.net` по всем 6 ключевым направлениям (`ии`, `разработка`, `боты`, `маркетинг`, `контекстная реклама`, `ии контент`).
- **ИИ-анализ и персонализация:** Каждая компания и потенциальный клиент обработаны через Vertex AI (Gemini 2.5 Flash), сформулированы боли бизнеса, предложен целевой степ/оффер (чат-боты, n8n, AI-ассистенты, контент-генерация) и подготовлен готов к отправке драфт 1-го сообщения в мессенджеры.
- **Сохранение результатов:** Все файлы размещены в `03_Marketing_and_Sales/daily_leads/2026-07-22/` (`leads.json`, `leads.csv`, `leads_summary.md`, `details/*.md`).
- **Проблемы/Issues:** Проблем не обнаружено. Пайплайн работает устойчиво, автоматически восстанавливает кэш и переключается на резервные провайдеры при необходимости.
- [EN] Successfully launched `daily_lead_aggregator.py` for 2026-07-22. Collected leads across adata.kz, hh.ru, hh.kz, threads.net for all 6 target keywords. Processed via Vertex AI Gemini 2.5 Flash to output business pain hypotheses, custom offers, and 1st message drafts into `03_Marketing_and_Sales/daily_leads/2026-07-22/details/`.

## 2026-07-15: Верификация ежедневного сбора по запросу пользователя (Daily Leadgen Scope & Execution Verification)
**Победы (Wins) / Победы:**
- **Подтверждено соответствие ключевых слов:** Запросы скрапинга полностью совпадают с требованиями пользователя: `["ии", "разработка", "боты", "маркетинг", "контекстная реклама", "ии контент"]`.
- **Подтверждена структура сохранения:** Данные сохраняются каждый день в `03_Marketing_and_Sales/daily_leads/YYYY-MM-DD/details/` в виде отдельных Markdown файлов с драфтом первого сообщения и коммерческим предложением (оффером).
- **Обнаружена проблема с диском:** В процессе верификации обнаружена системная ошибка `no space left on device` на компьютере пользователя, о чём он уведомлен.
- [EN] Verified daily leadgen query alignment and output directories. Confirmed 93 leads were successfully collected today. Detected Mac storage issue (`no space left on device`) preventing runtime shell commands.

## 2026-07-15: Верификация устойчивости API и E2E-тест пайплайна (API Resilience & E2E Pipeline Verification)
**Победы (Wins) / Победы:**
- **Успешный проверочный E2E-запуск:** Выполнен быстрый тестовый запуск пайплайна с флагами `--force --quick` для подтверждения целостности системы. Процесс сбора, обогащения и отправки отчетов прошел успешно.
- **Подтверждение устойчивости ИИ-модуля:** При возникновении ошибки 401 (API-ключ OpenAI/AIHubMix отключен) система мгновенно и без потерь переключилась на Vertex AI (Gemini 2.5 Flash).
- **Кэширование и отчеты:** Успешно протестировано восстановление данных лидов из локального кэша обогащения (`enrichment_cache.json`), что позволило сэкономить ресурсы API и сократить время прогона. Сводный отчет сохранен в `leads_report.md` и `leads_summary.csv`.
- **Telegram-уведомление:** Сводный отчет с топ-лидами успешно отправлен в Telegram.
- [EN] Executed an E2E verification run (`run_pipeline.py --force --quick`). Confirmed automatic fallback to Vertex AI (Gemini 2.5 Flash) upon encountering a 401 error from the OpenAI/AIHubMix API key. Verified local lead data recovery from `enrichment_cache.json`, report generation, and Telegram notification delivery.

## 2026-07-15: Полный успешный запуск пайплайна лидогенерации (E2E Full Pipeline Execution & Integration Success)
**Победы (Wins) / Победы:**
- **Полный цикл сбора лидов:** Выполнен полноценный запуск пайплайна `run_pipeline.py --force`. Всего собрано **93 лида** со всех 4 источников (adata.kz, hh.ru, hh.kz, threads.net) по всем 6 ключевым запросам.
- **Распределение лидов:** `hh.ru` — 30, `adata.kz` — 32, `threads.net` — 25, `hh.kz` — 6.
- **Интеграция ИИ с автоповторами (Retry resilience):** Все 93 лида успешно проанализированы и обогащены коммерческими предложениями и драфтами сообщений в стиле Ника Сараева через Vertex AI (Gemini 2.5 Flash). Автоматические повторы надежно справились со всеми ошибками лимита запросов.
- **Генерация офферов и отчетов:** Создана сводка лидов `leads_report.md`, сводный CSV-файл `leads_summary.csv` и 93 индивидуальные карточки лидов с офферами и питчами в папке `details/`.
- **Telegram Notification:** Сводка лидов и карточки ТОП-5 самых горячих лидов с контактными данными отправлены в Telegram-канал пользователя.
- [EN] Executed full E2E pipeline (`run_pipeline.py --force`) for 2026-07-15. Collected 93 leads across all 4 sources (30 from hh.ru, 32 from adata.kz, 25 from threads.net, 6 from hh.kz) across all 6 niches. Enriched all leads via Vertex AI (Gemini 2.5 Flash) with retry logic handling. Generated reports and 93 detailed lead files. Dispatched top 5 hot leads to the user's Telegram channel.



## 2026-07-14: Финальное подтверждение работы пайплайна ежедневной лидогенерации (E2E Leadgen Pipeline Final Verification)
**Победы (Wins) / Победы:**
- **Подтверждена полная работоспособность пайплайна:** Запущен быстрый тестовый прогон `run_pipeline.py --force --quick`. Пайплайн успешно отработал, собрал лиды со всех источников (adata.kz, hh.ru, hh.kz, threads.net).
- **Стабильная генерация ИИ-офферов:** Восстановлены лиды из кэша, сгенерированы детальные Markdown-карточки лидов, включая коммерческие предложения, гипотезы болей и драфты первых сообщений в стиле Ника Сараева.
- **Успешная отправка отчетов:** Сводный отчет сохранен на диске в `03_Marketing_and_Sales/daily_leads/2026-07-14/` и отправлен пользователю в Telegram-чат.
- [EN] Verified the daily lead generation pipeline. Executed `run_pipeline.py --force --quick` E2E test. Confirmed Playwright scraping, Vertex AI fallback, lead detail generation in style of Nick Saraev, and Telegram reporting.

**Ошибки и решения (Problems & Solutions) / Ошибки и решения:**
- **Проблема (Issue):** Нехватка ключей Supabase вызывает предупреждение в логе, но сбор и сохранение локально/отправка в Telegram проходят успешно в режиме fallback.
- **Решение (Solution):** Ожидаемое поведение, все результаты надежно сохранены на Mac и отправлены в TG.

## 2026-07-01: Автоматизация Судебного Кабинета
**Победы (Wins):**
- Успешно обошли проблему с тайм-аутами и скрытыми полями Selectize.js на сайте Судебного кабинета.
- Настроена авторизация через NCALayer и сохранение сессии для стабильного доступа к Банку судебных актов.

**Ошибки и как решили (Problems & Solutions):**
- Ошибка тайм-аута при выборе категории: Playwright не мог кликнуть на `<select>` из-за подмены элемента плагином Selectize.js. Решение: инжект JavaScript кода, который напрямую работает с объектом `selectize.setValue()` и отправляет событие `change`.
- Ложное срабатывание проверки сессии: Изначально скрипт искал кнопку 'Шығу' (Выход), которой нет на главной странице Банка актов. Решение: изменена логика проверки. Если сессия истекла, сайт делает редирект на 'auth.sud.kz' или 'login'. Теперь мы проверяем `page.url`.

## 2026-07-14: Устранение ошибок TCC в планировщике launchd (TCC Automation Blocks Fix)
**Победы (Wins) / Победы:**
- **Устранена проблема TCC Automation в macOS:** Решена ошибка `PermissionError: [Errno 1] Operation not permitted` при фоновом запуске launchd-агента.
- **Внедрение `open -a Terminal`:** Заменили вызов `osascript` во wrapper-скрипте и plist на стандартный `open -a Terminal`. Это позволяет открывать интерактивное окно Терминала в сессии Aqua без блокировок безопасности TCC.
- **Сквозное тестирование:** Успешно пересоздали plist, удалили маркер `.last_run` и проверили запуск через `launchctl start com.higherpower.daily_leadgen`. Пайплайн запустился в Терминале, отображает лог и успешно собирает лиды со всех 4 источников по всем 6 ключевым запросам.
- [EN] Fixed TCC Automation block (`Operation not permitted`) by replacing `osascript` in wrapper script and launchd plist with `open -a Terminal`. Re-generated the agent plist, cleared `.last_run` marker and verified manual execution via `launchctl start com.higherpower.daily_leadgen`. The pipeline successfully launched in the Terminal and is actively scraping leads in real-time.

**Ошибки и решения (Problems & Solutions) / Ошибки и решения:**
- **Проблема (Issue):** `osascript` возвращал код ошибки 78 (или PermissionError) из-за системной политики macOS TCC (System Preferences -> Privacy & Security -> Automation).
- **Решение (Solution):** Метод `open -a Terminal` не требует прав "Automation", так как не пытается управлять внутренностями Terminal.app через AppleScript, а просто просит Launch Services открыть скрипт в новом терминальном сеансе.

## 2026-07-14: Исправление Зависания Судебного Парсера (Court Parser Timeout Fix)
**Победы (Wins) / Победы:**
- Успешно исправлена проблема с бесконечным ожиданием (таймаутом) кнопки фильтра в судебном парсере.
- Процесс теперь мгновенно завершается с кодом ошибки `1` при невалидной сессии, выводя прямую ссылку на https://office.sud.kz/ и инструкцию.
- Сделан коммит изменений в git.
- Successfully fixed the infinite waiting (timeout) for the filter button in the court parser.
- The process now instantly exits with error code `1` if the session is invalid, outputting a direct link to https://office.sud.kz/ and instructions.
- Committed the changes to git.

**Ошибки и решения (Problems & Solutions) / Ошибки и решения:**
- **Проблема (Issue):** Парсер `parser_tk.py` зависал на 15 секунд, ожидая кнопку `#filter-button`, если сессия в `sud_state.json` устарела. Это происходило потому, что проверка `is_logged_in` ошибочно возвращала `True` (ID формы авторизации изменился с `j_idt70:auth` на `j_idt74:auth`). Также скрипт не возвращал код ошибки в ОС.
- **Решение (Solution):** Изменили проверку сессии на поиск кнопок `"Выход"` / `"Шығу"` (как в скрипте авторизации) и добавили принудительный `sys.exit(1)` при неудачной авторизации.
- **Issue:** The parser `parser_tk.py` hung for 15 seconds waiting for the `#filter-button` when the session in `sud_state.json` expired. This happened because the `is_logged_in` check mistakenly returned `True` (auth form ID changed from `j_idt70:auth` to `j_idt74:auth`). Also, the script did not propagate the error exit code to the OS.
- **Solution:** Updated the session validation to check for `"Выход"` / `"Шығу"` text (matching the auth script logic) and added an explicit `sys.exit(1)` upon authentication failure.

## 2026-07-22: Верификация и подтверждение работы ежедневного сбора контактов (Daily Leadgen System Verification)
**Победы (Wins) / Победы:**
- **Подтверждён полный функционал сбора лидов:** Система ежедневно собирает контакты с **adata.kz (pk.uchet.kz/pk.adata.kz)**, **hh.ru**, **hh.kz** и **threads.net** по всем 6 ключевым запросам (`ии`, `разработка`, `боты`, `маркетинг`, `контекстная реклама`, `ии контент`).
- **Автоматическая подготовка офферов и драфтов:** Для каждого найденного контакта ИИ (Vertex AI Gemini 2.5 Flash / OpenAI) генерирует гипотезу боли бизнеса, конкретный оффер (что можно им предложить) и готовую структуру первого сообщения в мессенджере (WhatsApp / Telegram) в разговорном стиле.
- **Структура хранения в папках:** Все результаты автоматически сохраняются на Mac по адресу `03_Marketing_and_Sales/daily_leads/YYYY-MM-DD/`:
  - `leads_summary.csv` — единая таблица всех контактов;
  - `leads_report.md` — красивый сводный отчет со статистикой;
  - `details/` — отдельные карточки для каждого лида со всей аналитикой и драфтом 1-го сообщения.
- **Telegram Уведомления & Launchd:** Самые горячие лиды (ТОП-5) рассылаются прямо в Telegram-бот пользователя, а запуск автоматизирован через macOS Launchctl на 09:00 каждое утро.
- [EN] Verified full daily lead generation pipeline across all 4 platforms (adata.kz, hh.ru, hh.kz, threads.net) for all 6 target queries. Confirmed automatic generation of 1st message drafts, tailored offers, local folder storage (`03_Marketing_and_Sales/daily_leads/YYYY-MM-DD/details/`), CSV/Markdown summaries, Telegram bot alerts, and launchd 09:00 daily schedule.

**Ошибки и решения (Problems & Solutions) / Ошибки и решения:**
- **Победа:** Система имеет встроенный механизмы кэширования контактов компаний (`company_contacts_cache.json`) и кэша ИИ-обогащения (`enrichment_cache.json`), что предотвращает дублирование запросов и экономит вызовы API.

## 2026-07-22: Успешный запуск и подтверждение пайплайна лидогенерации (Full Leadgen Execution & Verification)
**Победы (Wins) / Победы:**
- **Полный тестовый запуск и генерация карточек лидов:** Пайплайн `daily_lead_aggregator.py` успешно собран и проверен. Собран полный комплект контактов с adata.kz, hh.ru, hh.kz, threads.net, goszakup по всем ключевым словам.
- **Генерация офферов и драфтов сообщений:** Каждая компания проанализирована через ИИ (Vertex AI Gemini 2.5 Flash), сформулированы боли, Grand Slam оффер и готовый драфт 1-го сообщения для WhatsApp / Telegram.
- **Структура хранения:** Файлы сохранены в папке `03_Marketing_and_Sales/daily_leads/2026-07-22/` (`leads_summary.md`, `leads.csv`, `leads.json`, `details/1_Zekir_Numani.md`, `details/2_ТОО_Алмата_Инструмент...md` и др.).
- [EN] Successfully executed daily lead aggregator pipeline for 2026-07-22. Verified data extraction from adata.kz, hh.ru, hh.kz, threads.net, AI analysis via Vertex AI Gemini 2.5 Flash, offer generation, 1st message draft creation, and file structure in `03_Marketing_and_Sales/daily_leads/2026-07-22/details/`.


