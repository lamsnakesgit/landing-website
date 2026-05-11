# Cline Global Rules

## Language
You MUST always respond in Russian.
All code comments must be in Russian.
All messages to the user must be in Russian.

## Code Style
- Variable names: English (camelCase or snake_case)
- Function names: English
- Comments and docstrings: Russian
- Class names: English
- File names: English

## Communication
- When user writes in Russian, respond in Russian
- Never switch to English unless explicitly asked
- Be concise and direct (avoid verbose explanations)

## Auto-decisions
When prompted for interactive questions:
- For "Would you like to use React Compiler?" → answer "No"
- For "Would you like to use TypeScript?" → answer "Yes"
- For dependency installation prompts → answer "Yes"

Prefer explicit code. Do not add comments on every line.
Use modern ES2022+ syntax. No magic, readable names.
Max 50 lines per function. Break into sub-components.

# Автоматический поиск документации

## Когда информация отсутствует
- Если вы не знаете конкретную техническую информацию или документацию
- Если не хватает деталей по реализации определенного функционала
- Если нужно получить актуальную информацию по API или технологиям

## Как это работает
1. При возникновении вопроса о недостающей информации автоматически используйте Brave Search
2. Используйте команду "brave_web_search" с конкретным запросом
3. Используйте ключевые слова: "documentation", "API reference", "official guide", "tutorial"

## Примеры автоматического поиска:
- "Python Telegram bot API documentation"
- "FastAPI tutorial for beginners"
- "Docker Compose official documentation"
- "GitHub API v3 reference"

## Приоритеты поиска:
1. Официальная документация
2. Официальные руководства
3. Технические статьи и блоги
4. Stack Overflow и другие технические форумы

# .clinerules

## Context Management
- When context exceeds 50%, create a handoff summary
- Preserve: current file state, next steps, blockers
- Use /new automatically when hitting 70%

## Task Breakdown Rules
- Break tasks into 15-30 minute chunks
- Complete one file at a time
- Always commit after completing a subtask

## Memory Bank
- Document completed features in PROGRESS.md
- Update architecture decisions in ARCHITECTURE.md
- Track blockers in BLOCKERS.md

# Разработка сайтов и приложений

## Локализация интерфейса
- Все сайты и приложения должны иметь интерфейс на русском языке по умолчанию
- Все тексты: кнопки, меню, формы, сообщения, заголовки - на русском
- Учитывать особенности русского языка (падежи, множественное число, склонения)
- Интерфейс должен быть понятен русскоязычным пользователям

## Удаление маркетинговой информации
- НЕ указывать провайдеров в коде
- НЕ добавлять цены, тарифы или контакты провайдеров
- НЕ вставлять рекламные блоки
- Фокус на чистом функционале и пользовательском опыте
- Удалять любые упоминания хостинг-провайдеров, доменных регистраторов и т.д.

## Запрос недостающих данных
При получении технической документации или требований:
- Анализировать на полноту и достаточность информации
- Задавать уточняющие вопросы, если не хватает данных:
  - Требования к дизайну, цветовой гамме, шрифтам
  - Целевая аудитория и пользовательские сценарии
  - Функциональные требования и must-have фичи
  - Технические ограничения и требования к производительности
  - Данные для API/интеграций (если используются)
  - Требования к адаптивности и поддержке устройств

## Примеры уточняющих вопросов:
- "Какой стиль дизайна предпочтительнее: минималистичный, корпоративный, креативный?"
- "Какие основные функции должны быть в приложении?"
- "Нужна ли адаптация под мобильные устройства и планшеты?"
- "Какие данные будут использоваться в приложении?"
- "Есть ли требования к цветовой гамме или шрифтам?"

# Правила использования Context7 MCP

## Автоматический вызов
- Всегда используй инструменты `github.com/upstash/context7-mcp` (Context7), когда требуется:
    - Генерация кода для конкретных библиотек или фреймворков.
    - Настройка конфигураций или шаги по установке API.
    - Получение актуальной документации по библиотекам.
- Ты должен автоматически вызывать `resolve-library-id` для поиска ID библиотеки и затем `get-library-docs` для получения документации, не дожидаясь явного указания от пользователя.

## Процесс работы
1. **Поиск ID**: Если ID библиотеки неизвестен (формат `/org/project`), сначала вызови `resolve-library-id` с названием библиотеки.
2. **Получение документации**: Используй полученный ID для вызова `get-library-docs`.
3. **Применение**: Используй полученные примеры кода и API-референсы для выполнения задачи пользователя.

## Приоритет актуальности
- Предпочитай данные из Context7 обучающим данным модели, так как они содержат наиболее свежую информацию о версиях и API.


