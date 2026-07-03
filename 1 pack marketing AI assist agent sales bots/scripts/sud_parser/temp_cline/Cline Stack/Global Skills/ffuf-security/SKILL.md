---
name: ffuf-security
description: Использование FFUF для фаззинга веб-приложений, поиска скрытых директорий и уязвимостей.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# FFUF Security Skill

FFUF (Fuzz Faster U Fool) — быстрый веб-фаззер на Go. Ключевое слово `FUZZ` заменяется значениями из словаря.

## Базовые команды

### Поиск директорий
```bash
ffuf -u https://target.com/FUZZ -w /path/to/wordlist.txt
```

### Поиск файлов с расширениями
```bash
ffuf -u https://target.com/FUZZ -w wordlist.txt -e .php,.html,.txt,.bak,.js,.json
```

### Фаззинг GET-параметров
```bash
ffuf -u https://target.com/api?FUZZ=test -w params.txt
```

### Фаззинг значений параметров
```bash
ffuf -u https://target.com/api?id=FUZZ -w numbers.txt
```

## Продвинутые техники

### Рекурсивное сканирование
```bash
ffuf -u https://target.com/FUZZ -w wordlist.txt -recursion -recursion-depth 3
```
🚨 Всегда ограничивай глубину через `-recursion-depth`, иначе сканирование может быть бесконечным.

### Virtual Host (VHost) Discovery
Поиск скрытых поддоменов через фаззинг заголовка Host:
```bash
ffuf -u https://target.com -H "Host: FUZZ.target.com" -w subdomains.txt -fs 4242
```
`-fs` фильтрует по размеру ответа дефолтной страницы.

### POST Data Fuzzing
```bash
ffuf -u https://target.com/login -X POST \
  -d "username=admin&password=FUZZ" \
  -w passwords.txt -fc 401
```

### Fuzzing с JSON body
```bash
ffuf -u https://target.com/api/search -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "FUZZ"}' \
  -w wordlist.txt
```

### Множественные точки фаззинга
```bash
ffuf -u https://target.com/FUZZ1/FUZZ2 \
  -w dirs.txt:FUZZ1 \
  -w files.txt:FUZZ2
```

### Фаззинг HTTP-заголовков
```bash
ffuf -u https://target.com/admin -H "X-Forwarded-For: FUZZ" -w ips.txt
```

## Фильтрация результатов

### Match (показать только)
- `-mc 200,301,302,403` — Match Status Code
- `-ms 1234` — Match Size
- `-mw 50` — Match Words
- `-ml 10` — Match Lines
- `-mr "success"` — Match Regex

### Filter (скрыть)
- `-fc 404,403` — Filter Status Code
- `-fs 4242` — Filter Size (размер дефолтной страницы)
- `-fw 12` — Filter Words
- `-fl 5` — Filter Lines
- `-fr "not found"` — Filter Regex

**Лайфхак:** Сначала запусти без фильтров, посмотри размер/слова дефолтного ответа, потом добавь `-fs` или `-fw`.

## Контроль скорости
```bash
# Ограничить до 100 запросов в секунду
ffuf -u https://target.com/FUZZ -w wordlist.txt -rate 100

# Ограничить потоки (по умолчанию 40)
ffuf -u https://target.com/FUZZ -w wordlist.txt -t 10

# Задержка между запросами (мс)
ffuf -u https://target.com/FUZZ -w wordlist.txt -p 0.1
```

## Вывод результатов
```bash
# JSON
ffuf -u https://target.com/FUZZ -w wordlist.txt -o results.json -of json

# CSV
ffuf -u https://target.com/FUZZ -w wordlist.txt -o results.csv -of csv

# HTML
ffuf -u https://target.com/FUZZ -w wordlist.txt -o results.html -of html
```

## Интеграция

### С Burp Suite (через прокси)
```bash
ffuf -u https://target.com/FUZZ -w wordlist.txt -x http://127.0.0.1:8080
```

### С кастомными cookies
```bash
ffuf -u https://target.com/FUZZ -w wordlist.txt -b "session=abc123; token=xyz"
```

### С Bearer Token
```bash
ffuf -u https://target.com/api/FUZZ -w wordlist.txt -H "Authorization: Bearer <REDACTED>"
```

## Словари (Wordlists)
Рекомендуемые из SecLists:
- `Discovery/Web-Content/raft-large-directories.txt` — директории
- `Discovery/Web-Content/raft-large-files.txt` — файлы
- `Discovery/Web-Content/burp-parameter-names.txt` — параметры
- `Discovery/Web-Content/common.txt` — общий словарь
- `Discovery/DNS/subdomains-top1million-5000.txt` — поддомены

## Установка
```bash
# macOS
brew install ffuf

# Go
go install github.com/ffuf/ffuf/v2@latest

# SecLists
git clone https://github.com/danielmiessler/SecLists.git
```
