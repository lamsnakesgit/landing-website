
## 2026-07-01: Автоматизация Судебного Кабинета
**Победы (Wins):**
- Успешно обошли проблему с тайм-аутами и скрытыми полями Selectize.js на сайте Судебного кабинета.
- Настроена авторизация через NCALayer и сохранение сессии для стабильного доступа к Банку судебных актов.

**Ошибки и как решили (Problems & Solutions):**
- Ошибка тайм-аута при выборе категории: Playwright не мог кликнуть на `<select>` из-за подмены элемента плагином Selectize.js. Решение: инжект JavaScript кода, который напрямую работает с объектом `selectize.setValue()` и отправляет событие `change`.
- Ложное срабатывание проверки сессии: Изначально скрипт искал кнопку 'Шығу' (Выход), которой нет на главной странице Банка актов. Решение: изменена логика проверки. Если сессия истекла, сайт делает редирект на 'auth.sud.kz' или 'login'. Теперь мы проверяем `page.url`.

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
