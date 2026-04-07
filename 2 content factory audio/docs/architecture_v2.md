# Архитектура MediaFactory v2.0 (Target)

Этот документ описывает структуру обновленного бота с поддержкой состояний (states) и умным распределением команд.

## Сравнение Схем

### ТЕКУЩАЯ СХЕМА (V1.0) - Хаос
Сейчас бот реагирует на любой ввод (фото/голос) одинаково, сразу запуская генерацию видео. Это приводит к лишним тратам API и путанице.

```mermaid
graph TD
    T1[Telegram Trigger] --> S1{Switch}
    S1 -- "Любое фото" --> V1[Video Generation]
    S1 -- "Любой голос" --> V1
    S1 -- "Любой текст" --> V1
    V1 --> Send1[Отправка видео]
    style V1 fill:#f96,stroke:#333
```

### ЦЕЛЕВАЯ СХЕМА (V2.0 PRO) - Порядок
Здесь мы вводим **Supabase** как хранилище текущего режима пользователя. Бот "помнит", что вы только что нажали команду `/image2video` и ждет конкретно фото для видео.

```mermaid
graph TD
    T2[Telegram Trigger] --> S2{Smart Switch}
    
    %% Команды
    S2 -- "/photo2video" --> SB1[Supabase: Set 'waiting_vid']
    S2 -- "/image_visual" --> SB2[Supabase: Set 'waiting_art']
    S2 -- "/write" --> SB3[Supabase: Set 'waiting_post']
    
    %% Обработка фото
    S2 -- "Photo" --> CheckDB[Supabase: Get State]
    CheckDB -- "waiting_vid" --> VidBranch[🎬 Video Branch: Analyze -> Confirm -> Gen]
    CheckDB -- "none/default" --> PhotoBranch[📸 Photo Session: Portr/Prod -> Gen]
    
    %% Обработка текста
    S2 -- "Text" --> CheckDB2[Supabase: Get State]
    CheckDB2 -- "waiting_art" --> ArtBranch[🎨 Art Branch: Prompt -> Confirm -> Gen]
    CheckDB2 -- "waiting_post" --> CopyBranch[✍️ Copywriting: Formula AIDA -> Post]
    CheckDB2 -- "none" --> ChatBranch[🤖 Chat AI]
    
    %% Подтверждения (Prompt Lab)
    VidBranch -.-> Confirm[Wait for User OK]
    ArtBranch -.-> Confirm
    Confirm -- "APPROVED" --> FinalGen[Final Generation]
    
    style FinalGen fill:#9f9,stroke:#333
    style Confirm fill:#fff,stroke:#333
```

## Ключевые изменения (v2.0):
1. **Prompt Lab**: Интерактивное подтверждение промпта кнопками (Да/Нет) перед запуском API.
2. **Копирайтинг**: Бот помогает писать посты по формуле AIDA через команду `/write`.
3. **Состояния**: Бот понимает контекст (зачем вы прислали фото).
4. **Imagen 3**: Переход на самую стабильную модель генерации для России и СНГ.
