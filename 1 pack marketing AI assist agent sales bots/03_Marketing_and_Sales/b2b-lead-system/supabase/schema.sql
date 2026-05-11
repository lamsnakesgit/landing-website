-- ╔══════════════════════════════════════════════════════════════╗
-- ║          B2B Lead Generation System — Supabase Schema        ║
-- ║          Запустить в: Supabase → SQL Editor → Run            ║
-- ╚══════════════════════════════════════════════════════════════╝

-- Расширения
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- для нечёткого поиска по имени

-- ════════════════════════════════════════════════════════════════
--  БЛОК 1: ПАРСЕР ВАКАНСИЙ / КОМПАНИЙ
-- ════════════════════════════════════════════════════════════════

-- Компании
CREATE TABLE IF NOT EXISTS companies (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id     TEXT,                    -- ID из источника (hh_id, 2gis_id и т.д.)
    name            TEXT NOT NULL,
    site            TEXT,
    phone           TEXT,
    email           TEXT,
    city            TEXT,
    description     TEXT,
    category        TEXT,                    -- сфера/рубрика
    source          TEXT,                    -- hh.kz | adata.kz | 2gis | google_places
    hh_url          TEXT,                    -- ссылка на профиль/карточку
    lead_score      INTEGER DEFAULT 0,       -- для ручного/AI-скоринга
    is_processed    BOOLEAN DEFAULT FALSE,   -- был ли аутрич
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (external_id, source)
);

CREATE INDEX IF NOT EXISTS idx_companies_city     ON companies(city);
CREATE INDEX IF NOT EXISTS idx_companies_category ON companies(category);
CREATE INDEX IF NOT EXISTS idx_companies_source   ON companies(source);
CREATE INDEX IF NOT EXISTS idx_companies_name_trgm ON companies USING GIN (name gin_trgm_ops);

-- Вакансии
CREATE TABLE IF NOT EXISTS vacancies (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id          TEXT,
    company_external_id  TEXT,               -- ссылка на companies.external_id
    company_id           UUID REFERENCES companies(id) ON DELETE SET NULL,
    title                TEXT NOT NULL,
    description          TEXT,
    url                  TEXT,
    salary               TEXT,
    city                 TEXT,
    published_at         TIMESTAMPTZ,
    experience           TEXT,
    employment           TEXT,
    source               TEXT,
    created_at           TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (external_id, source)
);

CREATE INDEX IF NOT EXISTS idx_vacancies_company   ON vacancies(company_id);
CREATE INDEX IF NOT EXISTS idx_vacancies_title_trgm ON vacancies USING GIN (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_vacancies_published  ON vacancies(published_at DESC);

-- Контакты / ЛПР
CREATE TABLE IF NOT EXISTS contacts (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id           UUID REFERENCES companies(id) ON DELETE SET NULL,
    company_external_id  TEXT,
    vacancy_external_id  TEXT,
    name                 TEXT,
    role                 TEXT,               -- должность из вакансии
    email                TEXT,
    phone                TEXT,
    contact_link         TEXT,               -- ссылка на вакансию/профиль
    source               TEXT,
    is_contacted         BOOLEAN DEFAULT FALSE,
    notes                TEXT,
    created_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company_id);
CREATE INDEX IF NOT EXISTS idx_contacts_email   ON contacts(email);


-- ════════════════════════════════════════════════════════════════
--  БЛОК 2: АНАЛИЗАТОР TELEGRAM / WHATSAPP ГРУПП
-- ════════════════════════════════════════════════════════════════

-- Сырые сообщения
CREATE TABLE IF NOT EXISTS raw_messages (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source       TEXT NOT NULL,              -- telegram | whatsapp
    chat_id      TEXT NOT NULL,              -- ID чата/группы
    chat_name    TEXT,
    message_id   TEXT,
    user_id      TEXT,
    text         TEXT,
    media_type   TEXT,                       -- text | photo | document | etc.
    datetime     TIMESTAMPTZ,
    is_analyzed  BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (source, chat_id, message_id)
);

CREATE INDEX IF NOT EXISTS idx_raw_messages_source   ON raw_messages(source);
CREATE INDEX IF NOT EXISTS idx_raw_messages_chat     ON raw_messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_raw_messages_user     ON raw_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_raw_messages_datetime ON raw_messages(datetime DESC);
CREATE INDEX IF NOT EXISTS idx_raw_messages_analyzed ON raw_messages(is_analyzed) WHERE is_analyzed = FALSE;

-- Профили отправителей
CREATE TABLE IF NOT EXISTS profiles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source          TEXT NOT NULL,           -- telegram | whatsapp
    user_id         TEXT NOT NULL,
    name            TEXT,
    username        TEXT,                    -- @username (TG) или номер (WA)
    phone           TEXT,
    bio             TEXT,
    avatar_url      TEXT,
    tags            TEXT[],                  -- ['ЛПР', 'маркетолог', 'IT']
    relevance_score FLOAT DEFAULT 0,         -- 0.0–1.0 (AI оценка)
    is_target       BOOLEAN DEFAULT FALSE,
    in_blacklist    BOOLEAN DEFAULT FALSE,
    notes           TEXT,
    last_seen       TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (source, user_id)
);

