-- Инициализация Базы Данных для Outreach MVP
-- Скопируй и выполни этот код в SQL Editor внутри Supabase.
-- Схема ориентирована на one-by-one отправку, трекинг статусов,
-- ответы клиентов, blocklist и несколько WhatsApp-инстансов.

create extension if not exists "uuid-ossp";

-- =====================================================================
-- 1. Кампании
-- =====================================================================
create table if not exists public.campaigns (
    id uuid primary key default uuid_generate_v4(),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    name text not null,
    description text,
    source text,
    segment text,
    offer_angle text,
    channel text not null default 'whatsapp',
    status text not null default 'draft',
    notes text,
    constraint campaigns_status_check check (
        status in ('draft', 'active', 'paused', 'completed', 'archived')
    )
);

-- =====================================================================
-- 2. Лиды / контакты
-- =====================================================================
create table if not exists public.leads (
    id uuid primary key default uuid_generate_v4(),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    phone text not null unique,
    normalized_phone text generated always as (regexp_replace(phone, '[^0-9]', '', 'g')) stored,
    name text,
    company_name text,
    source text,
    niche text,
    city text,
    website text,
    instagram text,
    facebook text,
    whatsapp_name text,
    whatsapp_business_title text,
    whatsapp_business_description text,
    avatar_url text,
    role_guess text,
    pain_hypothesis text,
    offer_angle text,
    personal_hook text,
    generated_pitch text,
    tags text[] not null default '{}',
    ai_score integer not null default 0,
    status text not null default 'new',
    last_contacted_at timestamptz,
    last_replied_at timestamptz,
    last_message_id uuid,
    block_reason text,
    notes text,
    constraint leads_status_check check (
        status in (
            'new',
            'enriched',
            'queued',
            'sent',
            'delivered',
            'read',
            'replied',
            'interested',
            'not_interested',
            'followup_due',
            'blacklisted',
            'invalid_number',
            'closed'
        )
    ),
    constraint leads_ai_score_check check (ai_score >= 0 and ai_score <= 10)
);

-- =====================================================================
-- 3. Blocklist / do-not-contact
-- =====================================================================
create table if not exists public.blocklist (
    id uuid primary key default uuid_generate_v4(),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    phone text not null unique,
    normalized_phone text generated always as (regexp_replace(phone, '[^0-9]', '', 'g')) stored,
    lead_id uuid references public.leads(id) on delete set null,
    reason text not null,
    source text,
    active boolean not null default true,
    notes text,
    blocked_by text not null default 'system'
);

-- =====================================================================
-- 4. Исходящие и входящие сообщения
-- =====================================================================
create table if not exists public.messages (
    id uuid primary key default uuid_generate_v4(),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    lead_id uuid not null references public.leads(id) on delete cascade,
    campaign_id uuid references public.campaigns(id) on delete set null,
    direction text not null,
    channel text not null default 'whatsapp',
    instance_name text,
    sender_number text,
    recipient_phone text not null,
    content text,
    offer_angle text,
    personal_hook text,
    wa_message_id text unique,
    provider_status text not null default 'queued',
    message_type text not null default 'text',
    sent_at timestamptz,
    delivered_at timestamptz,
    read_at timestamptz,
    replied_at timestamptz,
    failed_at timestamptz,
    error_code text,
    error_message text,
    raw_response jsonb,
    constraint messages_direction_check check (direction in ('outbound', 'inbound')),
    constraint messages_status_check check (
        provider_status in ('queued', 'pending', 'sent', 'delivered', 'read', 'replied', 'failed', 'blocked')
    )
);

-- =====================================================================
-- 5. Детальный лог статусов по событиям webhook / runtime
-- =====================================================================
create table if not exists public.message_status_events (
    id uuid primary key default uuid_generate_v4(),
    created_at timestamptz not null default now(),
    message_id uuid references public.messages(id) on delete cascade,
    wa_message_id text,
    lead_id uuid references public.leads(id) on delete set null,
    event_type text not null,
    status text,
    instance_name text,
    payload jsonb,
    event_at timestamptz not null default now(),
    error_code text,
    error_message text
);

-- =====================================================================
-- 6. Ответы клиентов
-- =====================================================================
create table if not exists public.replies (
    id uuid primary key default uuid_generate_v4(),
    created_at timestamptz not null default now(),
    lead_id uuid not null references public.leads(id) on delete cascade,
    message_id uuid references public.messages(id) on delete set null,
    wa_message_id text,
    instance_name text,
    reply_text text,
    reply_type text not null default 'neutral',
    reply_at timestamptz not null default now(),
    raw_payload jsonb,
    constraint replies_type_check check (
        reply_type in ('positive', 'neutral', 'negative', 'stop', 'unknown')
    )
);

-- =====================================================================
-- 7. Базовые индексы
-- =====================================================================
create index if not exists idx_campaigns_status on public.campaigns(status);
create index if not exists idx_leads_status on public.leads(status);
create index if not exists idx_leads_source on public.leads(source);
create index if not exists idx_leads_niche on public.leads(niche);
create index if not exists idx_leads_normalized_phone on public.leads(normalized_phone);
create index if not exists idx_blocklist_normalized_phone on public.blocklist(normalized_phone);
create index if not exists idx_messages_lead_id on public.messages(lead_id);
create index if not exists idx_messages_campaign_id on public.messages(campaign_id);
create index if not exists idx_messages_provider_status on public.messages(provider_status);
create index if not exists idx_messages_wa_message_id on public.messages(wa_message_id);
create index if not exists idx_status_events_message_id on public.message_status_events(message_id);
create index if not exists idx_status_events_wa_message_id on public.message_status_events(wa_message_id);
create index if not exists idx_replies_lead_id on public.replies(lead_id);

-- =====================================================================
-- 8. RLS
-- =====================================================================
alter table public.campaigns enable row level security;
alter table public.leads enable row level security;
alter table public.blocklist enable row level security;
alter table public.messages enable row level security;
alter table public.message_status_events enable row level security;
alter table public.replies enable row level security;

drop policy if exists "Allow Service Role full access to campaigns" on public.campaigns;
drop policy if exists "Allow Service Role full access to leads" on public.leads;
drop policy if exists "Allow Service Role full access to messages" on public.messages;

create policy "Allow Service Role full access to campaigns" on public.campaigns for all using (true) with check (true);
create policy "Allow Service Role full access to leads" on public.leads for all using (true) with check (true);
create policy "Allow Service Role full access to blocklist" on public.blocklist for all using (true) with check (true);
create policy "Allow Service Role full access to messages" on public.messages for all using (true) with check (true);
create policy "Allow Service Role full access to message status events" on public.message_status_events for all using (true) with check (true);
create policy "Allow Service Role full access to replies" on public.replies for all using (true) with check (true);
