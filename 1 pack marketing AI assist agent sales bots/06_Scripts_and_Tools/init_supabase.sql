-- Инициализация Базы Данных для AI Outreach System
-- Скопируй и выполни этот код в SQL Editor внутри Supabase

-- 1. Таблица сырых лидов (с парсеров)
CREATE TABLE IF NOT EXISTS public.leads (
    id UUID DEFAULT extensions.uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    company_name TEXT NOT NULL,
    industry TEXT,
    phone TEXT UNIQUE,
    website TEXT,
    source TEXT, -- 'hh.ru', '2gis', 'goszakup'
    status TEXT DEFAULT 'new', -- 'new', 'enriched', 'contacted', 'replied', 'blacklisted'
    ai_score INTEGER DEFAULT 0, -- 1 to 10
    ai_summary TEXT, -- Результат работы Perplexity/Tavily
    generated_pitch TEXT -- Сообщение для первой отправки
);

-- 2. Таблица Кампаний (для группировки рассылок)
CREATE TABLE IF NOT EXISTS public.campaigns (
    id UUID DEFAULT extensions.uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    name TEXT NOT NULL,
    status TEXT DEFAULT 'active' -- 'active', 'paused', 'completed'
);

-- 3. Таблица Истории сообщений (Логи для AI)
CREATE TABLE IF NOT EXISTS public.messages (
    id UUID DEFAULT extensions.uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    lead_id UUID REFERENCES public.leads(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES public.campaigns(id) ON DELETE SET NULL,
    direction TEXT NOT NULL, -- 'outbound', 'inbound'
    content TEXT,
    wa_message_id TEXT UNIQUE,
    status TEXT DEFAULT 'sent' -- 'sent', 'delivered', 'read', 'failed'
);

-- 4. Включение Row Level Security (RLS)
ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

-- 5. Базовые политики (Разрешить всё для сервисного ключа n8n)
CREATE POLICY "Allow Service Role full access to leads" ON public.leads FOR ALL USING (true);
CREATE POLICY "Allow Service Role full access to campaigns" ON public.campaigns FOR ALL USING (true);
CREATE POLICY "Allow Service Role full access to messages" ON public.messages FOR ALL USING (true);

-- Создаем индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_leads_status ON public.leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_phone ON public.leads(phone);
CREATE INDEX IF NOT EXISTS idx_messages_wa_id ON public.messages(wa_message_id);
