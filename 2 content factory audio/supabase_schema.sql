-- ============================================
-- AI Media Bot — Схема базы данных Supabase
-- База данных для AI Media Bot (SaaS)
-- Хостинг: Supabase (PostgreSQL)
-- ============================================

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id                   BIGSERIAL PRIMARY KEY,
    telegram_id          BIGINT UNIQUE NOT NULL,
    username             TEXT,
    first_name           TEXT,
    referral_code        TEXT UNIQUE NOT NULL,
    referred_by          TEXT,          -- referral_code того кто пригласил
    referral_count       INTEGER DEFAULT 0,
    is_pro               BOOLEAN DEFAULT FALSE,
    credits_photos       INT DEFAULT 10, -- Бонусные (навсегда)
    credits_videos       INT DEFAULT 0,  -- Бонусные (навсегда-реферальные)
    daily_credits_ph     INT DEFAULT 5,  -- Сброс каждый день
    daily_credits_vid    INT DEFAULT 0,  -- Сброс каждый день (1 для PRO)
    has_used_free_vid    BOOLEAN DEFAULT FALSE, -- Флаг на 1 бесплатный ролик
    total_photos         INT DEFAULT 0,
    total_videos         INT DEFAULT 0,
    is_admin             BOOLEAN DEFAULT FALSE,
    created_at           TIMESTAMPTZ DEFAULT NOW(),
    last_activity        TIMESTAMPTZ DEFAULT NOW()
);

-- Таблица генераций
CREATE TABLE IF NOT EXISTS generations (
    id            BIGSERIAL PRIMARY KEY,
    user_id       BIGINT REFERENCES users(telegram_id),
    type          TEXT,          -- photo / video / audio
    prompt        TEXT,
    result_url    TEXT,
    cost_usd      DECIMAL(10, 4),
    model_used    TEXT,
    status        TEXT,          -- pending / done / error
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    completed_at  TIMESTAMPTZ
);

-- Таблица логов всех сообщений (кто что пишет)
CREATE TABLE IF NOT EXISTS user_messages (
    id            BIGSERIAL PRIMARY KEY,
    user_id       BIGINT REFERENCES users(telegram_id),
    message_text  TEXT,
    metadata      JSONB, -- file_id, command, args и т.д.
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Таблица рефералов
CREATE TABLE IF NOT EXISTS referrals (
    id           BIGSERIAL PRIMARY KEY,
    referrer_id  BIGINT NOT NULL,
    referee_id   BIGINT NOT NULL,
    rewarded     BOOLEAN DEFAULT FALSE,
    rewarded_at  TIMESTAMPTZ,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(referrer_id, referee_id)
);

-- Таблица платежей (ручной учёт)
CREATE TABLE IF NOT EXISTS payments (
    id           BIGSERIAL PRIMARY KEY,
    user_id      BIGINT REFERENCES users(telegram_id),
    amount_rub   INT,                           -- сумма в рублях
    tier         TEXT,                          -- тариф
    status       TEXT DEFAULT 'pending',        -- pending / confirmed / rejected
    notes        TEXT,                          -- заметки админа
    confirmed_by BIGINT,                        -- telegram_id админа
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ
);

-- Индексы для быстрых запросов
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_referral_code ON users(referral_code);
CREATE INDEX IF NOT EXISTS idx_generations_user_id ON generations(user_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_id);

-- Функция генерации уникального реферального кода (6 символов)
CREATE OR REPLACE FUNCTION generate_referral_code()
RETURNS TEXT AS $$
DECLARE
    chars TEXT := 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    code TEXT := '';
    i INT;
BEGIN
    FOR i IN 1..6 LOOP
        code := code || substr(chars, floor(random() * length(chars) + 1)::INT, 1);
    END LOOP;
    RETURN code;
END;
$$ LANGUAGE plpgsql;

-- Row Level Security (безопасность)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE generations ENABLE ROW LEVEL SECURITY;

-- Политика: сервис-ключ (service_role) имеет полный доступ
-- n8n использует service_role key — ему всё доступно

-- ============================================
-- ПРОВЕРОЧНЫЙ ЗАПРОС после создания:
-- SELECT * FROM users LIMIT 5;
-- SELECT generate_referral_code();
-- ============================================
