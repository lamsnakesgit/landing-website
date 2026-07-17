Проект: AI_Lawyer
Завершённость: [████████░░] 80% — captcha/session architecture

# ARCHITECTURE — парсинг судебных дел по ТК

## Цель

Собрать устойчивый pipeline для поиска и анализа судебных дел по трудовому кодексу / трудовым спорам:

1. находить релевантные дела;
2. скачивать HTML/PDF/акты;
3. нормализовать metadata;
4. извлекать аргументы, доказательства, правовые нормы и исход;
5. строить SaaS-аналитику стратегий для юристов.

## Источники данных

### 1. Публичный банк судебных актов

- URL: `https://office.sud.kz/courtActs/index.xhtml`
- Статус: доступен, HTTP `200`.
- Плюсы:
  - публичный доступ;
  - есть фильтры по году, категории, региону, инстанции, сторонам и результату;
  - содержит вступившие в законную силу акты.
- Минусы:
  - есть Google reCAPTCHA;
  - поиск нельзя надёжно запускать полностью headless без дополнительной captcha/session strategy;
  - HTML/JSF-разметка может меняться.

### 2. Судебный кабинет

- URL: `https://office.sud.kz/`
- Цель: доступ к более полным материалам дела, документам и скачиванию PDF.
- Требует:
  - ЭЦП;
  - NCALayer;
  - реальный KalkanCrypt SDK;
  - рабочий `GOST.p12` / ключ клиента.
- Текущий `src/ncalayer_mock.py` — stub / reverse-engineering слой, не полноценная боевая подпись.

### 3. Внешние правовые базы

Будущий слой:
- Параграф / аналоги;
- скачивание НПА в Word;
- RAG / knowledge base для норм права и редакций закона.

## Текущий кодовый слой

Основной файл: `src/sud_parser.py`

### Поддержанные режимы

- `--mode court-acts` — публичный банк судебных актов.
- `--mode iin` — старый сценарий через Судебный кабинет / ИИН, пока не завершён.

### Главные возможности

- Открытие банка актов.
- Автозаполнение формы поиска.
- Категории трудовых споров:
  - `labor_disputes`
  - `reinstatement`
  - `reinstatement_with_salary`
  - `salary_payments`
  - `salary_and_vacation_compensation`
- Фильтры:
  - год;
  - инстанции;
  - регион;
  - суд;
  - истец;
  - ответчик;
  - адвокат;
  - результат рассмотрения.
- Сохранение:
  - HTML формы;
  - HTML результатов;
  - metadata формы;
  - JSON результатов;
  - CSV результатов;
  - screenshot формы.
- Session/cookies:
  - `--user-data-dir`;
  - `--storage-state`.
- Chrome GUI:
  - `--browser-channel chrome`.

## Captcha strategy

### Не делать

Не зашивать “обход капчи” прямо в парсер как случайный хак.

Причины:
- высокая хрупкость;
- риск блокировок;
- сложно дебажить;
- зависимость от внешнего сервиса;
- возможные юридические/ToS риски.

### Базовый production-путь

1. Persistent browser profile:
   ```bash
   --user-data-dir ./data/browser_profiles/office_sud
   ```
2. Первый запуск:
   - человек вручную проходит reCAPTCHA / авторизацию;
   - cookies/localStorage сохраняются в профиле.
3. Следующие запуски:
   - использовать тот же profile;
   - пытаться искать без повторной reCAPTCHA.
4. Если сессия протухла:
   - fallback: ручное обновление сессии;
   - либо captcha provider adapter.

### Storage state

Playwright official pattern:
- `context.storage_state(path=...)`;
- следующий контекст стартует с `storage_state=...`.

Команда:

```bash
python3 src/sud_parser.py \
  --mode court-acts \
  --browser-channel chrome \
  --storage-state ./data/browser_profiles/office_sud_storage.json \
  --manual-captcha-wait 600
```

### CaptchaProvider adapter

Если решаем использовать solver:

```text
CaptchaProvider
  solve_recaptcha_v2(sitekey, page_url) -> token
```

Провайдеры:
- 2Captcha;
- Anti-Captcha;
- CapSolver.

Требования:
- API key только из env;
- не хранить ключи в коде;
- логировать только request id / status, без секретов;
- иметь таймауты и retry;
- fallback на ручной режим.

## Cookies/session architecture

### Persistent profile

Папка:

```text
AI_Lawyer/data/browser_profiles/office_sud/
```

Что хранит:
- cookies;
- localStorage;
- IndexedDB;
- browser preferences;
- возможно состояние reCAPTCHA / авторизации.

Плюсы:
- ближе всего к реальному браузерному сценарию;
- меньше ручных действий;
- можно использовать для Судебного кабинета после ЭЦП-логина.

Минусы:
- профиль нельзя безопасно шарить;
- может протухать;
- нужен secure storage на сервере.

### Storage state JSON

Путь:

```text
AI_Lawyer/data/browser_profiles/office_sud_storage.json
```

Плюсы:
- проще переносить между job-ами;
- удобно для CI/worker архитектуры.

Минусы:
- не всё состояние браузера сохраняется;
- session может зависеть от fingerprint/IP/User-Agent.

### Exported cookies JSON

Поддержан отдельный входной формат:

```bash
--cookies-json /path/to/sud_cookies.json
```

Текущий подтверждённый файл содержит:

