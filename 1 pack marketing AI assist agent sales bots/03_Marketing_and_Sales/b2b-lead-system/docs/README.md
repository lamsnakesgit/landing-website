# B2B Lead Generation System
### Парсер вакансий + Анализатор групп | hh.kz · adata.kz · 2ГИС · Telegram · WhatsApp

---

## Что это

Автоматическая машина для поиска B2B-лидов из двух источников:

1. **Парсер вакансий** — hh.kz, adata.kz, 2ГИС/Google Places → база компаний + ЛПР, готовая под аутрич
2. **Анализатор групп** — Telegram + WhatsApp чаты → AI-скоринг сообщений → алерты в личный Telegram

---

## Структура проекта

```
b2b-lead-system/
├── parsers/
│   ├── hh_parser.py          # Парсер hh.kz (API)
│   ├── adata_parser.py       # Парсер adata.kz (HTML)
│   ├── gis_parser.py         # 2ГИС / Google Places
│   ├── main_parser.py        # Координатор + FastAPI HTTP endpoint
│   └── requirements.txt
├── n8n-workflows/
│   ├── vacancy_parser_workflow.json    # Воркфлоу парсера
│   └── group_analyzer_workflow.json   # Воркфлоу анализатора групп
├── supabase/
│   └── schema.sql            # Все таблицы + индексы + вьюхи
├── config/
│   ├── .env.example          # Шаблон переменных
│   └── prompts.md            # Все AI-промпты
└── docs/
    └── README.md             # Эта документация
```

---

## Быстрый старт

### Шаг 1: База данных Supabase

1. Создай проект на [supabase.com](https://supabase.com) (бесплатный tier подходит)
2. Перейди в **SQL Editor**
3. Скопируй и выполни содержимое `supabase/schema.sql`

### Шаг 2: Настройка окружения

```bash
cd parsers
cp ../config/.env.example .env
# Заполни .env своими ключами
pip install -r requirements.txt
```

### Шаг 3: Запуск парсера

**Через CLI (тест):**
```bash
# Базовый запуск — IT-директора Алматы
python main_parser.py \
  --city "Алматы" \
  --sphere "IT" \
  --role "директор" \
  --sources "hh,adata" \
  --output result.json

# Маркетинг, без сохранения в Supabase
python main_parser.py \
  --city "Астана" \
  --sphere "маркетинг" \
  --role "руководитель отдела" \
  --no-supabase \
  --output marketing.json

# С 2ГИС
python main_parser.py \
  --city "Алматы" \
  --sphere "логистика" \
  --role "директор" \
  --sources "hh,2gis" \
  --gis-api-key YOUR_2GIS_KEY
```

**Через HTTP (для n8n):**
```bash
# Запустить сервер
uvicorn main_parser:app --host 0.0.0.0 --port 8080

# Вызвать через curl
curl -X POST http://localhost:8080/parse \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Алматы",
    "sphere": "IT",
    "role": "директор",
    "sources": ["hh", "adata"],
    "save_to_supabase": true
  }'
```

### Шаг 4: Импорт воркфлоу в n8n

1. Открой n8n → **Workflows → Import from file**
2. Импортируй `n8n-workflows/vacancy_parser_workflow.json`
3. Импортируй `n8n-workflows/group_analyzer_workflow.json`
4. В каждом воркфлоу замени:
   - `YOUR_SUPABASE_URL` → твой URL
   - `REPLACE_WITH_YOUR_TELEGRAM_CREDENTIAL_ID` → ID твоего TG-кредентиала в n8n
   - `REPLACE_WITH_YOUR_OPENAI_CREDENTIAL_ID` → ID твоего OpenAI кредентиала

---

## Настройка анализатора групп

### Telegram

1. Создай бота через [@BotFather](https://t.me/BotFather): `/newbot`
2. Добавь бота в нужные группы как **администратора** (иначе не будет видеть сообщения)
3. Узнай `chat_id` группы через [@userinfobot](https://t.me/userinfobot) или [@getmyid_bot](https://t.me/getmyid_bot)
4. Добавь `chat_id` в ноду "Список чатов" воркфлоу

### WhatsApp

Два варианта интеграции:

**Вариант A — Meta Cloud API (официальный, бесплатно):**
- Регистрация: [developers.facebook.com](https://developers.facebook.com)
- Apps → Add App → Business → WhatsApp
- Ограничение: только сообщения, отправленные напрямую боту (не группы)

**Вариант B — Waha / WhatsApp-Web.js (неофициальный, для групп):**
- Self-hosted: [github.com/devlikeapro/waha](https://github.com/devlikeapro/waha)
- Docker: `docker run -p 3000:3000 devlikeapro/waha`
- Даёт доступ к группам через QR-код авторизацию
- URL в n8n: `http://localhost:3000/api/messages`

---

## Supabase — Таблицы

### Парсер вакансий
| Таблица | Описание |
|---|---|
| `companies` | Компании с контактами, сайтом, источником |
| `vacancies` | Вакансии, привязанные к компаниям |
| `contacts` | ЛПР: имя, должность, email, телефон |

### Анализатор групп
| Таблица | Описание |
|---|---|
| `raw_messages` | Все сообщения из всех чатов |
| `profiles` | Профили отправителей с AI-оценкой |
| `matches` | Результаты AI-анализа + статус обработки |

### Полезные вьюхи
- `outreach_ready` — компании готовые к аутричу (с контактами)
- `hot_leads` — горячие лиды из групп с профилями

---

## Переменные n8n (Variables)

Добавь в n8n → **Settings → Variables:**

| Переменная | Значение |
|---|---|
| `SUPABASE_URL` | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | твой anon или service role key |
| `TELEGRAM_ALERT_CHAT_ID` | ID куда шлёт алерты |
| `TELEGRAM_BOT_TOKEN` | токен бота |
| `WHATSAPP_API_TOKEN` | токен WA Cloud API |
| `WHATSAPP_PHONE_ID` | Phone Number ID |

---

## Алерт в Telegram — как выглядит

```
🎯 Новый целевой контакт — 82% релевантности

📍 Чат: IT Kazakhstan (telegram)
👤 Отправитель: Айдар Сейткали @aidarseit
🎭 Портрет: ЛПР, IT, директор
📌 Намерение: 🔥 ИЩЕТ ПОДРЯДЧИКА
🔑 Ключевые слова: автоматизация, CRM, интеграция, b2b
📂 Темы: AI-автоматизация, IT

💬 Сообщение:
"Ищем подрядчика на автоматизацию воронки продаж через CRM..."

🤖 AI-разбор: Директор IT-компании ищет подрядчика на CRM-интеграцию — прямое попадание в ЦА

[💾 Сохранить] [✅ Отработано] [🚫 Чёрный список]
```

---

## Кастомизация

### Поменять ЦА в анализаторе
Отредактируй system-промпт в ноде "AI: Анализ сообщения" → измени список интересующих тем.

### Порог релевантности
В ноде "Объединить скоры" → параметр `THRESHOLD = 0.65` (0.0-1.0).

### Добавить новый источник парсинга
1. Создай `your_parser.py` по образцу `hh_parser.py`
2. Импортируй в `main_parser.py`
3. Добавь в `sources` список в n8n воркфлоу

---

## Монетизация

- **Лидогенерация для заказчиков**: запускай парсер по их параметрам, продавай базу
- **Аутрич-кампании**: используй `outreach_ready` вьюху + промпт 4 для персонализации
- **SaaS**: оберни FastAPI endpoint в платный API с per-request тарификацией
