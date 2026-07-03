---
name: kie-ai-integration
description: Интеграция с kie.ai API для генерации изображений, видео, аудио и работы с AI моделями (Midjourney, Flux, Suno, Runway, Veo, Gemini и др.). Используй при работе с kie.ai API, настройке генерации контента или интеграции AI моделей.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# KIE.AI Integration Skill

> Comprehensive guide для интеграции kie.ai API — unified платформа для доступа к топовым AI моделям (изображения, видео, аудио, чат).

## Что такое kie.ai

**kie.ai** — это unified API платформа, предоставляющая доступ к лучшим AI моделям через единый интерфейс:

- **Image Models**: Midjourney, Flux, DALL-E, Stable Diffusion, Nano Banana, Seedream
- **Video Models**: Runway Gen-4, Google Veo 3, Kling, Grok Imagine, Sora 2, Hailuo
- **Audio Models**: Suno V4, ElevenLabs
- **Chat Models**: Gemini 2.5 Flash/Pro, Claude, GPT

### Преимущества
- ✅ Единый API для всех моделей
- ✅ Прозрачное ценообразование (credits-based)
- ✅ 99.9% uptime, низкая латентность
- ✅ Comprehensive документация
- ✅ Free trial без кредитной карты
- ✅ Webhook callbacks для async операций

---

## Быстрый старт

### 1. Регистрация и получение API ключа

```bash
# 1. Зарегистрироваться на https://kie.ai
# 2. Перейти в API Key Management: https://kie.ai/api-keys
# 3. Создать новый API ключ
# 4. Сохранить ключ в безопасном месте
```

**🚨 Безопасность:**
- NEVER хардкодить API ключ в коде
- NEVER коммитить ключ в Git
- MUST использовать переменные окружения
- SHOULD периодически ротировать ключи

### 2. Базовая аутентификация

**API Base URL:**
```
https://api.kie.ai
```

**Authorization Header:**
```bash
Authorization: Bearer YOUR_API_KEY
```

### 3. Проверка баланса кредитов

```bash
curl -X GET "https://api.kie.ai/common/credits" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "code": 200,
  "msg": "success",
  "data": 100
}
```

---

## Unified API Structure

Все модели в kie.ai следуют единой структуре:

### Шаг 1: Создание задачи (Create Task)

```bash
POST https://api.kie.ai/market/{model}/create
```

**Request:**
```json
{
  "prompt": "A futuristic city at sunset",
  "model_specific_params": "..."
}
```

**Response:**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "task_id": "abc123xyz"
  }
}
```

### Шаг 2: Проверка статуса (Query Task Status)

```bash
GET https://api.kie.ai/market/{model}/task/{task_id}
```

**Response (Processing):**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "status": "processing",
    "progress": 45
  }
}
```

**Response (Success):**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "status": "success",
    "result_url": "https://cdn.kie.ai/results/abc123.png",
    "metadata": {}
  }
}
```

### Шаг 3 (Опционально): Webhook Callbacks

Вместо polling можно использовать webhooks:

```json
{
  "prompt": "...",
  "callback_url": "https://your-domain.com/webhook"
}
```

**Webhook Payload:**
```json
{
  "task_id": "abc123xyz",
  "status": "success",
  "result_url": "https://cdn.kie.ai/results/abc123.png",
  "timestamp": 1736654400000
}
```

---

## Популярные модели и примеры

### 1. Midjourney API (Text-to-Image)

**Endpoint:** `POST /market/midjourney/create`

```bash
curl -X POST "https://api.kie.ai/market/midjourney/create" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "mj_txt2img",
    "prompt": "A serene mountain landscape at dawn, photorealistic",
    "aspect_ratio": "16:9"
  }'
