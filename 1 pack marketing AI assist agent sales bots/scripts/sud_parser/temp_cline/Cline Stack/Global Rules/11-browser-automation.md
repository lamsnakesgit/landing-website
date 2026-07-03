# Автоматизация браузера (Browser Automation)

> 📁 Полная документация, паттерны и примеры — в скилле `browser-automation`.
> MUST использовать `use_skill("browser-automation")` при сложных задачах с браузером.

## Когда использовать браузер
- Используй Playwright для интерактива: клики, формы, логин, модалки, dropdown, drag & drop, вкладки, редиректы и JS-поведение.
- Используй Playwright для диагностики: консольные ошибки, сетевые запросы, нестабильные состояния UI и реальные шаги пользователя.
- Для сложных браузерных задач, e2e-сценариев и UI-диагностики используй skill `browser-automation`.

## Playwright vs Tavily

| Задача | Инструмент |
|---|---|
| Просто прочитать страницу | `tavily_extract` |
| Скриншот страницы | Playwright |
| Клики, формы, интерактив | Playwright |
| Консоль/сетевые запросы | Playwright |
| Сбор данных с сайта | Playwright или `tavily_crawl` |
| Проверить структуру интерфейса | Playwright (`browser_snapshot`) |
| Авторизация + действия | Playwright |

## Основные инструменты

```
browser_navigate         — перейти по URL
browser_snapshot         — получить accessibility-снапшот страницы
browser_take_screenshot  — сделать скриншот (PNG/JPEG)
browser_click            — кликнуть по элементу (по ref из snapshot)
browser_type             — ввести текст в поле
browser_fill_form        — заполнить несколько полей сразу
browser_press_key        — нажать клавишу
browser_wait_for         — ждать текст или его исчезновение
browser_console_messages — прочитать консоль (error/warning/info)
browser_network_requests — посмотреть сетевые запросы
browser_evaluate         — выполнить JS на странице
browser_close            — закрыть страницу
browser_navigate_back    — назад
browser_tabs             — список/создание/выбор вкладок
browser_hover            — навести мышь
browser_select_option    — выбрать в dropdown
browser_handle_dialog    — принять/отклонить диалог
```

## Правила использования
- MUST использовать `browser_snapshot` вместо screenshot для навигации — он даёт структуру страницы и `ref` для кликов.
- MUST всегда закрывать браузер через `browser_close` после завершения задачи.
- MUST проверять `browser_console_messages` после действий, связанных с UI и логикой страницы.
- MUST использовать `browser_wait_for` после навигации и значимых действий, а не кликать цепочкой без проверки состояния.
- MUST после изменения DOM или перехода страницы при необходимости вызывать `browser_snapshot` заново — старые `ref` могут устареть.
- SHOULD проверять user-visible результат действия, а не только факт клика.
- SHOULD использовать `browser_network_requests` при диагностике 4xx/5xx, загрузки данных и странного поведения клиента.
- SHOULD использовать `browser_fill_form` для заполнения нескольких полей — быстрее чем по одному.
- SHOULD делать `browser_take_screenshot` при обнаружении визуальных проблем.
- NEVER открывать реальные банки, финансы и личные аккаунты через Playwright без явного запроса пользователя.

## Безопасность и границы
- Playwright открывает изолированный браузер без данных пользователя.
- НЕ использовать расширение Chrome для Claude.
- Не выполняй через браузер рискованные пользовательские действия без явного разрешения.
- При работе с авторизацией используй данные только через переменные окружения.

## Быстрый старт
```
browser_navigate → browser_snapshot → browser_click(ref) → browser_console_messages
```
