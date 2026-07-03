# MCP Server Authoring Runbook

## Базовый чек-лист

1. Проверить, нужен ли MCP server вообще.
2. Собрать минимальный stdio server.
3. Проверить `npm run build`.
4. Проверить реальный entrypoint.
5. Настроить env.
6. Добавить запись в Cline config.
7. Сделать smoke tool call.
8. Зафиксировать итоговый config snippet для пользователя.

## Рекомендация по deployment

### Для приватного MCP на VPS
Предпочитай:
- код и `.env` на VPS;
- запуск через `ssh ... /path/to/run-mcp.sh`;
- без лишнего reverse proxy и без отдельного HTTP API.

### Когда нужен proxy/service
Только если:
- MCP должны использовать несколько клиентов одновременно;
- нужен удалённый HTTP transport;
- нужен постоянный daemon с отдельными логами и мониторингом.

## Пример config для Cline

```json
{
  "mcpServers": {
    "example-vps": {
      "disabled": false,
      "autoApprove": [],
      "type": "stdio",
      "command": "ssh",
      "args": [
        "-i",
        "/absolute/path/to/key",
        "user@host",
        "/opt/example-mcp/run-mcp.sh"
      ]
    }
  }
}
```
