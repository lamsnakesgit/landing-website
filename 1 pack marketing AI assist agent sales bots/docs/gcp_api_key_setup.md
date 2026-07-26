# Настройка GCP API Key для нового Free Trial проекта

## Проблема
Политика организации `iam.disableServiceAccountKeyCreation` блокирует создание service account ключей.
**API Key — НЕ блокируется**, это другой тип ключа.

## Как создать API Key для нового проекта

### Способ 1: Google AI Studio (быстрый)

1. Открой https://aistudio.google.com/apikey
2. Войди под **новым** Free Trial аккаунтом
3. Нажми **"Create API Key"**
4. Выбери новый проект (или создай новый проект)
5. Скопируй ключ (начинается с `AIza...`)
6. Пришли мне — я добавлю в `.env`

### Способ 2: GCP Console

1. https://console.cloud.google.com/apis/credentials
2. Выбери **новый Free Trial проект** сверху
3. Нажми **+ Create Credentials → API Key**
4. Скопируй ключ

## Что этот ключ даёт

| Сервис | Работает? |
|--------|-----------|
| Gemini 1.5 Flash/Pro | ✅ |
| Gemini 2.0 Flash | ✅ |
| Gemini TTS (голоса) | ✅ |
| Imagen | ❌ (только Vertex AI) |
| Nano Banana 2 | ❌ (через AIHubMix) |

## Что с Nano Banana и остальным

Nano Banana (gemini-3.1-flash-image) лучше через **AIHubMix** — у тебя уже есть `AIHUBMIX_API_KEY` в `.env`.
Голоса Gemini TTS — работают через API key.

## Старые SA-файлы

Переименованы в `*_expired.json` — не удаляю, на всякий случай.