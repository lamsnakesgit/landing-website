# ⏰ Настройка Ежедневного Запуска Сбора Лидов (Cron)

## 📌 Описание
Система автоматически каждый день собирает B2B-контакты с **adata.kz**, **hh.ru**, **hh.kz**, **threads.net**, **kaspi.jobs** и **госзакупок** по 6 ключевым запросам:
- `ии`
- `разработка`
- `боты`
- `маркетинг`
- `контекстная реклама`
- `ии контент`

Результаты генерируются и сохраняются в папке:
`03_Marketing_and_Sales/daily_leads/ГГГГ-ММ-ДД/`

Структура каждого дня:
- `leads_summary.md` — Итоговый сводный отчёт и аналитика по лидам.
- `leads.csv` — CSV-файл для импорта в Google Таблицы / Excel.
- `leads.json` — Исходный JSON.
- `details/` — Индивидуальный `.md` файл для каждой компании с драфтом 1-го сообщения и разработанным ИИ-оффером.

---

## 🛠 Настройка Cron на локальном Mac / Linux

1. Откройте терминал и выполните:
```bash
crontab -e
```

2. Добавьте следующую строку для запуска каждый день в 09:00 утра:
```cron
0 9 * * * cd "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots" && python3 "03_Marketing_and_Sales/b2b-lead-system/parsers/daily_lead_aggregator.py" >> "03_Marketing_and_Sales/daily_leads/cron_run.log" 2>&1
```

---

## 🚀 Настройка Cron на VPS (Сервере)

1. Подключитесь к VPS по SSH:
```bash
ssh root@151.244.228.104
```

2. Запустите редактирование crontab:
```bash
crontab -e
```

3. Вставьте правило для ежедневного запуска в 09:00:
```cron
0 9 * * * cd /root/ai_agents && python3 03_Marketing_and_Sales/b2b-lead-system/parsers/daily_lead_aggregator.py >> /root/ai_agents/cron.log 2>&1
```
