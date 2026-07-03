# Правила использования инструментов поиска

## Таблица: задача → инструмент

| Задача | Инструмент |
|---|---|
| Быстрый поиск фактов | `tavily_search` |
| Глубокий технический поиск | `tavily_search` (advanced) |
| Веб-поиск с чистым контентом | `web_search_exa` |
| Поиск кода и документации | `get_code_context_exa` |
| Полный контент конкретной страницы | `crawling_exa` или `tavily_extract` |
| Анализ структуры сайта | `tavily_map` |
| Полный обход сайта | `tavily_crawl` |
| Комплексное исследование темы | `tavily_research` |
| Документация библиотеки | `context7` (resolve + query) |
| Поиск кода в репозиториях GitHub | `github search_code` |
| Поиск зрелых репозиториев и готовых паттернов | `github search_repositories` |
| Семантический поиск по локальному проекту | `cocoindex-code → search` |

## Базовый research priority
- Для внешнего исследования по умолчанию используй связку: **Tavily → Exa → Context7 → GitHub MCP**.
- Для library/framework документации Context7 может подниматься выше общего research-потока.
- Если ответ может уже быть в проекте или доступных MCP, сначала используй локальный код и внутренние инструменты.

## Автоматическое применение
- Новая технология или сервис → сначала `tavily_search`/`tavily_research`, потом `web_search_exa`, затем official docs и repo patterns.
- Баг/ошибка → `tavily_search` (advanced) + exact error search + official docs/issues.
- Анализ чужого сайта → `tavily_extract` + `tavily_map`.
- Чистый контент без мусора → `web_search_exa`.
- Сниппеты кода, SDK usage и примеры → `get_code_context_exa`.
- Документация библиотек → `context7` (приоритет над памятью модели).
- Готовые реализации и production patterns → `github search_code`, `github search_repositories`, skill `implementation-research`.
- Локальный поиск по большой кодовой базе → `cocoindex-code → search`, skill `local-code-search`.
- Нетривиальные UI/frontend референсы → сначала official accessibility/pattern docs (`W3C WAI`, `ARIA APG`, `web.dev`, mature design systems вроде `USWDS` / `Carbon` / `Primer` / `Material`), затем skill `frontend-design` / `cc-design` / `huashu-design`, потом Exa/Tavily и зрелые репозитории.

## Несколько проходов поиска
- Если после первого поиска ответ остаётся неполным, противоречивым или слабым, делай второй и третий проход через Tavily, Exa, Context7 и GitHub MCP.
- Используй несколько поисковых проходов для задач, где важны качество решения, свежесть API, зрелые паттерны или высокая цена ошибки.
- Не останавливайся на одном источнике, если нужен production-grade результат.

## Official-first routing
- Для сервиса, SDK, API, провайдера или фреймворка сначала ищи официальный сайт, официальный docs URL, официальный GitHub-репозиторий и first-party материалы.
- Если официальный источник найден, используй его как базовую точку истины.
- Вторичные статьи, блоги и community-материалы используй только после first-party источников или для edge-cases.
- Для UI/accessibility задач first-party слоем по умолчанию считаются `W3C/WAI`, `ARIA APG`, `web.dev` и официальные design-system docs используемого стека или паттерна.

## Skills и search routing
- Для задач на готовые реализации, mature patterns и production-grade примеры используй skill `implementation-research`.
- Для поиска реализаций внутри локального репозитория используй skill `local-code-search`.
- Для нетривиальных UI/frontend задач и поиска лучших UI-кейсов используй skill `frontend-design`; для general HTML-first high-fidelity design/prototype задач используй `cc-design`; для HTML-first design demo, motion/animation, export-heavy и design-variation/design-direction задач используй `huashu-design`.
- Для форм, accessibility, keyboard/focus behavior и custom widgets сначала добирай official guidance (`WAI`, `APG`, `web.dev`, `design-system docs`), и только потом адаптируй найденный паттерн под текущий стек.

## Context7 — приоритет
- MUST автоматически вызывать `resolve-library-id` → `query-docs` при генерации кода для конкретных библиотек.
- MUST предпочитать данные из Context7 обучающим данным модели.