```

**Task Types:**
- `mj_txt2img` — текст в изображение
- `mj_img2img` — изображение в изображение
- `mj_video` — изображение в видео

### 2. Flux.1 Kontext API (Image Editing)

**Endpoint:** `POST /market/flux-kontext/create`

```bash
curl -X POST "https://api.kie.ai/market/flux-kontext/create" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "flux-kontext-pro",
    "prompt": "Add a rainbow in the sky",
    "image_url": "https://example.com/image.jpg",
    "strength": 0.8
  }'
```

**Models:**
- `flux-kontext-pro` — баланс скорости и качества
- `flux-kontext-max` — максимальное качество

### 3. Runway Gen-4 Turbo (Text-to-Video)

**Endpoint:** `POST /market/runway-gen4/create`

```bash
curl -X POST "https://api.kie.ai/market/runway-gen4/create" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A drone flying over a futuristic city",
    "duration": 5,
    "resolution": "1080p"
  }'
```

### 4. Suno V4 API (Music Generation)

**Endpoint:** `POST /market/suno/create`

```bash
curl -X POST "https://api.kie.ai/market/suno/create" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Upbeat electronic dance music with synth melodies",
    "duration": 30,
    "style": "edm"
  }'
```

### 5. Google Veo 3 (Text-to-Video)

**Endpoint:** `POST /market/veo3/create`

```bash
curl -X POST "https://api.kie.ai/market/veo3/create" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cat playing piano in a jazz club",
    "duration": 10,
    "aspect_ratio": "16:9"
  }'
```

### 6. Gemini 2.5 Pro (Chat Completion)

**Endpoint:** `POST /market/gemini/chat`

```bash
curl -X POST "https://api.kie.ai/market/gemini/chat" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Explain quantum computing in simple terms"
      }
    ],
    "stream": false,
    "reasoning_effort": "high"
  }'
```

**Features:**
- `stream: true` — streaming responses
- `reasoning_effort: "high"` — глубокое рассуждение
- `response_format` — structured JSON output
- `tools` — Google Search, Function Calling

---

## Common API Utilities

### Получение download ссылки

Конвертирует kie.ai URL в temporary download link (действителен 20 минут):

```bash
curl -X POST "https://api.kie.ai/common/download" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://cdn.kie.ai/results/abc123.png"
  }'
```

**Response:**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "download_url": "https://cdn.kie.ai/temp/xyz789.png?expires=1736655000"
  }
}
```

**🚨 Важно:**
- Ссылка действительна только 20 минут
- MUST скачивать файл сразу после получения URL
- SHOULD кэшировать скачанный контент

---

## Интеграция с N8N

### Базовый workflow для генерации изображений

**Структура:**
1. **Webhook/Form Trigger** — получение запроса
2. **HTTP Request (Create Task)** — создание задачи
3. **Wait** — пауза 10 секунд
4. **HTTP Request (Check Status)** — проверка статуса
5. **IF Node** — проверка `status === "success"`
6. **Loop** — повторять шаг 3-5 пока не `success`
7. **Return Result** — вернуть `result_url`

### Пример HTTP Request ноды (Create Task)

```json
{
  "method": "POST",
  "url": "https://api.kie.ai/market/midjourney/create",
  "authentication": "genericCredentialType",
  "genericAuthType": "httpHeaderAuth",
  "headers": {
    "Authorization": "Bearer {{$env.KIE_API_KEY}}"
  },
  "body": {
    "task_type": "mj_txt2img",
    "prompt": "={{$json.prompt}}",
    "aspect_ratio": "16:9"
  }
}
```

### Пример HTTP Request ноды (Check Status)

```json
{
  "method": "GET",
  "url": "https://api.kie.ai/market/midjourney/task/={{$json.task_id}}",
  "authentication": "genericCredentialType",
  "genericAuthType": "httpHeaderAuth",
  "headers": {
    "Authorization": "Bearer {{$env.KIE_API_KEY}}"
  }
}
```

### Использование Webhook Callbacks

**Преимущество:** Не нужно polling, kie.ai сам отправит результат.

