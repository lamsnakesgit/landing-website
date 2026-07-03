---
name: render-deploy
description: Деплой на Render через CLI и GitHub. Настройка проектов, переменных окружения, баз данных. Используй при работе с Render, Node.js, Python или веб-сервисами.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Render Deployment

## Установка и настройка

```bash
# Установка CLI
npm install -g render-cli

# Авторизация
render login

# Проверка версии
render --version
```

## Деплой проекта

### Инициализация проекта
```bash
# В директории проекта
render init

# Создать render.yaml
render blueprint init
```

### Деплой
```bash
# Деплой текущего blueprint
render blueprint apply

# Деплой конкретного сервиса
render deploy --service <service-id>
```

## Управление сервисами

```bash
# Список сервисов
render services list

# Информация о сервисе
render services get <service-id>

# Перезапустить сервис
render services restart <service-id>

# Удалить сервис
render services delete <service-id>
```

## Переменные окружения

```bash
# Установить переменную
render env set KEY=VALUE --service <service-id>

# Список переменных
render env list --service <service-id>

# Удалить переменную
render env unset KEY --service <service-id>
```

## Базы данных

### Создать базу данных
```bash
# PostgreSQL
render databases create --name my-db --plan starter

# Redis
render redis create --name my-redis --plan starter
```

### Подключение
```bash
# Получить строку подключения
render databases get <database-id>

# Подключиться
psql <connection-string>
```

## Домены

```bash
# Добавить кастомный домен
render domains add example.com --service <service-id>

# Список доменов
render domains list --service <service-id>

# Удалить домен
render domains delete example.com --service <service-id>
```

## Логи

```bash
# Логи сервиса
render logs --service <service-id>

# Логи в реальном времени
render logs --service <service-id> --follow

# Логи за период
render logs --service <service-id> --since 1h
```

## Конфигурация (render.yaml)

```yaml
services:
  - type: web
    name: my-app
    env: node
    plan: starter
    buildCommand: npm install && npm run build
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: my-db
          property: connectionString
    healthCheckPath: /health
    autoDeploy: true

databases:
  - name: my-db
    plan: starter
    ipAllowList: []
```

## Docker деплой

```yaml
# render.yaml
services:
  - type: web
    name: my-docker-app
    env: docker
    dockerfilePath: ./Dockerfile
    dockerContext: .
    plan: starter
    envVars:
      - key: PORT
        value: 3000
```

## Статические сайты

```yaml
# render.yaml
services:
  - type: static
    name: my-static-site
    buildCommand: npm run build
    staticPublishPath: ./dist
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

## Background Workers

```yaml
# render.yaml
services:
  - type: worker
    name: my-worker
    env: node
    plan: starter
    buildCommand: npm install
    startCommand: npm run worker
```

## Cron Jobs

```yaml
# render.yaml
services:
  - type: cron
    name: my-cron
    env: node
    schedule: "0 */6 * * *"
    buildCommand: npm install
    startCommand: npm run cron
```

## GitHub интеграция

1. Подключить репозиторий в Render Dashboard
2. Выбрать ветку для деплоя
3. Автоматический деплой при push

## Blueprint (Infrastructure as Code)

```bash
# Применить blueprint
render blueprint apply

# Проверить изменения
render blueprint plan

# Удалить ресурсы
render blueprint destroy
```

## Troubleshooting

### Деплой не работает
```bash
# Проверить логи
render logs --service <service-id>

# Проверить статус
render services get <service-id>

# Перезапустить
render services restart <service-id>
```

### Медленный деплой
- Оптимизировать build команду
- Использовать кеширование
- Уменьшить размер образа

### Проблемы с базой данных
```bash
# Проверить подключение
render databases get <database-id>

# Проверить переменные
render env list --service <service-id>
```

## Полезные команды

```bash
# Открыть dashboard
render dashboard

# SSH в сервис
render shell --service <service-id>

# Переменные для локальной разработки
render env pull --service <service-id> > .env
```

## Best Practices

1. **Использовать render.yaml** для Infrastructure as Code
2. **Настроить health checks** для мониторинга
3. **Использовать переменные окружения** для секретов
4. **Настроить автодеплой** из GitHub
5. **Мониторить логи** и метрики
6. **Использовать preview environments** для тестирования