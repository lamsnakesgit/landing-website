# 📊 Аналитика трат API — план мониторинга

## Цели
- Получать уведомления в Telegram о тратах по каждому API
- Вести лог использования по сервисам
- Контролировать бюджет (free tier vs платное)

---

## Архитектура мониторинга

```
После каждой генерации (TTS / Imagen / Suno / Gemini)
    → Code нода: считает стоимость
    → Supabase INSERT → таблица api_usage

Cron: каждый день 23:00
    → Supabase SELECT SUM за сегодня
    → Telegram: "📊 Сводка трат за день"
```

---

## Таблица Supabase: api_usage

```sql
CREATE TABLE api_usage (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  service TEXT NOT NULL,          -- 'tts', 'imagen', 'suno', 'gemini'
  user_id TEXT,                   -- telegram user_id (для SaaS)
  units NUMERIC,                  -- символы / токены / штуки
  cost_usd NUMERIC(10, 6),        -- стоимость в $
  is_free_tier BOOLEAN DEFAULT false,
  metadata JSONB,                 -- доп. данные (голос, модель и т.д.)
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Индекс для быстрой агрегации по дате
CREATE INDEX idx_api_usage_date ON api_usage (created_at);
CREATE INDEX idx_api_usage_service ON api_usage (service);
```

---

## Цены для расчёта

| Сервис | Модель/Голос | Цена | Метрика | Free tier |
|--|--|--|--|--|
| **Google TTS** | Chirp3-HD | $0.000016/символ | символы | 1M симв/мес |
| **Google TTS** | Wavenet | $0.000016/символ | символы | 1M симв/мес |
| **Google Imagen 3** | imagen-3.0 | $0.04/изображение | штуки | нет |
| **Gemini Flash** | gemini-2.0-flash | $0.075/1M вх. токенов | токены | 1M токенов/день |
| **Gemini Flash** | gemini-2.0-flash | $0.30/1M вых. токенов | токены | — |
| **Suno/KIE** | V5 | по тарифу KIE | треки | зависит от плана |

---

## Code нода для логирования TTS

```javascript
// Вставить после ноды "Извлечь MP3" в любом TTS воркфлоу
const text = $('Конфиг').item.json.TEXT || '';
const voice = $('Конфиг').item.json.VOICE || '';
const chars = text.length;

// Chirp3-HD: $0.000016 за символ (WaveNet tier)
const costPerChar = 0.000016;
const costUsd = chars * costPerChar;
const isFree = chars <= 1000000; // в рамках free tier

return [{
  json: {
    service: 'tts',
    units: chars,
    cost_usd: costUsd,
    is_free_tier: isFree,
    metadata: { voice, chars }
  }
}];
```

---

## Code нода для логирования Imagen 3

```javascript
const costUsd = 0.04; // за одно изображение
return [{
  json: {
    service: 'imagen',
    units: 1,
    cost_usd: costUsd,
    is_free_tier: false,
    metadata: { model: 'imagen-3.0' }
  }
}];
```

---

## Дневной отчёт в Telegram (Cron 23:00)

```
📊 Сводка трат за 31.03.2026

🔊 TTS:      12,450 симв → $0.20 (free tier ✅)
🎨 Imagen:   3 картинки  → $0.12
🤖 Gemini:   45K токенов → $0.003
🎵 Suno:     2 трека     → по тарифу KIE

💰 Итого: ~$0.32
📅 Месяц: ~$4.80 (экстраполяция)

⚡ Free tier остаток:
- TTS: 987,550 симв (98.7%)
- Gemini: лимит не превышен ✅
```

---

## Воркфлоу n8n: daily_cost_report

### Ноды:
1. **Schedule Trigger** → каждый день 23:00
2. **Supabase** → SELECT агрегация за сегодня
3. **Code** → форматирование отчёта
4. **Telegram** → отправка в личку

### SQL запрос для агрегации:
```sql
SELECT 
  service,
  SUM(units) as total_units,
  SUM(cost_usd) as total_cost,
  BOOL_OR(is_free_tier) as has_free
FROM api_usage
WHERE created_at >= NOW()::date
GROUP BY service
ORDER BY total_cost DESC;
```

---

## TODO
- [ ] Создать таблицу api_usage в Supabase
- [ ] Добавить Code ноду логирования в test_google_tts.json
- [ ] Создать воркфлоу daily_cost_report.json
- [ ] Настроить бюджетный алерт в Google Cloud ($10/мес)
- [ ] Добавить логирование в Imagen воркфлоу
- [ ] Добавить логирование в Suno/KIE воркфлоу
