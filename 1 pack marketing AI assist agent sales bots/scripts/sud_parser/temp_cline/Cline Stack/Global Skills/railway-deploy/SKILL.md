---
name: railway-deploy
description: Деплой на Railway через CLI и GitHub. Настройка проектов, переменных окружения, баз данных. Используй при работе с Railway, Node.js, Python или full-stack проектами.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Railway Deployment

## Установка и настройка

```bash
# Установка CLI
npm install -g @railway/cli

# Авторизация
railway login

# Проверка версии
railway --version
```

## Деплой проекта

### Инициализация проекта
```bash
# В директории проекта
railway init

# Выбрать:
# - Create new project
# - Или привязать к существующему
```

### Деплой
```bash
# Деплой текущей директории
railway up

# Деплой с логами
railway up --logs

# Деплой конкретного сервиса
railway up --service <service-name>
```

## Управление проектами

```bash
# Список проектов
railway projects

# Информация о проекте
railway status

# Переключить проект
railway link <project-id>

# Удалить проект
railway delete
```

## Сервисы

```bash
# Список сервисов
railway services

# Добавить сервис
railway add

# Удалить сервис
railway service delete <service-name>
```

## Переменные окружения

```bash
# Установить переменную
railway variables set KEY=VALUE

# Установить для сервиса
railway variables set KEY=VALUE --service <service-name>

# Список переменных
railway variables

# Удалить переменную
railway variables delete KEY
```

## Базы данных

### Добавить базу данных
```bash
# PostgreSQL
railway add --database postgres

# MySQL
railway add --database mysql

# Redis
railway add --database redis

# MongoDB
railway add --database mongodb
```

### Подключение к базе
```bash
# Получить строку подключения
railway variables

# Подключиться через psql
railway run psql $DATABASE_URL
```

## Домены

```bash
# Сгенерировать домен
railway domain

# Добавить кастомный домен
railway domain add example.com

# Список доменов
railway domain list
```

## Логи

```bash
# Логи сервиса
railway logs

# Логи в реальном времени
railway logs --follow

# Логи конкретного сервиса
railway logs --service <service-name>
```

## Конфигурация (railway.json)

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "npm run build"
  },
  "deploy": {
    "startCommand": "npm start",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5
  }
}
```

## Docker деплой

```json
// railway.json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "node server.js"
  }
}
```

## Монорепо

```json
// railway.json в корне
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "npm run build --workspace=packages/api"
  }
}
```

## Cron Jobs

```json
// railway.json
{
  "deploy": {
    "cronSchedule": "0 */6 * * *",
    "startCommand": "node scripts/cron.js"
  }
}
```

## GitHub интеграция

1. Подключить репозиторий в Railway Dashboard
2. Выбрать ветку для деплоя
3. Автоматический деплой при push

## Environment Variables из GitHub

```bash
# Использовать в CI/CD
railway variables set RAILWAY_TOKEN=${{ secrets.RAILWAY_TOKEN }}
```

## Troubleshooting

### Деплой не работает
```bash
# Проверить логи
railway logs

# Проверить переменные
railway variables

# Перезапустить сервис
railway service restart
```

### Медленный деплой
- Оптимизировать Dockerfile
- Использовать кеширование слоёв
- Уменьшить размер образа

### Проблемы с базой данных
```bash
# Проверить подключение
railway run psql $DATABASE_URL

# Проверить переменные
railway variables | grep DATABASE
```

## Полезные команды

```bash
# Запустить команду в контексте Railway
railway run <command>

# SSH в сервис
railway shell

# Открыть dashboard
railway open

# Переменные для локальной разработки
railway run -- npm run dev
```

## Best Practices

1. **Использовать preview environments** для тестирования
2. **Настроить health checks** для мониторинга
3. **Использовать переменные окружения** для секретов
4. **Настроить автодеплой** из GitHub
5. **Мониторить логи** и метрики