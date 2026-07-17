Проект: AI_Lawyer
Завершённость: [████████░░] 80% — captcha/session architecture

# PROGRESS — AI Lawyer / Судебный кабинет

## Короткий вывод

Парсер `src/sud_parser.py` доведён до рабочего слоя подготовки поиска по банку судебных актов `office.sud.kz/courtActs/index.xhtml`:

- открывает публичный банк судебных актов;
- заполняет параметры поиска по трудовым спорам;
- умеет работать через установленный Google Chrome;
- сохраняет HTML-снапшоты, metadata формы, JSON/CSV результатов;
- поддерживает будущий reuse cookies/session через `--user-data-dir` и `--storage-state`;
- не получил результаты в последнем live-запуске, потому что поиск упёрся в ручной reCAPTCHA и за 300 секунд не был завершён.

## Что подтверждено live

### Страница и форма

- URL банка судебных актов: `https://office.sud.kz/courtActs/index.xhtml`
- HTTP status: `200`
- Основная форма поиска: `form#j_idt43`
- Найдены категории трудовых споров:
  - `142030000100000000` — Еңбек даулары
  - `142030000100010000` — восстановление на работе
  - `142030000100010010` — восстановление с выплатой зарплаты
  - `142030000100020000` — зарплата и иные выплаты
  - `142030000100020010` — зарплата / компенсация отпуска

### Артефакты

Папка: `AI_Lawyer/data/court_acts/`

- `court_acts_form_metadata.json` — карта формы и справочники.
- `court_acts_form_snapshot.html` — HTML формы до поиска.
- `court_acts_filled_form.png` — скрин формы после автозаполнения.
- `court_acts_search_results.html` — HTML после ожидания поиска.
- `court_acts_results.json` — нормализованные результаты.
- `court_acts_results.csv` — CSV для анализа.

Последний live-запуск:
- `court_acts_results.json`: `[]`
- `court_acts_results.csv`: только заголовки
- причина: `Время ожидания ручного поиска истекло`, результатов не появилось.

## Что изменено в коде

Файл: `AI_Lawyer/src/sud_parser.py`

Добавлено:

1. CLI-режим `--mode court-acts`.
2. Категории трудовых споров.
3. Заполнение формы банка судебных актов:
   - год;
   - категория;
   - инстанции;
   - keyword;
   - область / суд;
   - истец / ответчик / адвокат;
   - результат рассмотрения.
4. Обработка скрытых `selectize`-полей через DOM `evaluate`.
5. Парсинг HTML результатов в:
   - `CourtActResult`;
   - JSON;
   - CSV.
6. Фильтрация ложных результатов из footer/help-блоков.
7. Опциональное скачивание PDF через `--download-pdfs`.
8. Запуск через установленный Chrome:
   - `--browser-channel chrome`
9. Reuse сессии:
   - `--user-data-dir <path>` для persistent browser context;
   - `--storage-state <path>` для cookies/localStorage JSON.

## Команды

### Проверка синтаксиса и CLI

```bash
cd AI_Lawyer
python3 -m py_compile src/sud_parser.py
python3 src/sud_parser.py --help
```

### Headless smoke без ручной капчи

```bash
cd AI_Lawyer
python3 src/sud_parser.py \
  --mode court-acts \
  --year 2025 \
  --category labor_disputes \
  --keyword "Еңбек даулары" \
  --instances first \
  --max-results 10 \
  --headless
```

Ожидаемо: форма заполнится, результаты будут `0`, потому что reCAPTCHA не проходится в headless.

### Semi-auto запуск через Google Chrome

```bash
cd AI_Lawyer
python3 src/sud_parser.py \
  --mode court-acts \
  --year 2025 \
  --category labor_disputes \
  --keyword "Еңбек даулары" \
  --instances first \
  --max-results 20 \
  --manual-captcha-wait 300 \
  --browser-channel chrome
```

Дальше вручную:
1. прокрутить вниз;
2. пройти reCAPTCHA;
3. нажать кнопку поиска;
4. дождаться сохранения `JSON/CSV`.

### Запуск с persistent Chrome profile

```bash
cd AI_Lawyer
python3 src/sud_parser.py \
  --mode court-acts \
  --year 2025 \
  --category labor_disputes \
  --keyword "Еңбек даулары" \
  --instances first \
  --max-results 20 \
  --manual-captcha-wait 300 \
  --browser-channel chrome \
  --user-data-dir ./data/browser_profiles/office_sud
```

Цель: один раз пройти reCAPTCHA / авторизацию, потом переиспользовать cookies/localStorage.

### Запуск со storage_state

```bash
cd AI_Lawyer
python3 src/sud_parser.py \
  --mode court-acts \
  --year 2025 \
  --category labor_disputes \
  --keyword "Еңбек даулары" \
  --instances first \
  --max-results 20 \
  --manual-captcha-wait 300 \
  --browser-channel chrome \
  --storage-state ./data/browser_profiles/office_sud_storage.json
```

## Архитектурное решение по captcha/session

### Основной путь

1. Не пытаться каждый раз решать reCAPTCHA заново.
2. Использовать persistent browser profile:
   - `launch_persistent_context(user_data_dir=...)`;
   - cookies/localStorage живут между запусками.
3. Хранить storage state:
   - `context.storage_state(path=...)`;
   - можно запускать новые контексты с уже сохранёнными cookies.
4. Для боевого кабинета идти через:
   - реальную ЭЦП;
   - `NCALayer` / `pykalkan`;
   - session reuse после авторизации.

### Captcha solver как fallback

Возможные провайдеры:
- 2Captcha;
- Anti-Captcha;
- CapSolver.