```json
{
  "method": "POST",
  "url": "https://api.kie.ai/market/midjourney/create",
  "body": {
    "task_type": "mj_txt2img",
    "prompt": "={{$json.prompt}}",
    "callback_url": "https://your-n8n.com/webhook/kie-callback"
  }
}
```

**Webhook Trigger в N8N:**
- Path: `/webhook/kie-callback`
- Method: `POST`
- Response: `200 OK`

---

## Pricing и Credits

### Стоимость по типам моделей

| Тип модели | Credits за генерацию |
|---|---|
| **Image Models** | 10-50 credits |
| **Video Models** | 100-500 credits |
| **Audio Models** | 20-100 credits |
| **Chat Models** | Per token (0.01-0.1 credits/1K tokens) |

### Мониторинг кредитов

```bash
# Проверка баланса
curl -X GET "https://api.kie.ai/common/credits" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Best Practices:**
- SHOULD проверять баланс перед каждой генерацией
- MUST устанавливать low-credit warnings
- SHOULD планировать пополнение заранее
- MUST реализовать graceful degradation при нехватке кредитов

---

## Error Handling

### Типичные ошибки

| Code | Описание | Решение |
|---|---|---|
| `401` | Unauthorized | Проверить API ключ |
| `402` | Insufficient credits | Пополнить баланс |
| `422` | Validation error | Проверить параметры запроса |
| `429` | Rate limit exceeded | Добавить retry с backoff |
| `500` | Internal server error | Повторить запрос через 5-10 сек |

### Retry Strategy

```javascript
async function createTaskWithRetry(params, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch('https://api.kie.ai/market/midjourney/create', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.KIE_API_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
      });
      
      if (response.ok) {
        return await response.json();
      }
      
      if (response.status === 429) {
        // Rate limit — exponential backoff
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
        continue;
      }
      
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}
```

---

## Best Practices

### 1. Безопасность

```bash
# ✅ ПРАВИЛЬНО — переменные окружения
export KIE_API_KEY="your-api-key-here"

# ❌ НЕПРАВИЛЬНО — хардкод в коде
const API_KEY = "<REDACTED>"
```

### 2. Async операции

```javascript
// ✅ ПРАВИЛЬНО — использовать webhooks
const response = await createTask({
  prompt: "...",
  callback_url: "https://your-domain.com/webhook"
});

// ❌ НЕПРАВИЛЬНО — бесконечный polling
while (true) {
  const status = await checkStatus(taskId);
  if (status === "success") break;
  await sleep(1000); // Нагрузка на API
}
```

### 3. Обработка результатов

```javascript
// ✅ ПРАВИЛЬНО — скачать и сохранить
const downloadUrl = await getDownloadLink(resultUrl);
const file = await fetch(downloadUrl);
const buffer = await file.arrayBuffer();
await fs.writeFile('result.png', Buffer.from(buffer));

// ❌ НЕПРАВИЛЬНО — полагаться на временную ссылку
// Ссылка истекает через 20 минут!
```

### 4. Мониторинг кредитов

```javascript
// ✅ ПРАВИЛЬНО — проверка перед генерацией
const credits = await checkCredits();
if (credits < 50) {
  throw new Error('Недостаточно кредитов для генерации');
}

// ❌ НЕПРАВИЛЬНО — генерация без проверки
// Может привести к 402 ошибке в процессе
```

---

## Интеграция с VPS сервисами

### Использование с N8N на VPS

**N8N URL:** `https://<YOUR_N8N_DOMAIN>`

**Пример workflow:**
1. Webhook Trigger принимает запрос
2. HTTP Request создаёт задачу в kie.ai
3. Webhook Callback получает результат
4. Scraper Server (`http://<YOUR_VPS_IP>:9111`) обрабатывает результат
5. Telegram API отправляет уведомление

### Environment Variables для N8N

```bash
# В N8N Settings → Environment Variables
KIE_API_KEY=your-kie-api-key
KIE_WEBHOOK_URL="<REDACTED>"
```

---

## Документация и поддержка

### Официальные ресурсы

