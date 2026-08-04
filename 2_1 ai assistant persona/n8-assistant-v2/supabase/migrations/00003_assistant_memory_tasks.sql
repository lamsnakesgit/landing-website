-- Persistent assistant memory, context, and task routing.
-- Source of truth for MVP: Supabase. External tools can mirror this later.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS public.assistant_profiles (
    telegram_id BIGINT PRIMARY KEY REFERENCES public.telegram_users(telegram_id) ON DELETE CASCADE,
    display_name TEXT,
    language TEXT DEFAULT 'ru',
    timezone TEXT DEFAULT 'Asia/Almaty',
    system_prompt TEXT,
    preferences JSONB DEFAULT '{}'::jsonb,
    business_context JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.assistant_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id BIGINT REFERENCES public.telegram_users(telegram_id) ON DELETE CASCADE,
    session_key TEXT,
    scope TEXT NOT NULL DEFAULT 'user' CHECK (scope IN ('user', 'chat', 'project', 'global')),
    memory_type TEXT NOT NULL DEFAULT 'preference' CHECK (memory_type IN ('preference', 'fact', 'business_rule', 'style', 'decision', 'summary')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    source TEXT NOT NULL DEFAULT 'telegram',
    confidence NUMERIC(3, 2) DEFAULT 0.80 CHECK (confidence >= 0 AND confidence <= 1),
    created_by TEXT NOT NULL DEFAULT 'assistant',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_assistant_memories_telegram_id
    ON public.assistant_memories(telegram_id);

CREATE INDEX IF NOT EXISTS idx_assistant_memories_session_key
    ON public.assistant_memories(session_key);

CREATE INDEX IF NOT EXISTS idx_assistant_memories_scope_type
    ON public.assistant_memories(scope, memory_type);

CREATE TABLE IF NOT EXISTS public.conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_key TEXT NOT NULL,
    telegram_id BIGINT REFERENCES public.telegram_users(telegram_id) ON DELETE SET NULL,
    chat_id BIGINT,
    message_thread_id BIGINT,
    message_id BIGINT,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT NOT NULL,
    attachments JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversation_messages_session_created
    ON public.conversation_messages(session_key, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversation_messages_telegram
    ON public.conversation_messages(telegram_id, created_at DESC);

CREATE TABLE IF NOT EXISTS public.knowledge_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id BIGINT REFERENCES public.telegram_users(telegram_id) ON DELETE SET NULL,
    source_type TEXT NOT NULL CHECK (source_type IN ('document', 'artifact', 'url', 'telegram_file', 'manual_note', 'repo_doc', 'integration')),
    title TEXT NOT NULL,
    uri TEXT,
    content_hash TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'indexed', 'failed', 'archived')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_sources_telegram_status
    ON public.knowledge_sources(telegram_id, status);

CREATE TABLE IF NOT EXISTS public.knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES public.knowledge_sources(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(source_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_source
    ON public.knowledge_chunks(source_id);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_embedding
    ON public.knowledge_chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE TABLE IF NOT EXISTS public.agent_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id BIGINT REFERENCES public.telegram_users(telegram_id) ON DELETE SET NULL,
    session_key TEXT,
    chat_id BIGINT,
    message_thread_id BIGINT,
    source TEXT NOT NULL DEFAULT 'telegram',
    route TEXT NOT NULL DEFAULT 'general' CHECK (route IN ('content', 'research', 'crm', 'scheduler', 'integration', 'code', 'general')),
    title TEXT NOT NULL,
    objective TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'needs_clarification', 'running', 'blocked', 'done', 'failed', 'cancelled')),
    input JSONB DEFAULT '{}'::jsonb,
    output JSONB DEFAULT '{}'::jsonb,
    assigned_to TEXT,
    due_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_tasks_telegram_status
    ON public.agent_tasks(telegram_id, status);

CREATE INDEX IF NOT EXISTS idx_agent_tasks_route_status
    ON public.agent_tasks(route, status);

CREATE INDEX IF NOT EXISTS idx_agent_tasks_session_created
    ON public.agent_tasks(session_key, created_at DESC);

CREATE TABLE IF NOT EXISTS public.agent_task_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES public.agent_tasks(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    actor TEXT NOT NULL DEFAULT 'assistant',
    payload JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_task_events_task_created
    ON public.agent_task_events(task_id, created_at DESC);

ALTER TABLE public.assistant_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assistant_memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_task_events ENABLE ROW LEVEL SECURITY;

