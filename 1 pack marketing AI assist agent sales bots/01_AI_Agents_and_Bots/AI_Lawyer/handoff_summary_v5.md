Проект: AI_Lawyer
Завершённость: [█████████░] 86% — VPS Kalkan handoff

# Handoff Summary v5 — AI_Lawyer / Судебный кабинет / KalkanCrypt

## 1. Короткий вывод

Проект перешёл от браузерной авторизации Playwright к правильной целевой архитектуре:

- **Playwright login каждые 2 минуты больше не считаем core-path.**
- Целевой путь: **server-side KalkanCrypt на VPS** подписывает XML через `.p12`, получает/обновляет `JSESSIONID`, а парсер работает 24/7.
- Локально уже подтверждено:
  - есть рабочий `.p12`;
  - пароль из `.env` валиден;
  - есть `sud_cookies.json`;
  - `JSESSIONID` открывает авторизованный `office.sud.kz`;
  - `/form/lawsuit/` доступен и содержит форму поиска судебных дел.
- На VPS Antigravity уже делал серию Docker/KalkanCrypt итераций и дошёл до финального теста `task-730`.

## 2. Текущий локальный state

### Изменённые/созданные файлы

- `AI_Lawyer/src/sud_parser.py`
  - `--mode court-acts`
  - `--mode iin`
  - `--cookies-json`
  - `--storage-state`
  - `--user-data-dir`
  - кабинетный flow через cookies
  - переход в `/form/lawsuit/`
  - поле ИИН/БИН: `#j_idt36:j_idt37:edit-iin`
  - поле номер дела: `#j_idt36:j_idt37:edit-num`

- `AI_Lawyer/src/ncalayer_mock.py`
  - читает `.env`;
  - видит `P12_PATH` / `TEST_KEY_PATH`;
  - использует `PASS_p12`;
  - не логирует пароль;
  - маскирует путь ключа;
  - подготовлен к `pykalkan.Adapter`;
  - поддерживает `createCAdESFromBase64` и `createCMSSignatureFromBase64`.

- `AI_Lawyer/.gitignore`
  - игнорирует `.env`;
  - игнорирует `*.p12`, `*.pfx`, `*.pem`, `*.key`;
  - игнорирует browser/session/cookie/runtime artifacts.

- `AI_Lawyer/PROGRESS.md`
  - обновлён live-статус;
  - добавлены команды cookies/P12/cabinet.

- `AI_Lawyer/ARCHITECTURE.md`
  - добавлен cookies JSON flow;
  - добавлен P12 / NCALayer / Kalkan section;
  - добавлен маршрут `/form/lawsuit/`.

- `AI_Lawyer/DEV_DIARY.md`
  - обновлён stage 3: cookie login + P12 key + кабинетный поиск дел.

### Локально подтверждено

```bash
cd AI_Lawyer
PYTHONDONTWRITEBYTECODE=1 python3 src/sud_parser.py \
  --mode iin \
  --headless \
  --cookies-json "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/sud_cookies.json"
```

Результат:

- `syntax_ok=1`
- `JSESSIONID` загружен из cookies JSON.
- Авторизованный кабинет распознан.
- ЭЦП-вход пропущен.
- `/form/lawsuit/` сохранён без запуска поиска.
- `/form/lawsuit/`:
  - status `200`;
  - содержит ИИН/БИН;
  - содержит номер дела;
  - содержит reCAPTCHA.

## 3. Секреты / ключи / cookies

### `.env`

Файл существует локально:

```text
AI_Lawyer/.env
```

Подтверждённые ключи без значений:

```env
PASS_p12=<set>
P12_PATH=<set>
TEST_KEY_PATH=<set>
```

### `.p12`

Новый актуальный ключ:

```text
/Users/higherpower/Downloads/GOST512_28412edbee5073856db88468b73dbd8f53bb9636.p12
```

Проверка пароля:

```text
p12_password_ok=1
```

### Cookies

Внешний cookie export:

```text
/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/sud_cookies.json
```

Содержит:

```text
JSESSIONID
domain=office.sud.kz
```

Значения cookies и пароль не логировать и не коммитить.

## 4. VPS / Antigravity статус по KalkanCrypt

По сообщению пользователя, Antigravity уже работал на VPS и сделал серию задач:

### Цель VPS-ветки

Не использовать браузер для логина. Вместо этого:

1. Python получает XML авторизации.
2. KalkanCrypt подписывает XML через `.p12`.
3. Скрипт отправляет signed XML во внутренний endpoint `office.sud.kz`.
4. Судебный кабинет выдаёт новый `JSESSIONID`.
5. Парсер обновляет session автоматически и работает 24/7.

### Важные итерации Antigravity

- `task-574` — быстрая загрузка нужной библиотеки KalkanCrypt вместо гигантского SDK.
- `task-583` — добавлен `libltdl.so.7`.
- `task-609` — переход на `ubuntu:20.04` из-за OpenSSL 1.1.
- `task-618` — попытка `amazonlinux:2`.
- `task-643` — AlmaLinux 8 + ручная сборка `libiconv`.
- `task-672` — `ldconfig` и `LD_LIBRARY_PATH`.
- `task-678` — preload `libiconv.so.2` через `RTLD_GLOBAL`.
- Step-by-step diagnostic — найден segfault around `KC_LoadKeyStore`.
- Full Kalkan stack — обнаружена нужная `libkalkancrypto.so` как backend.
- `task-730` — финальный тест: убрать `KC_Init`, грузить зависимости через `RTLD_GLOBAL`, вызывать `KC_LoadKeyStore` напрямую.

### Последний известный статус VPS

Последнее сообщение:

```text
Deploy final fix finished
```

Но в локальной сессии **не проверено**, прошёл ли `task-730` фактически с `SUCCESS` чтения `.p12`.

