-- SQL схема для подсистемы SMM Brand AI в Supabase

-- Таблица реестра постов/видео
CREATE TABLE IF NOT EXISTS public.smm_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50) NOT NULL, -- 'telegram', 'youtube', 'instagram', 'tiktok'
    post_id VARCHAR(255) NOT NULL, -- ID поста на конкретной платформе (например, ID сообщения в TG или ID видео на YT)
    url TEXT, -- Ссылка на пост/видео
    publish_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- Дата публикации поста
    title TEXT, -- Заголовок или начало текста поста
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Уникальный ключ: на одной платформе ID поста должен быть уникален
    CONSTRAINT unique_platform_post UNIQUE (platform, post_id)
);

-- Индекс для быстрого поиска по платформе и ID поста
CREATE INDEX IF NOT EXISTS idx_smm_posts_platform_post_id ON public.smm_posts(platform, post_id);

-- Таблица ежедневной истории метрик
CREATE TABLE IF NOT EXISTS public.smm_metrics_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50) NOT NULL,
    post_id VARCHAR(255) NOT NULL,
    views INTEGER DEFAULT 0, -- Просмотры
    likes INTEGER DEFAULT 0, -- Лайки
    comments INTEGER DEFAULT 0, -- Комментарии
    shares INTEGER DEFAULT 0, -- Поделились / Репосты
    saves INTEGER DEFAULT 0, -- Сохранения (Instagram)
    reactions_json JSONB DEFAULT '{}'::jsonb, -- Подробные реакции (для Telegram: огни, лайки, сердечки)
    er NUMERIC(5, 2) DEFAULT 0.00, -- Engagement Rate в % (например, 5.25)
    tracked_date DATE DEFAULT CURRENT_DATE, -- Дата снятия метрик
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Внешний ключ, связывающий с реестром постов
    CONSTRAINT fk_smm_metrics_post FOREIGN KEY (platform, post_id) REFERENCES public.smm_posts(platform, post_id) ON DELETE CASCADE,
    -- Уникальный ключ: один замер на один пост в один день
    CONSTRAINT unique_post_date UNIQUE (platform, post_id, tracked_date)
);

-- Индексы для ускорения выборок аналитики
CREATE INDEX IF NOT EXISTS idx_smm_metrics_history_post_date ON public.smm_metrics_history(platform, post_id, tracked_date);
CREATE INDEX IF NOT EXISTS idx_smm_metrics_history_tracked_date ON public.smm_metrics_history(tracked_date);

-- Комментарии к таблицам (для документирования базы данных)
COMMENT ON TABLE public.smm_posts IS 'Реестр опубликованных материалов во всех соцсетях';
COMMENT ON TABLE public.smm_metrics_history IS 'Ежедневная история вовлеченности и охватов по каждому опубликованному материалу';
