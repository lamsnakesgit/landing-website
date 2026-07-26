# Гайд: Авторизация в Судебном кабинете (office.sud.kz) через KalkanCrypt без браузера

**Дата:** Июль 2026
**Статус:** Успешно реализовано.

Этот документ описывает полный процесс, ошибки и решения при настройке автоматической авторизации в Судебном кабинете РК через ЭЦП (GOST), минуя NCALayer и Playwright/Selenium. Это позволяет парсить данные на сервере (VPS) полностью в headless-режиме, используя Python и нативную библиотеку KalkanCrypt.

---

## 🛑 Проблема
Судебный кабинет РК использует:
1. **JavaServer Faces (JSF) + RichFaces** для фронтенда. Это значит, что обычные `POST` запросы не работают. Формы генерируются динамически, их ID меняются (например, `j_idt73:j_idt93`), а сервер ожидает строгий AJAX-протокол.
2. **XML-подпись (GOST)** для авторизации. NCALayer локально подписывает challenge (блок `loginInfoForSign`), который выдает сервер. На сервере без UI запустить NCALayer сложно.

---

## ✅ Решение: Архитектура
Мы используем:
- **Docker-контейнер на базе AlmaLinux 8** (так как проприетарные библиотеки KalkanCrypt скомпилированы под RHEL/CentOS).
- **KalkanCrypt C-Wrapper (`kalkan_sign.c`)** для генерации подписи XML напрямую из `.p12` файла ЭЦП.
- **Python `requests` + `BeautifulSoup`** для имитации RichFaces AJAX-запросов и сохранения сессии.

---

## 🛠 Пошаговый алгоритм авторизации

### Шаг 1. Получение Challenge (XML для подписи)
Делаем обычный `GET` запрос на `https://office.sud.kz/index.xhtml`.
Сервер возвращает страницу, в которой скрыт `input` с ID, заканчивающимся на `loginInfoForSign`. В его `value` лежит XML вида:
`<loginInfoForSign>...</loginInfoForSign>`
Из этого же `GET` запроса мы должны вытащить `javax.faces.ViewState` и **динамические ID формы**.

### Шаг 2. Подпись XML (KalkanCrypt)
Мы передаем этот XML в нашу C-утилиту `kalkan_sign`.
**Секреты успеха (как мы победили ошибки):**
- **Ошибка `0x8f0003b` (невалидный сертификат / цепочка)**: KalkanCrypt требует, чтобы цепочка доверия была валидна.
- **Решение 1:** Загружать промежуточные и корневые сертификаты НУЦ РК в форматах `.pem` (не `.cer` / `.der`), используя флаги `KC_CERT_CA` (0x00000201) и `KC_CERT_INTERMEDIATE` (0x00000202).
- **Решение 2:** Сертификаты НУЦ РК ОБЯЗАТЕЛЬНО должны быть добавлены в системное хранилище доверенных сертификатов ОС (`update-ca-trust` в Linux). В Dockerfile это делается так:
  ```dockerfile
  RUN find /certs -name "*.pem" -exec cp {} /usr/share/pki/ca-trust-source/anchors/ \; && \
      find /certs -name "*.cer" -exec cp {} /usr/share/pki/ca-trust-source/anchors/ \; && \
      update-ca-trust extract
  ```
- **Функция подписи:** Используем `SignXML` (а не `SignData`). Подписываем с флагом `0` (или `KC_SIGN_DRAFT`).

### Шаг 3. Отправка AJAX (RichFaces) запроса
Мы получили подписанный XML (2741 байт). Теперь его нужно отправить обратно.
**КРИТИЧЕСКИЕ ТРЕБОВАНИЯ к POST-запросу:**
1. **Заголовки:**
   - `Faces-Request: partial/ajax` (ОБЯЗАТЕЛЬНО! Без него сервер вернет всю страницу или 500 ошибку).
   - `Content-Type: application/x-www-form-urlencoded`
2. **Payload (тело запроса):**
   - Должно содержать все `hidden` поля оригинальной формы (включая `javax.faces.ViewState`).
   - Имя поля подписанного XML: `{form_id}:{button_id}:signedXml`
   - Имя поля сертификата: `{form_id}:{button_id}:cert` (достаточно извлечь из подписанного XML содержимое тега `<X509Certificate>`).
   - Специфичные JSF параметры:
     - `javax.faces.partial.ajax=true`
     - `javax.faces.source={button_id}`
     - `javax.faces.partial.execute=@all`
     - `javax.faces.partial.render=@all`
     - `{button_id}={button_id}` (имитация нажатия кнопки).

Пример динамического маппинга полей (см. `sud_parser.py`):
```python
button_id = "j_idt73:j_idt93:j_idt94:j_idt118"
form_id = "j_idt73:j_idt93"
ajax_data = {
    "javax.faces.partial.ajax": "true",
    "javax.faces.source": button_id,
    "javax.faces.partial.execute": "@all",
    "javax.faces.partial.render": "@all",
    button_id: button_id,
    f"{form_id}:{form_id.split(':')[-1]+'4'}:signedXml": signed_xml, # пример
    # + все hidden inputs из формы
}
```

### Шаг 4. Парсинг данных
После получения `HTTP 200` на AJAX запрос (размер ответа обычно небольшой XML с тегом `<partial-response>`), сессия считается авторизованной.
Дальше мы просто делаем `GET /ru/case/list` или `/lawyerRoom/myCase.xhtml` и парсим HTML с помощью `BeautifulSoup` (bs4), извлекая таблицы и ссылки.

---

## 🛑 Частые ошибки и их решения
1. **HTTP 400 Bad Request при отправке POST:**
   - Вы отправили не AJAX-запрос. Добавьте `Faces-Request: partial/ajax`.
   - Забыли `javax.faces.ViewState`.
2. **KalkanCrypt ругается на сертификат (0x8f0003b):**
   - Убедитесь, что передаете `.p12`, а не пароль в неправильном месте.
   - Запустите `update-ca-trust` внутри контейнера. ОС должна доверять сертификатам НУЦ.
   - Проверьте, что загружаете `.pem` версии корневых сертификатов через `KC_LoadCertFromFile`.
3. **Парсер не может найти ID формы:**
   - Судебный кабинет часто обновляет интерфейс (или ID меняются динамически). Обязательно используйте BeautifulSoup или regex для поиска `input[id$="loginInfoForSign"]` и вычисляйте имя формы отталкиваясь от него, а не зашивайте `j_idt73:j_idt93` жестко в код.

---

## Структура файлов на сервере
- `deploy.py`: Автоматизирует копирование ключей/скриптов и сборку Docker-образа на VPS.
- `scripts/sud_parser/kalkan_docker/Dockerfile`: Настраивает CentOS/AlmaLinux, ставит либы XMLSec и KalkanCrypt.
- `scripts/sud_parser/kalkan_docker/kalkan_sign.c`: Си-код обертки над Kalkan SDK.
- `scripts/sud_parser/kalkan_docker/sud_parser.py`: Основной Python-воркер (AJAX авторизация, навигация, парсинг BS4).

---

> **Внимание:** Берегите пароли от ЭЦП и не коммитьте `*.p12` ключи в открытые репозитории! Используйте `.env` или переменные окружения CI/CD.
