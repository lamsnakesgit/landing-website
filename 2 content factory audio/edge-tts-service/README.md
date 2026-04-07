# Edge TTS Service — Railway Deploy

Бесплатный TTS сервис на базе Microsoft Edge TTS.  
Русские нейросетевые голоса, без API ключей.

## Деплой на Railway

1. Залей папку `edge-tts-service` в GitHub репозиторий
2. Railway → New Project → Deploy from GitHub
3. Выбери репозиторий → Railway автоматически найдёт Dockerfile
4. После деплоя получишь URL типа: `https://your-app.railway.app`

## Эндпоинты

### GET /
Health check: `{"status": "ok"}`

### GET /voices
Список всех русских голосов

### POST /tts
Генерация аудио MP3

```json
{
  "text": "Привет! Я голосовой ассистент Ланы.",
  "voice": "ru-RU-SvetlanaNeural",
  "rate": "-5%",
  "volume": "+0%"
}
```

Возвращает: бинарный MP3

## Русские голоса

| Голос | Пол | Описание |
|--|--|--|
| `ru-RU-SvetlanaNeural` | Женский | Мягкий, чёткий ✅ |
| `ru-RU-DmitryNeural` | Мужской | Глубокий, чёткий ✅ |
| `ru-RU-DariyaNeural` | Женский | Тёплый |

## n8n HTTP Request нода

**URL:** `https://your-app.railway.app/tts`  
**Method:** POST  
**Body:**
```json
{
  "text": "{{ $json.part }}",
  "voice": "ru-RU-SvetlanaNeural",
  "rate": "-5%"
}
```
**Response Format:** File (бинарный)

## Параметр rate (скорость)

- `-10%` — медленнее
- `-5%` — чуть медленнее (рекомендуется)
- `+0%` — нормально
- `+10%` — быстрее