Паттерн:
- сделать интерфейс `CaptchaProvider`;
- провайдер получает `sitekey`, `pageurl`, тип captcha;
- возвращает token;
- парсер инжектит token в `g-recaptcha-response`;
- затем инициирует submit.

Важно:
- ключи провайдеров только через env;
- не хардкодить токены;
- captcha solver — не core path, а fallback;
- юридические и операционные риски нужно отдельно принять перед production.

## SaaS-архитектура дальше

Минимальный pipeline:

1. `SearchJob`
   - категория ТК;
   - год;
   - регион;
   - сторона / ключевые слова;
   - статус.
2. `Collector`
   - Playwright + session profile;
   - скачивает HTML/PDF;
   - складывает raw artifacts.
3. `Normalizer`
   - вытаскивает номер дела, суд, дату, стороны, результат, ссылки.
4. `Document Store`
   - `raw_html`;
   - `pdf`;
   - `parsed_text`;
   - metadata JSON.
5. `Analysis`
   - стратегия истца/ответчика;
   - аргументы;
   - доказательства;
   - outcome;
   - цитаты/пруфы;
   - применённые нормы.
6. `SaaS/API`
   - пользовательские запросы;
   - очередь задач;
   - отчёты;
   - Telegram/веб-интерфейс.

## Блокеры

1. **reCAPTCHA в публичном банке актов**
   - Ручной шаг пока требуется.
   - Следующий инженерный шаг: persistent profile + storage state; затем captcha provider adapter.

2. **ЭЦП / реальный Судебный кабинет**
   - Текущий `ncalayer_mock.py` — stub.
   - Для боевого входа нужен реальный `KalkanCrypt` SDK и тестовый `GOST.p12`.

3. **Нет подтверждённых результатов поиска**
   - Последний live-запуск не завершил поиск.
   - Нужно повторить с ручным прохождением reCAPTCHA либо реализовать session reuse/captcha adapter.

## Обновление 2026-07-01 — cookies + P12 + кабинет

### Что добавлено

1. Найден и подключён cookie export:
   - внешний файл: `sud_cookies.json`;
   - формат: список cookies;
   - подтверждённая cookie: `JSESSIONID`;
   - домен: `office.sud.kz`.
2. Добавлен CLI-флаг:
   ```bash
   --cookies-json <path>
   ```
   Он загружает exported cookies и превращает их в Playwright `storage_state`.
3. Подтверждено live:
   - `JSESSIONID` открывает авторизованный `office.sud.kz`;
   - кабинетная страница содержит признаки авторизации: `Выход` / `Личный кабинет`;
   - скрипт корректно распознаёт авторизованный кабинет и пропускает ЭЦП-вход.
4. Проверена страница поиска судебных дел:
   - URL: `https://office.sud.kz/form/lawsuit/`
   - HTTP status: `200`
   - есть поля:
     - `#j_idt36:j_idt37:edit-iin` — `ИИН / БИН`;
     - `#j_idt36:j_idt37:edit-num` — `Номер дела`.
   - есть reCAPTCHA.
5. Новый `.p12` ключ:
   - файл найден в Downloads;
   - пароль из `.env` переменной `PASS_p12`;
   - проверка `openssl pkcs12` прошла: `p12_password_ok=1`;
   - путь записан в `.env` как `P12_PATH` и `TEST_KEY_PATH`.
6. `src/ncalayer_mock.py` теперь:
   - читает `.env` без внешней зависимости;
   - не логирует секреты;
   - маскирует путь к ключу;
   - поддерживает `PASS_p12`, `P12_PATH`, `TEST_KEY_PATH`;
   - подготовлен к реальной подписи через `pykalkan.Adapter`;
   - ясно сообщает, что `pykalkan` не установлен.
7. Добавлен `AI_Lawyer/.gitignore`:
   - `.env`;
   - `*.p12`, `*.pfx`;
   - browser profiles / cookies / storage;
   - runtime HTML/PNG/CSV/JSON artifacts.

### Live smoke

```bash
cd AI_Lawyer
PYTHONDONTWRITEBYTECODE=1 python3 src/sud_parser.py \
  --mode iin \
  --headless \
  --cookies-json "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/sud_cookies.json"
```

Результат:
- `syntax_ok=1`
- cookies загружены: `count=1`, `names=['JSESSIONID']`
- кабинет авторизован: `Похоже, cookies/session уже открыли авторизованный кабинет`
- страница поиска судебных дел сохранена без запуска поиска:
  - `data/cabinet/lawsuit_search.html`
  - `data/cabinet/lawsuit_search.png`

### Текущие ограничения

- `pykalkan` не установлен, поэтому реальная подпись через KalkanCrypt пока недоступна.
- `KalkanCrypt SDK` / `libkalkancryptwr-64.so` ещё не установлен.
- `/form/lawsuit/` всё равно содержит reCAPTCHA, даже внутри авторизованного кабинета.
- Поиск по ИИН/БИН реализован как подготовленный workflow, но боевой поиск с конкретным ИИН ещё не запускался.

## Следующий точный шаг

1. Установить `pykalkan` и KalkanCrypt SDK:
   ```bash
   cd AI_Lawyer
   pip3 install pykalkan
   ```
   Затем положить/указать `libkalkancryptwr-64.so` через:
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
5. Для публичного банка актов с cookie:
   ```bash
   cd AI_Lawyer
   PYTHONDONTWRITEBYTECODE=1 python3 src/sud_parser.py \
     --mode court-acts \
     --cookies-json "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/sud_cookies.json" \
     --browser-channel chrome \
     --manual-captcha-wait 600
   ```
