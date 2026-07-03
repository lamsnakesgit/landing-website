---
name: transcript-analyzer
description: Анализ, суммаризация и извлечение ключевых моментов из транскриптов видео (YouTube) или аудио.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Transcript Analyzer Skill

## Источники транскриптов

### Локальный API (YT Transcript на VPS)
```bash
# Получить транскрипт на английском
curl "http://<YOUR_VPS_IP>:9222/transcript/{videoId}?lang=en&format=text"

# Получить транскрипт на русском
curl "http://<YOUR_VPS_IP>:9222/transcript/{videoId}?lang=ru&format=text"

# Получить с таймкодами (JSON формат)
curl "http://<YOUR_VPS_IP>:9222/transcript/{videoId}?lang=en&format=json"

# Проверить доступные языки
curl "http://<YOUR_VPS_IP>:9222/languages/{videoId}"
```

### Извлечение videoId из URL
```javascript
// YouTube URL → videoId
function extractVideoId(url) {
  const patterns = [
    /(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})/,
    /(?:youtu\.be\/)([a-zA-Z0-9_-]{11})/,
    /(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
  ];
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) return match[1];
  }
  return null;
}
```

### Invidious API (альтернатива)
```bash
# Информация о видео
curl "http://<YOUR_VPS_IP>:3001/api/v1/videos/{videoId}"

# Поиск видео
curl "http://<YOUR_VPS_IP>:3001/api/v1/search?q=topic&type=video"
```

## Очистка транскрипта
```python
import re

def clean_transcript(text: str) -> str:
    # Удалить таймкоды [00:01:23]
    text = re.sub(r'\[\d{2}:\d{2}(:\d{2})?\]', '', text)
    # Удалить метки спикеров
    text = re.sub(r'^(Speaker \d+|SPEAKER_\d+):\s*', '', text, flags=re.MULTILINE)
    # Нормализовать пробелы
    text = re.sub(r'\s+', ' ', text).strip()
    # Удалить [музыка], [аплодисменты] и подобные пометки
    text = re.sub(r'\[.*?\]', '', text)
    return text
```

## Стратегии суммаризации

### Для коротких транскриптов (< 4000 токенов)
Отправляй целиком в LLM с промптом для анализа.

### Map-Reduce (для длинных транскриптов)
```python
def map_reduce_summarize(text: str, chunk_size: int = 3000) -> str:
    # 1. MAP: Разбить на чанки и суммаризировать каждый
    chunks = chunk_text(text, chunk_size, overlap=200)
    summaries = []
    for i, chunk in enumerate(chunks):
        summary = call_llm(f"""
Суммаризируй этот фрагмент (часть {i+1} из {len(chunks)}):
{chunk}

Выдели 3-5 ключевых пунктов.
""")
        summaries.append(summary)

    # 2. REDUCE: Объединить все саммари в финальное
    combined = "\n\n".join(summaries)
    final = call_llm(f"""
На основе этих промежуточных саммари создай финальную суммаризацию:
{combined}

Формат:
1. Краткое содержание (3-4 предложения)
2. Основные темы
3. Ключевые выводы
4. Упомянутые ресурсы
""")
    return final
```

### Refine (последовательное улучшение)
```python
def refine_summarize(text: str, chunk_size: int = 3000) -> str:
    chunks = chunk_text(text, chunk_size, overlap=200)
    summary = ""
    for i, chunk in enumerate(chunks):
        if i == 0:
            summary = call_llm(f"Суммаризируй:\n{chunk}")
        else:
            summary = call_llm(f"""
Текущее саммари: {summary}

Дополни его на основе нового фрагмента:
{chunk}

Обнови саммари, добавив новую информацию.
""")
    return summary
```

## Чанкинг текста
```python
def chunk_text(text: str, chunk_size: int = 3000, overlap: int = 200) -> list:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap
    return [c for c in chunks if c.strip()]
```

## Промпты для анализа

### Общий анализ
```
Проанализируй транскрипт видео и предоставь:

1. **Краткое содержание** (3-4 предложения).
2. **Основные темы** (bullet points).
3. **Ключевые выводы и инсайты**.
4. **Упомянутые инструменты, книги или ссылки**.
5. **Action Items** (что можно применить на практике).

Транскрипт:
{transcript}
```

### Извлечение фактов
```
Извлеки из транскрипта все конкретные факты, числа, даты, имена и ссылки.
Формат: JSON массив объектов { "type": "fact|number|date|name|link", "value": "...", "context": "..." }

Транскрипт:
{transcript}
```

### Создание структурированных заметок
```
Преврати этот транскрипт в структурированные заметки формата Markdown:
- Используй заголовки для тем
- Bullet points для ключевых идей
- Блоки кода для технических примеров
- Цитаты (>) для важных высказываний

Транскрипт:
{transcript}
```

### Поиск противоречий
```
Проанализируй транскрипт и найди:
1. Внутренние противоречия (спикер говорит одно, потом другое).
2. Спорные утверждения (без источников/доказательств).
3. Потенциальные ошибки (фактические неточности).

Транскрипт:
{transcript}
```

## Полный пайплайн
```bash
# 1. Получить транскрипт
TRANSCRIPT=$(curl -s "http://<YOUR_VPS_IP>:9222/transcript/dQw4w9WgXcQ?lang=en&format=text")

# 2. Сохранить в файл
echo "$TRANSCRIPT" > /tmp/transcript.txt

# 3. Прочитать и проанализировать через LLM (Cline сам может это сделать)
```

## Форматирование результата
Всегда возвращай результат в структурированном Markdown:
- Заголовки для разделов
- Bullet points для списков
- **Жирный** для ключевых терминов
- `Код` для технических терминов
- > Цитаты для важных высказываний спикера

## Лучшие практики
- 🚨 Всегда проверяй доступные языки перед запросом транскрипта.
- Для видео без субтитров — используй Whisper API для распознавания речи.
- Map-Reduce лучше для длинных видео (>30 мин), Refine — для средних (10-30 мин).
- Сохраняй исходный транскрипт перед обработкой (на случай повторного анализа).
- Указывай источник (URL видео, автор, дата) в результате анализа.
