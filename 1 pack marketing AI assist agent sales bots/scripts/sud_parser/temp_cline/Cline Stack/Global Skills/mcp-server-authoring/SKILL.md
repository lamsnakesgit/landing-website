---
name: mcp-server-authoring
description: Use when creating, installing, deploying, or wiring a custom MCP server into Cline or another MCP client, especially for TypeScript/Node.js stdio servers.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# MCP Server Authoring

Коротко: этот skill нужен, когда надо создать новый MCP сервер, задеплоить его, подключить в Cline и проверить smoke-тестами.

## Когда использовать
- нужно создать новый MCP server под API/SDK/внутренний сервис;
- нужно установить MCP в Cline/Claude Desktop;
- нужно перевести локальный MCP на VPS;
- нужно проверить stdio transport, env, build path, config entry и smoke tool call.

## Когда НЕ использовать
- если задача решается обычным script/API без MCP;
- если нужно только обновить один tool в уже понятном локальном MCP без смены deployment/config схемы;
- если вопрос только про использование уже подключённого MCP, а не про его создание/установку.

## Workflow
1. Определи, действительно ли нужен отдельный MCP server.
2. Выбери runtime: локально, SSH/stdin на VPS или отдельный proxy/service.
3. Для stdio MCP сначала стабилизируй build/output path и env loading.
4. Подключи сервер в MCP config клиента (`cline_mcp_settings.json` или другой target config).
5. Для новых записей по умолчанию ставь `disabled: false` и `autoApprove: []`, если пользователь не просил иначе.
6. Проведи smoke-тесты:
   - build проходит;
   - entrypoint существует;
   - env на месте;
   - один реальный tool call отвечает успешно.
7. Отдай пользователю готовый config snippet и краткий ops-путь обновления.

## Production decision points
- **Локальный stdio** — когда проект ещё активно пилится локально.
- **SSH/stdin на VPS** — лучший baseline для приватного MCP, который не нужно публиковать как HTTP service.
- **Отдельный HTTP/proxy service** — только если нужен multi-client remote access, постоянный runtime или наружная маршрутизация.

## Что обязательно проверить
- `tsconfig.json` и реальный build output (`dist/index.js` vs `dist/src/index.js`);
- что MCP server не ждёт интерактивного ввода при старте;
- что все секреты приходят через env, а не захардкожены;
- что config клиента указывает на существующий executable path/command;
- что smoke tool call проходит из того же режима запуска, в котором MCP будет реально использоваться.

## Типовые ошибки
- неверный build path в MCP config;
- сервер требует OAuth/browser flow во время runtime;
- `dist/**` случайно тестируется или пакуется лишним мусором;
- stdio server пытаются деплоить как web service без причины;
- на VPS копируются macOS metadata-файлы вроде `._*`.

## Smoke tests
- Запрос: «Создай MCP для API и подключи его в Cline»
  - Ожидание: skill ведёт через server → config → smoke test.
- Запрос: «Перенеси локальный MCP на VPS»
  - Ожидание: skill рекомендует SSH/stdin baseline, если HTTP service не нужен.
- Запрос: «Почему MCP not connected?»
  - Ожидание: skill сначала проверяет build path, env и command.

## Red flags
- не публикуй секреты в skill/docs/config snippets;
- не создавай новый MCP server, если хватит обычного script/workflow;
- не тащи user-specific токены в reusable skill.
