# Nano Banana 2 на Vertex AI — ошибки и решения

## Проблема 1: Неправильный регион (404)
**Симптом:** `gemini-3.1-flash-image` возвращал 404 на `us-central1`
**Причина:** Nano Banana 2 работает **только** через `global` endpoint, не через региональные
**Решение:** LOCATION = `global`, а не `us-central1`
**Урок:** Всегда проверять supported regions в документации перед первым вызовом

## Проблема 2: Путаница с model ID
**Симптом:** Долго не могли найти правильную модель
**Причина:** Есть 3 модели:
- `gemini-2.5-flash-image` = **Nano Banana** (старая, плохая кириллица)
- `gemini-3.1-flash-image` = **Nano Banana 2** (нужная, хорошая кириллица)
- `gemini-3-pro-image` = **Nano Banana Pro** (пока не включена)

**Решение:** Понять соответствия model ID → display name через `GET /v1beta/models`
**Урок:** display name в API = "Nano Banana 2" а model ID = `gemini-3.1-flash-image`

## Проблема 3: API endpoint путаница
**Симптом:** Nano Banana 2 не работал на `us-central1-aiplatform.googleapis.com` но работал на `aiplatform.googleapis.com`
**Причина:** Документация Vertex AI указывает региональные endpoints, но `gemini-3.1-flash-image` поддерживает ТОЛЬКО `global`
**Решение:** Использовать `https://aiplatform.googleapis.com/v1/projects/{id}/locations/global/...`
**Урок:** Не полагаться на дефолтные примеры — читать supported regions для каждой модели

## Проблема 4: Vertex AI vs AI Studio путаница
**Симптом:** $190 free trial на Vertex AI не работал для Nano Banana 2
**Причина:** Nano Banana 2 доступен на Vertex AI ($190 credits) но **не включён** в Model Garden по умолчанию. AI Studio имеет отдельный биллинг
**Решение:** Использовать global endpoint на `aiplatform.googleapis.com` с service account
**Урок:** Vertex AI и AI Studio = разные API endpoints и разные биллинг системы

## Проблема 5: Rate limit 429
**Симптом:** Запросы падали с 429 после 1-2 успешных
**Решение:** Добавить retry логику с паузами 30-150с и 15с между слайдами
**Урок:** Nano Banana 2 имеет rate limit ~1 запрос в 15-30 секунд

## Проблема 6: Кириллический текст говно на старой Nano Banana
**Симптом:** Текст на русском ломался на `gemini-2.5-flash-image`
**Решение:** Перейти на `gemini-3.1-flash-image` (Nano Banana 2) — кириллица значительно лучше
**Урок:** `gemini-2.5-flash-image` != `gemini-3.1-flash-image`. Разные модели.