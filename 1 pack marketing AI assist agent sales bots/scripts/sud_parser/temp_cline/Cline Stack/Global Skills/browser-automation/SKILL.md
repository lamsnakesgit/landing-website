---
name: browser-automation
description: Автоматизация браузера через Playwright MCP — навигация, клики, формы, скриншоты, консоль, сетевые запросы. Используй при тестировании веб-приложений, сборе данных, диагностике ошибок или любых задачах требующих интерактивного браузера.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Browser Automation — Playwright MCP

## Проверено в тесте (2026-03-28)
- `browser_navigate` → `browser_snapshot` → `browser_take_screenshot` → `browser_close` — работает корректно
- Playwright MCP подключён как `playwright` в `cline_mcp_settings.json`
- autoApprove: `browser_snapshot`, `browser_screenshot`, `browser_click`, `browser_type`, `browser_navigate`, `browser_close`, `browser_wait_for`

## Полный список инструментов

| Инструмент | Назначение |
|---|---|
| `browser_navigate` | Перейти по URL |
| `browser_snapshot` | Accessibility-снапшот (структура + ref для кликов) |
| `browser_take_screenshot` | Скриншот PNG/JPEG |
| `browser_click` | Клик по элементу (нужен `ref` из snapshot) |
| `browser_type` | Ввести текст в поле |
| `browser_fill_form` | Заполнить несколько полей сразу |
| `browser_press_key` | Нажать клавишу (Enter, Tab, Escape...) |
| `browser_wait_for` | Ждать появления/исчезновения текста |
| `browser_console_messages` | Прочитать консоль (error/warning/info/debug) |
| `browser_network_requests` | Посмотреть сетевые запросы |
| `browser_evaluate` | Выполнить произвольный JS на странице |
| `browser_close` | Закрыть страницу |
| `browser_navigate_back` | Назад в истории |
| `browser_tabs` | list/new/close/select вкладки |
| `browser_hover` | Навести мышь (для dropdown/tooltip) |
| `browser_select_option` | Выбрать вариант в `<select>` |
| `browser_handle_dialog` | Принять/отклонить alert/confirm/prompt |
| `browser_drag` | Drag & drop |
| `browser_resize` | Изменить размер окна |
| `browser_run_code` | Запустить произвольный Playwright код |
| `browser_file_upload` | Загрузить файл |
| `browser_install` | Установить браузер |

## Стандартный паттерн работы

```
1. browser_navigate(url)
2. browser_snapshot()          ← получить структуру и ref элементов
3. browser_click(ref=...)      ← кликнуть по нужному элементу
4. browser_wait_for(text=...)  ← дождаться результата
5. browser_console_messages(level="error")  ← проверить ошибки
6. browser_close()
```

## Паттерн: тестирование формы

```
1. browser_navigate("http://localhost:3000")
2. browser_snapshot()           ← найти ref полей
3. browser_fill_form(fields=[   ← заполнить все поля
     {ref: "...", value: "test@email.com"},
     {ref: "...", value: "password123"}
   ])
4. browser_click(ref="submit-button")
5. browser_wait_for(text="Успешно")
6. browser_console_messages(level="error")
7. browser_take_screenshot(type="png")
8. browser_close()
```

## Паттерн: диагностика ошибок

```
1. browser_navigate(url)
2. browser_console_messages(level="error")   ← JS ошибки
3. browser_network_requests(includeStatic=false)  ← 404/500
4. browser_take_screenshot(type="png")       ← визуал
5. browser_close()
```

## Паттерн: сбор данных

```
1. browser_navigate(url)
2. browser_snapshot()           ← структура страницы
3. browser_evaluate(function="() => { return document.querySelector('.data').innerText }")  ← извлечь данные
4. browser_close()
```

## Ключевые правила

🚨 MUST использовать `browser_snapshot` (не screenshot) для навигации — только snapshot даёт `ref` для кликов.

🚨 MUST всегда вызывать `browser_close` после завершения — иначе браузер висит в памяти.

MUST проверять `browser_console_messages(level="error")` при тестировании.

SHOULD использовать `browser_wait_for` после действий — не кликать сразу после навигации.

SHOULD делать `browser_take_screenshot` при обнаружении визуальных проблем.

NEVER хранить пароли и токены в коде — только через переменные окружения.

## Выбор: Playwright vs Tavily

```
Просто прочитать контент страницы → tavily_extract (быстрее, дешевле)
Интерактив, клики, формы → Playwright
Консоль/ошибки JS → Playwright
Проверка редиректов → Playwright
Сбор данных со многих страниц → tavily_crawl (если без JS) или Playwright (с JS)
```

## Troubleshooting

**Элемент не найден:** сначала вызови `browser_snapshot` — ref меняется после каждого действия.

**Браузер завис:** `browser_close`, затем `browser_navigate` снова.

**Страница не загрузилась:** добавь `browser_wait_for` после navigate.

**Нужен мобильный вид:** `browser_resize(width=375, height=812)` перед navigate.