- **Документация:** https://docs.kie.ai
- **API Reference:** https://docs.kie.ai/market/quickstart
- **API Key Management:** https://kie.ai/api-keys
- **Status Page:** https://status.kie.ai
- **Email Support:** support@kie.ai
- **Discord Community:** https://discord.gg/kie-ai

### Полезные ссылки

- **Pricing:** https://kie.ai/pricing
- **Models Catalog:** https://kie.ai/models
- **Changelog:** https://docs.kie.ai/changelog
- **API Updates:** https://docs.kie.ai/updates

---

## Troubleshooting

### Проблема: Task застрял в "processing"

**Решение:**
1. Проверить статус через 30-60 секунд
2. Если > 5 минут — задача могла упасть
3. Создать новую задачу с теми же параметрами
4. Связаться с support@kie.ai если проблема повторяется

### Проблема: 422 Validation Error

**Решение:**
1. Проверить все required параметры
2. Проверить формат параметров (string, number, array)
3. Проверить допустимые значения (aspect_ratio, duration, etc.)
4. Изучить model-specific документацию

### Проблема: Download link expired

**Решение:**
1. Запросить новую download ссылку через `/common/download`
2. Скачать файл немедленно (ссылка действует 20 минут)
3. Сохранить файл локально или в облако

---

## Примеры использования

### Python

```python
import requests
import os
import time

API_KEY = os.environ.get('KIE_API_KEY')
BASE_URL = 'https://api.kie.ai'

def create_image(prompt):
    """Создать изображение через Midjourney API"""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Создание задачи
    response = requests.post(
        f'{BASE_URL}/market/midjourney/create',
        headers=headers,
        json={
            'task_type': 'mj_txt2img',
            'prompt': prompt,
            'aspect_ratio': '16:9'
        }
    )
    
    task_id = response.json()['data']['task_id']
    print(f'Task created: {task_id}')
    
    # Polling статуса
    while True:
        status_response = requests.get(
            f'{BASE_URL}/market/midjourney/task/{task_id}',
            headers=headers
        )
        
        data = status_response.json()['data']
        
        if data['status'] == 'success':
            return data['result_url']
        elif data['status'] == 'failed':
            raise Exception(f"Task failed: {data.get('error')}")
        
        print(f"Progress: {data.get('progress', 0)}%")
        time.sleep(10)

# Использование
image_url = create_image('A futuristic city at sunset')
print(f'Image ready: {image_url}')
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const API_KEY = process.env.KIE_API_KEY;
const BASE_URL = 'https://api.kie.ai';

async function createVideo(prompt) {
  const headers = {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
  };
  
  // Создание задачи с webhook
  const response = await axios.post(
    `${BASE_URL}/market/runway-gen4/create`,
    {
      prompt: prompt,
      duration: 5,
      callback_url: 'https://your-domain.com/webhook/kie'
    },
    { headers }
  );
  
  const taskId = response.data.data.task_id;
  console.log(`Task created: ${taskId}`);
  
  return taskId;
}

// Webhook handler (Express.js)
app.post('/webhook/kie', (req, res) => {
  const { task_id, status, result_url } = req.body;
  
  if (status === 'success') {
    console.log(`Video ready: ${result_url}`);
    // Обработка результата
  }
  
  res.status(200).send('OK');
});
```

---

## Заключение

**kie.ai** — это мощная unified платформа для работы с топовыми AI моделями через единый API. Следуя этому skill, ты сможешь:

✅ Быстро интегрировать любую AI модель  
✅ Эффективно управлять async операциями  
✅ Правильно обрабатывать ошибки и retry  
✅ Мониторить кредиты и оптимизировать расходы  
✅ Интегрировать с N8N и другими сервисами  

**Следующие шаги:**
1. Получить API ключ на https://kie.ai
2. Протестировать в Playground
3. Интегрировать в свой проект
4. Настроить мониторинг и alerts

**Поддержка:** support@kie.ai | https://docs.kie.ai