- `JSESSIONID`;
- domain: `office.sud.kz`;
- format: list of browser cookies.

Этот файл превращается в Playwright `storage_state` в runtime. Значения cookies не логируются.

Подтверждено live:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 src/sud_parser.py \
  --mode iin \
  --headless \
  --cookies-json "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/sud_cookies.json"
```

Результат:
- cookies загружены;
- авторизованный кабинет открыт;
- ЭЦП-вход пропущен;
- `/form/lawsuit/` сохранён как HTML/PNG.

## ЭЦП / NCALayer architecture

### P12 key

Подтверждено:

- новый `.p12` лежит в Downloads;
- пароль есть в `.env` как `PASS_p12`;
- `openssl pkcs12` подтвердил пароль: `p12_password_ok=1`;
- `.env` дополнен:
  - `P12_PATH=<set>`;
  - `TEST_KEY_PATH=<set>`.

Секреты и ключи игнорируются через `AI_Lawyer/.gitignore`.

### NCALayer mock

Файл:

```text
src/ncalayer_mock.py
```

Текущее состояние:

- читает `.env` без внешней зависимости;
- поддерживает env:
  - `PASS_p12`;
  - `P12_PASSWORD`;
  - `TEST_KEY_PASSWORD`;
  - `P12_PATH`;
  - `TEST_KEY_PATH`;
  - `KALKAN_LIBRARY_PATH`;
  - `ALLOW_STUB_SIGNATURE`;
- не логирует пароль;
- маскирует путь к ключу;
- поддерживает методы:
  - `getActiveTokens`;
  - `createCAdESFromBase64`;
  - `createCMSSignatureFromBase64`;
- подготовлен к реальной подписи через `pykalkan.Adapter`.

Текущий блокер:

- `pykalkan` не установлен;
- KalkanCrypt shared library ещё не подключена;
- без этого реальная CAdES/CMS подпись не выполняется.

Минимальный следующий шаг:

```bash
cd AI_Lawyer
pip3 install pykalkan
```

Затем указать библиотеку:

```env
KALKAN_LIBRARY_PATH=/path/to/libkalkancryptwr-64.so
```

## SaaS pipeline

```text
User/Search Request
  ↓
SearchJob
  ↓
Collector
  ↓
Raw Artifacts Store
  ↓
Normalizer
  ↓
Document Text Extraction
  ↓
LLM Legal Analysis
  ↓
Report / Strategy / Dataset
```

### SearchJob

Поля:
- `job_id`
- `source`: `court_acts` / `cabinet`
- `category`
- `year`
- `region`
- `court`
- `keyword`
- `party`
- `status`
- `created_at`
- `finished_at`

### Collector

Задачи:
- открыть источник;
- восстановить session;
- заполнить форму;
- пройти captcha strategy;
- сохранить HTML/PDF.

### Raw Artifacts Store

Структура:

```text
data/
  court_acts/
    raw/
      <job_id>/
        search_page.html
        result_page.html
        screenshots/
        pdf/
    normalized/
      <job_id>.json
      <job_id>.csv
```

### Normalizer

Извлекает:
- номер дела;
- суд;
- дата;
- судья;
- стороны;
- категория;
- результат;
- ссылки на документы;
- текст решения.

### Analysis

LLM-задачи:
- классификация исхода;
- аргументы истца;
- аргументы ответчика;
- доказательства;
- применённые нормы;
- позиция суда;
- что сработало / не сработало;
- рекомендации для похожего дела.

## Ближайшие инженерные шаги

1. Проверить persistent profile:
   ```bash
   cd AI_Lawyer
   python3 src/sud_parser.py \
     --mode court-acts \
     --browser-channel chrome \
     --user-data-dir ./data/browser_profiles/office_sud \
     --manual-captcha-wait 600
   ```

2. После ручного прохождения reCAPTCHA повторить тот же запуск.
   - Если повторный поиск проходит без капчи — session reuse рабочий.
   - Если нет — делать `CaptchaProvider`.

3. Добавить `--parse-html-file` режим:
   - пользователь вручную сохраняет HTML страницы результатов;
   - парсер превращает HTML в JSON/CSV без браузера.

4. Добавить `job_id` и раскладку raw artifacts по job-папкам.

5. Для Судебного кабинета:
   - установить `pykalkan`;
   - подключить KalkanCrypt SDK (`libkalkancryptwr-64.so`);
   - использовать уже найденный `.p12` и `PASS_p12` из `.env`;
   - проверить `ncalayer_mock.py` с реальной подписью;
   - использовать `sud_cookies.json` / persistent profile для входа без повторной ЭЦП, пока сессия жива.
6. Для поиска судебных дел:
   - использовать `/form/lawsuit/`;
   - поле ИИН/БИН: `#j_idt36:j_idt37:edit-iin`;
   - поле номер дела: `#j_idt36:j_idt37:edit-num`;
   - учитывать, что на странице есть reCAPTCHA.

## Риски

- reCAPTCHA может появляться каждый запуск, если Google считает автоматизацию подозрительной.
- Session может быть привязана к IP / профилю / fingerprint.
- Государственный сайт может менять JSF id / форму.
- Автоматическое captcha-solving нужно отдельно согласовать по юридическим и операционным рискам.
- Для боевого кабинета без реальной ЭЦП полноценного доступа не будет.