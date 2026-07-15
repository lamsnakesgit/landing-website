
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
