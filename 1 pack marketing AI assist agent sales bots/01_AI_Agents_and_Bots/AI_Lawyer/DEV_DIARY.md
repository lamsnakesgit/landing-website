# Дневник Разработки: ИИ-Юрист (MVP)

В этом файле мы ведем историю развития проекта, фиксируем принятые архитектурные решения, возникшие проблемы (блокеры) и то, как мы их преодолели. Это поможет другим агентам (и нам самим) не наступать на те же грабли.

## 🎯 Глобальная цель (Зачем мы это делаем?)
Создать автономного ИИ-Юриста, который помогает юристам экономить время.  
**MVP:** Бот, который по ИИН/БИН заходит в "Судебный кабинет" (через ЭЦП), скачивает судебные акты (PDF), а также обновленные законы из "Параграфа" (Word), и анализирует их через LLM (Gemini/GPT-4o) для поиска стратегии, судебной практики и генерации документов.

---

## 🛠️ Архитектурные Решения (Что мы решили?)
- **Стек:** Python + Playwright + LLM API.
- **Почему не n8n?** Судебный кабинет использует сложную систему авторизации (NCALayer, WebSocket), которую невозможно надежно обходить через визуальные ноды n8n. Playwright дает полный контроль над DOM-деревом браузера.
- **ЭЦП / NCALayer:** для боевого входа нужен реальный KalkanCrypt SDK + `.p12` ключ. Локальный `ncalayer_mock.py` теперь умеет читать `.env`, видеть `.p12` и готов к подписи через `pykalkan.Adapter`, но сам `pykalkan` и KalkanCrypt SDK ещё не установлены.
- **Session-first подход:** если уже есть валидный `JSESSIONID`, используем `--cookies-json` / persistent profile и не гоняем ЭЦП каждый запуск.
- **Captcha strategy:** reCAPTCHA не зашивается хаком в парсер. Основной путь — cookies/session reuse; fallback — отдельный `CaptchaProvider` adapter после отдельного решения по рискам.

---

## 🚀 Прогресс (Что уже сделали)

### [2026-06-29] Этап 1: Фундамент и архитектура
1. **Создан план MVP (`MVP_Plan.md`).** Описаны юзкейсы ИИ (генерация стратегий, оценка успешности иска).
2. **Написан микросервис `ncalayer_mock.py`.**
   - *Проблема:* Как заставить браузер общаться с нашим питоном?
   - *Решение:* Подняли `websockets` сервер на `127.0.0.1:13579`. Сервер отвечает на стандартные запросы (`getActiveTokens`, `createCAdESFromBase64`), которые ожидает фронтенд Судебного кабинета.
3. **Написан базовый скрейпер `sud_parser.py`.**
   - *Гипотеза:* Мы не знали, как именно устроен фронтенд сайта `office.sud.kz`.
   - *Действие:* Написали тестовый скрипт, скачали HTML-код главной страницы.
   - *Открытие:* Нашли точные селекторы. Вкладка ЭЦП имеет `id="tab-eds"`. Кнопка вызова подписи работает через `onclick="selectSignType()"`. Данные для подписи могут прятаться в скрытых инпутах.
   - *Результат:* Парсер умеет открывать сайт и доходить до сценария авторизации.

---

### [2026-06-30] Этап 2: Публичный банк судебных актов + session/captcha architecture
1. **Найден рабочий публичный источник судебных актов:** `https://office.sud.kz/courtActs/index.xhtml`.
   - Страница доступна live, HTTP `200`.
   - Основная форма поиска: `form#j_idt43`.
2. **Доработан `src/sud_parser.py` под поиск трудовых споров.**
   - Добавлен режим `--mode court-acts`.
   - Добавлены категории ТК/трудовых споров: `labor_disputes`, `reinstatement`, `salary_payments` и др.
   - Реализовано автозаполнение формы, включая скрытые `selectize`-поля через DOM.
   - Добавлено сохранение HTML, metadata, JSON/CSV результатов и screenshot.
3. **Подтверждён блокер reCAPTCHA.**
   - Live-запуск через `--browser-channel chrome` открывает Google Chrome и заполняет форму.
   - Один из запусков не получил результаты: ручной поиск не был завершён за `300` секунд, `court_acts_results.json = []`.
4. **Добавлен session/cookies reuse.**
   - `--user-data-dir` для persistent browser profile.
   - `--storage-state` для Playwright cookies/localStorage JSON.
5. **Зафиксирована архитектура.**
   - `PROGRESS.md` — текущее состояние, команды, блокеры.
   - `ARCHITECTURE.md` — pipeline, captcha/session strategy, SaaS-путь.

---

### [2026-07-01] Этап 3: Cookie login + P12 key + кабинетный поиск дел
1. **Подтверждён живой cookie-login в `office.sud.kz`.**
   - Найден внешний `sud_cookies.json`.
   - Формат: список cookies.
   - Подтверждённая cookie: `JSESSIONID`, domain `office.sud.kz`.
   - `src/sud_parser.py --mode iin --headless --cookies-json ...` открывает авторизованный кабинет и пропускает ЭЦП-вход.