### Что нужно спросить/проверить на VPS

1. Есть ли commit-ы Antigravity по Docker/Kalkan?
2. Где репозиторий/папка на VPS?
3. Логи `task-730`.
4. Итоговый Dockerfile.
5. Итоговый Python diagnostic script.
6. Подтверждение:
   - `KC_LoadKeyStore` проходит;
   - `.p12` читается;
   - password валиден;
   - нет segfault;
   - signed payload генерируется.

## 5. Коммиты

Пользователь спросил: «комиты есть?»

Нужно проверить git:

```bash
cd AI_Lawyer
git status --short -- .
git log --oneline -5 -- .
```

На момент последней локальной проверки были изменения:

```text
M src/ncalayer_mock.py
M src/sud_parser.py
?? .gitignore
?? ARCHITECTURE.md
?? PROGRESS.md
...
```

То есть локальные изменения могли быть **не закоммичены**. Проверить актуально перед продолжением.

## 6. Что уже не является core path

Браузерный Playwright-login через UI и ручные логины каждые 2 минуты — не целевая архитектура.

Оставляем Playwright только для:

- диагностики DOM;
- первичного reverse-engineering;
- fallback semi-auto;
- страниц, где нет server-side endpoint;
- сохранения HTML/скриншотов.

Core path:

```text
KalkanCrypt VPS → signed XML → JSESSIONID → HTTP/Playwright session reuse → parser_tk.py / sud_parser.py
```

## 7. Следующий точный план

### Шаг 1 — проверить VPS результат `task-730`

Нужны логи:

```bash
# на VPS / в окружении Antigravity
docker ps -a
docker logs <kalkan_container>
```

Или команда/лог Antigravity task-730.

Definition of done:

```text
KC_LoadKeyStore SUCCESS
P12 key loaded
No segfault
No missing lib
```

### Шаг 2 — забрать Docker/Kalkan артефакты в проект

В AI_Lawyer стоит добавить:

```text
AI_Lawyer/kalkan/
  Dockerfile
  test_kalkan_load.py
  sign_xml.py
  README.md
```

Но не добавлять `.p12` и `.env`.

### Шаг 3 — реализовать session refresh service

Новый слой:

```text
src/kalkan_auth.py
```

Функции:

```python
load_key()
sign_auth_xml(xml: str) -> str
request_jsessionid() -> str
refresh_session_if_needed() -> str
```

### Шаг 4 — переписать parser_tk.py / sud_parser.py

Цель:

- не зависеть от ручного Playwright login;
- брать свежий `JSESSIONID`;
- ходить в `/form/lawsuit/`;
- искать по ИИН/БИН;
- парсить результаты;
- скачивать PDF.

### Шаг 5 — cron / n8n / SaaS

После стабильного refresh:

- запуск по cron/n8n;
- очередь задач;
- хранилище HTML/PDF;
- LLM-анализ стратегий/аргументов/пруфов.

## 8. Проверенные команды локально

### Smoke cookies-login кабинета

```bash
cd AI_Lawyer
PYTHONDONTWRITEBYTECODE=1 python3 src/sud_parser.py \
  --mode iin \
  --headless \
  --cookies-json "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/sud_cookies.json"
```

### GUI cookies-login кабинета

```bash
cd AI_Lawyer
PYTHONDONTWRITEBYTECODE=1 python3 src/sud_parser.py \
  --mode iin \
  --browser-channel chrome \
  --cookies-json "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/sud_cookies.json"
```

### Поиск по ИИН/БИН

```bash
cd AI_Lawyer
PYTHONDONTWRITEBYTECODE=1 python3 src/sud_parser.py \
  --mode iin \
  --iin "<IIN_OR_BIN>" \
  --browser-channel chrome \
  --cookies-json "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/sud_cookies.json"
```

### Проверка `.p12` без раскрытия пароля

```bash
cd AI_Lawyer
PASS_p12=$(python3 -c "from pathlib import Path; env={}; p=Path('.env');
for line in p.read_text().splitlines():
    line=line.strip()
    if line and not line.startswith('#') and '=' in line:
        k,v=line.split('=',1); env[k.strip()]=v.strip().strip('\"').strip(\"'\")
print(env.get('PASS_p12',''))") \
openssl pkcs12 \
  -in "/Users/higherpower/Downloads/GOST512_28412edbee5073856db88468b73dbd8f53bb9636.p12" \
  -passin env:PASS_p12 \
  -nokeys -clcerts -info -noout
```

## 9. Риски

- `JSESSIONID` может протухнуть.
- `/form/lawsuit/` содержит reCAPTCHA.
- KalkanCrypt зависит от старых системных библиотек:
  - OpenSSL 1.1 / legacy crypto;
  - `libltdl.so.7`;
  - `libiconv.so.2`;
  - `libkalkancrypto.so`;
  - порядок загрузки через `RTLD_GLOBAL`.
- Нельзя коммитить `.env`, `.p12`, cookies, session profiles.
- Локально мало места на диске; перед тяжёлыми тестами освободить место.

## 10. Важный next action

KalkanCrypt на VPS падает с segfault (exit 139). Автоматический 24/7 login через Kalkan — **blocked**.

**Рекомендуемый путь**: запустить парсинг через cookies-flow уже сегодня, а Kalkan чинить параллельно.

Следующий инженерный шаг:

```text
1. Добавить в sud_parser.py полноценный поиск по ИИН/БИН в /form/lawsuit/
2. Сохранять результаты поиска (HTML/JSON)
3. Парсить список дел из результатов
4. Скачивать PDF по каждому делу
5. Параллельно: отладить Kalkan segfault на VPS (strace + libltdl + libkalkancrypto.so)
```
