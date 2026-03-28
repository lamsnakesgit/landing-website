# Log File: WA SaaS Control

## 2026-03-15
**Wins (Победы):**
- Проведен анализ текущих скриптов (Google Apps Script и n8n). Выявлены узкие места, из-за которых рассылка в n8n не стартовала (нехватка интеграции с Google Sheets и логики цикла внутри n8n воркфлоу).
- Определена архитектура отправки медиа (фото) через Evolution API в рамках n8n.
- Разработана система статусов и отслеживания дожимов, а также стратегия автоматической очистки номеров на стороне пайплайна n8n.
- **Принято важное архитектурное решение:** полный отказ от использования Google Apps Script для рассылки из-за его ненадежности. Вся логика циклов, очистки номеров, пауз и обновления статусов будет инкапсулирована исключительно внутри n8n. Google Таблицы будут выступать только в роли БД.

**Problems / Issues (Проблемы и сложности):**
- Шаблон `wa_saas_control_v1.0.json` был просто "заглушкой", генерирующей ИИ-текст и дергающей API без привязки к базе получателей.
- Ручная очистка номеров занимала бы время, поэтому решено автоматизировать это на лету.

## 2026-03-26
**Wins (Победы):**
- Successfully diagnosed access issues with the n8n instance (n8n.aiconicvibe.store). The server is responding correctly, the problem is localized to the browser cache.
- Успешно диагностирована проблема с доступом к инстансу n8n (n8n.aiconicvibe.store). Сервер отвечает корректно, проблема локализована на уровне кэша браузера.
- Explained Single Page Application (SPA) behavior during connection drops/IP changes due to VPN disconnection.
- Объяснено поведение Single Page Application (SPA) при обрыве соединения/смене IP из-за отключения VPN.

**Problems / Issues (Проблемы и сложности):**
- User experienced a blank dark screen when accessing n8n after disabling VPN, caused by Service Worker caching and module loading failures.
- Пользователь столкнулся с пустой темной страницей при попытке зайти в n8n после отключения VPN. Это вызвано кэшированием старых ресурсов Service Worker-ом и ошибкой загрузки новых бандлов.
- Slow loading in Incognito mode is due to fetching all assets completely without cache and potentially slower external routing without VPN.
- Замедленная загрузка в режиме Инкогнито объясняется полным скачиванием ресурсов без кэша и более длинными маршрутами провайдера без VPN.