CREATE INDEX IF NOT EXISTS idx_profiles_source    ON profiles(source);
CREATE INDEX IF NOT EXISTS idx_profiles_score     ON profiles(relevance_score DESC);
CREATE INDEX IF NOT EXISTS idx_profiles_target    ON profiles(is_target) WHERE is_target = TRUE;
CREATE INDEX IF NOT EXISTS idx_profiles_blacklist ON profiles(in_blacklist) WHERE in_blacklist = FALSE;

-- Совпадения / матчи (результат AI-анализа)
CREATE TABLE IF NOT EXISTS matches (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id      UUID REFERENCES raw_messages(id) ON DELETE CASCADE,
    user_id         TEXT,
    profile_id      UUID REFERENCES profiles(id) ON DELETE SET NULL,
    keywords        TEXT[],                  -- найденные ключевые слова
    intent          TEXT,                    -- "ищет_подрядчика" | "продаёт" | "нанимает" | "спрашивает"
    topics          TEXT[],                  -- темы: AI, маркетинг, логистика
    relevance_score FLOAT,                   -- 0.0–1.0
    is_target       BOOLEAN DEFAULT FALSE,
    alert_sent      BOOLEAN DEFAULT FALSE,
    status          TEXT DEFAULT 'new',      -- new | saved | done | blacklisted
    ai_summary      TEXT,                    -- краткое резюме от AI
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_matches_message   ON matches(message_id);
CREATE INDEX IF NOT EXISTS idx_matches_score     ON matches(relevance_score DESC);
CREATE INDEX IF NOT EXISTS idx_matches_target    ON matches(is_target) WHERE is_target = TRUE;
CREATE INDEX IF NOT EXISTS idx_matches_alert     ON matches(alert_sent) WHERE alert_sent = FALSE;
CREATE INDEX IF NOT EXISTS idx_matches_status    ON matches(status);


-- ════════════════════════════════════════════════════════════════
--  БЛОК 3: ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
-- ════════════════════════════════════════════════════════════════

-- Автообновление updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Функция: связать vacancies.company_id через external_id после вставки
CREATE OR REPLACE FUNCTION link_vacancy_to_company()
RETURNS TRIGGER AS $$
BEGIN
    NEW.company_id := (
        SELECT id FROM companies
        WHERE external_id = NEW.company_external_id
          AND source = NEW.source
        LIMIT 1
    );
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER link_vacancy_company
    BEFORE INSERT OR UPDATE ON vacancies
    FOR EACH ROW EXECUTE FUNCTION link_vacancy_to_company();

-- Функция: связать contacts.company_id через external_id
CREATE OR REPLACE FUNCTION link_contact_to_company()
RETURNS TRIGGER AS $$
BEGIN
    NEW.company_id := (
        SELECT id FROM companies
        WHERE external_id = NEW.company_external_id
        LIMIT 1
    );
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER link_contact_company
    BEFORE INSERT OR UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION link_contact_to_company();


-- ════════════════════════════════════════════════════════════════
--  БЛОК 4: ПОЛЕЗНЫЕ VIEWS
-- ════════════════════════════════════════════════════════════════

-- Компании с контактами — для аутрич-листа
CREATE OR REPLACE VIEW outreach_ready AS
SELECT
    c.id,
    c.name,
    c.city,
    c.category,
    c.site,
    c.phone AS company_phone,
    c.email AS company_email,
    c.source,
    c.hh_url,
    COUNT(DISTINCT ct.id)  AS contacts_count,
    COUNT(DISTINCT v.id)   AS vacancies_count,
    MAX(v.published_at)    AS last_vacancy_date,
    c.lead_score,
    c.is_processed
FROM companies c
LEFT JOIN contacts ct ON ct.company_id = c.id
LEFT JOIN vacancies v  ON v.company_id = c.id
GROUP BY c.id
HAVING COUNT(DISTINCT ct.id) > 0 OR c.email IS NOT NULL OR c.phone IS NOT NULL
ORDER BY c.lead_score DESC, last_vacancy_date DESC;

-- Горячие лиды из групп — для алертов
CREATE OR REPLACE VIEW hot_leads AS
SELECT
    m.id AS match_id,
    m.ai_summary,
    m.intent,
    m.keywords,
    m.relevance_score,
    m.created_at,
    p.name AS sender_name,
    p.username,
    p.phone,
    p.bio,
    p.tags,
    p.relevance_score AS profile_score,
    r.text AS message_text,
    r.chat_name,
    r.source,
    r.datetime AS message_datetime
FROM matches m
JOIN raw_messages r  ON r.id = m.message_id
LEFT JOIN profiles p ON p.user_id = m.user_id AND p.source = r.source
WHERE m.is_target = TRUE
  AND p.in_blacklist IS NOT TRUE
ORDER BY m.relevance_score DESC, m.created_at DESC;
