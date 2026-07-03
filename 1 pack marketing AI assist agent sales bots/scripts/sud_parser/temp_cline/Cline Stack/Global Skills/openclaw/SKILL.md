---
name: openclaw
description: Управление и настройка OpenClaw AI агента. Деплой, конфигурация провайдеров, tools, отладка. Используй при работе с OpenClaw, настройке моделей, интеграции API или диагностике проблем.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# OpenClaw — Рабочий стек и опыт

## Серверы

### TEST (тестовый)
- URL: https://<YOUR_OPENCLAW_DOMAIN>
- Basic Auth: operator / 7OSldoKrpJtZnofMXNd5w
- Gateway Token: 069c55e6c85c0db39b276b2beb10982d48ccc283e4acd217b113051ac2cb05fb
- Порт: 18789
- Путь: /docker/openclaw/

### PROD (продакшн)
- URL: https://<YOUR_OPENCLAW_STAGING_DOMAIN>
- Gateway Token: qqfwR5u70idSvuBHbc4Jp2SnfBs8qMdW
- Порт: 49593
- Путь: /docker/openclaw-ztxp/

## SSH подключение

ssh -i ~/.ssh/id_ed25519 <SSH_USER>@<YOUR_VPS_IP>

## Управление контейнерами

Статус: docker ps | grep openclaw
Логи: docker logs openclaw-gateway --tail 50 -f
Перезапуск: cd /docker/openclaw && docker compose restart
Пересборка: cd /docker/openclaw && docker compose up -d --build

## Конфигурация

Путь: /home/node/.openclaw/openclaw.json (внутри контейнера)

## Провайдеры

### PoloAPI (основной)

Критически важно: Использовать api: "anthropic-messages" для работы tools!

Рабочий конфиг:
- baseUrl: https://poloai.top
- apiKey: sk-XqHNrrgZIIT0webpColoG6TSYIvesItmg7clMHu0o8e3UQbb
- api: anthropic-messages
- model: claude-sonnet-4-6

НЕ РАБОТАЕТ с tools: api: "openai-completions" — HTTP 400
РАБОТАЕТ с tools: api: "anthropic-messages" — tools вызываются корректно

## Проблемы и решения

### HTTP 400: Improperly formed request

Причина: Используется openai-completions адаптер вместо anthropic-messages
Решение: Изменить api: "anthropic-messages" в конфиге провайдера, удалить старый провайдер, перезапустить gateway

### Tools не вызываются

Диагностика: прямой тест через curl к https://poloai.top/v1/messages
Если curl работает а OpenClaw нет — проблема в адаптере

## Hot Reload

OpenClaw поддерживает hot reload конфига. Но для надёжности лучше перезапускать.

## История изменений

### 16.03.2026 — Tools fix
- Проблема: HTTP 400 при вызове tools через PoloAPI
- Причина: адаптер openai-completions не прокидывал tools
- Решение: перешли на api: "anthropic-messages"
- Результат: tools работают корректно
- Документация: OPENCLAW-TOOLS-FIX.md на Desktop