2. **Найден и проверен новый `.p12` ключ.**
   - Последний ключ в Downloads: `GOST512_28412edbee5073856db88468b73dbd8f53bb9636.p12`.
   - Пароль берётся из `.env` переменной `PASS_p12`.
   - Проверка через `openssl pkcs12` прошла: `p12_password_ok=1`.
   - В `.env` добавлены `P12_PATH` и `TEST_KEY_PATH` без вывода секретов.
3. **Доработан `src/ncalayer_mock.py`.**
   - Загружает `.env` без внешней зависимости.
   - Маскирует путь к ключу.
   - Не логирует пароль и signed payload.
   - Подготовлен к реальной подписи через `pykalkan.Adapter`.
   - Поддерживает `createCAdESFromBase64` и `createCMSSignatureFromBase64`.
4. **Доработан `src/sud_parser.py` под кабинет.**
   - `--cookies-json` поддержан для публичного банка актов и режима `--mode iin`.
   - Добавлена эвристика авторизованного кабинета по HTML markers.
   - Найден маршрут поиска судебных дел: `/form/lawsuit/`.
   - Найдены поля:
     - `#j_idt36:j_idt37:edit-iin` — ИИН/БИН;
     - `#j_idt36:j_idt37:edit-num` — номер дела.
   - При отсутствии `--iin` скрипт сохраняет страницу поиска дел без запуска поиска.
5. **Добавлен `.gitignore`.**
   - Игнорируются `.env`, `*.p12`, `*.pfx`, browser/session profiles, cookies/storage JSON и runtime artifacts.
6. **Smoke-тесты пройдены.**
   - `syntax_ok=1`.
   - `JSESSIONID` загружается и открывает авторизованный кабинет.
   - `/form/lawsuit/` доступен с cookies, HTTP `200`, содержит ИИН/БИН и номер дела, но также содержит reCAPTCHA.

---

## 🚧 Текущие ошибки, блокеры и гипотезы (Что болит)

**Блокер 1: `pykalkan` / KalkanCrypt ещё не установлены**
- *Описание:* `.p12` ключ и пароль проверены, но Python-модуль `pykalkan` отсутствует, а KalkanCrypt shared library не подключена.
- *Решение:* Установить `pykalkan`, положить `libkalkancryptwr-64.so`, указать `KALKAN_LIBRARY_PATH`, затем проверить `ncalayer_mock.py` на реальной подписи.

**Блокер 2: reCAPTCHA в публичном банке и `/form/lawsuit/`**
- *Описание:* Публичный банк актов и страница поиска судебных дел защищены Google reCAPTCHA. Cookies открывают кабинет, но не гарантируют автоматический поиск без captcha.
- *Решение по умолчанию:* session/cookies reuse через `--cookies-json` или `--user-data-dir`. Fallback — отдельный `CaptchaProvider` adapter для 2Captcha / Anti-Captcha / CapSolver после отдельного решения по рискам.

**Блокер 3: Гео-блокировка**
- *Описание:* Государственные сайты РК могут блокировать запросы от зарубежных IP.
- *Решение:* Скрейпер и Эмулятор ЭЦП в итоге должны быть развернуты на VPS в Казахстане или в окружении с устойчивым доступом к `office.sud.kz`.

**Блокер 4: Мало свободного места на диске**
- *Описание:* При проверке `py_compile` система не смогла записать `.pyc`: `No space left on device`. После очистки стало около `2.2Gi`, но диск всё ещё близко к 100%.
- *Решение:* Для проверок использовать `PYTHONDONTWRITEBYTECODE=1` и освободить место перед тяжёлыми браузерными/парсинговыми задачами.

---

## 🔜 Следующие шаги (Что делать дальше)

1. Установить `pykalkan` и KalkanCrypt SDK:
   ```bash
   cd AI_Lawyer
   pip3 install pykalkan
   ```
   затем указать:
   ```env
   KALKAN_LIBRARY_PATH=/path/to/libkalkancryptwr-64.so
   ```

2. Запустить NCALayer mock:
   ```bash
   cd AI_Lawyer
   PYTHONDONTWRITEBYTECODE=1 python3 src/ncalayer_mock.py
   ```

3. Проверить кабинетный flow с cookies:
   ```bash
   cd AI_Lawyer
   PYTHONDONTWRITEBYTECODE=1 python3 src/sud_parser.py \
     --mode iin \
     --browser-channel chrome \
     --cookies-json "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/sud_cookies.json"
   ```

4. Для поиска по ИИН/БИН:
   ```bash
   cd AI_Lawyer
   PYTHONDONTWRITEBYTECODE=1 python3 src/sud_parser.py \
     --mode iin \
     --iin "<IIN_OR_BIN>" \
     --browser-channel chrome \
     --cookies-json "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/sud_cookies.json"
   ```

5. Дописать парсинг результатов `/form/lawsuit/` и скачивание PDF через `page.expect_download()`.

6. Для публичного банка актов с cookie:
   ```bash
   cd AI_Lawyer
   PYTHONDONTWRITEBYTECODE=1 python3 src/sud_parser.py \
     --mode court-acts \
     --cookies-json "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/sud_cookies.json" \
  --browser-channel chrome \
  --manual-captcha-wait 600
   ```
