---
name: supabase-integration
description: Интеграция Supabase в Content Factory Audio: работа с таблицами users, generations, payments и RLS.
---

# Supabase Integration (Content Factory Audio)

> Этот skill используется для безопасной и эффективной работы с базой данных Supabase, учитывая специфику проекта (AI Media Bot).

## Специфика проекта
Согласно `database/supabase_schema.sql`, основные таблицы:
- `users`: хранение баланса (credits), статуса PRO и реферальных данных.
- `generations`: логирование генераций (photo/video/audio) и их стоимости.
- `user_messages`: история взаимодействий.
- `referrals`: связи между пользователями.
- `payments`: учет платежей и тарифов.

---

## Базовые правила
- **Секреты:** URL и ключи (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`) — только в `.env`.
- **Клиент:** В Streamlit (`app.py`) используем `SUPABASE_ANON_KEY` для обычных операций.
- **Админ-доступ:** `SUPABASE_SERVICE_ROLE_KEY` используется только в n8n или защищенных скриптах для обхода RLS (например, начисление кредитов).
- **RLS (Row Level Security):** Всегда проверяй, включен ли RLS для новых таблиц.

## Типичные операции
1. **Проверка баланса:** `SELECT daily_credits_ph, credits_photos FROM users WHERE telegram_id = ...`
2. **Логирование генерации:** Вставка в `generations` с указанием `model_used` и `cost_usd`.
3. **Реферальная система:** Использование функции `generate_referral_code()` при регистрации нового пользователя.

## Чек-лист для самопроверки
- [ ] Ключи не захардкожены в коде.
- [ ] Для операций пользователя используется Anon Key + RLS.
- [ ] Для системных операций (платежи, админка) используется Service Role Key.
- [ ] Все запросы к `generations` включают `user_id` для корректной фильтрации.
