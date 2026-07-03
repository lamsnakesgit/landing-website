---
name: vercel-deploy
description: Деплой на Vercel через CLI и GitHub. Настройка проектов, переменных окружения, кастомных доменов. Используй при работе с Vercel, Next.js, React или фронтенд проектами.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Vercel Deployment

## Установка и настройка

```bash
# Установка CLI
npm install -g vercel

# Авторизация
vercel login

# Проверка версии
vercel --version
```

## Деплой проекта

### Первый деплой
```bash
# В директории проекта
vercel

# Следовать инструкциям:
# - Link to existing project? No (для нового)
# - Project name: my-project
# - Directory: ./
# - Override settings? No
```

### Деплой в production
```bash
vercel --prod
```

### Деплой конкретной директории
```bash
vercel --cwd ./packages/frontend
```

## Управление проектами

```bash
# Список проектов
vercel projects ls

# Информация о проекте
vercel inspect <project-url>

# Удалить проект
vercel projects rm <project-name>
```

## Переменные окружения

```bash
# Добавить переменную
vercel env add VARIABLE_NAME

# Добавить для конкретного окружения
vercel env add VARIABLE_NAME production
vercel env add VARIABLE_NAME preview
vercel env add VARIABLE_NAME development

# Список переменных
vercel env ls

# Удалить переменную
vercel env rm VARIABLE_NAME
```

## Домены

```bash
# Добавить домен
vercel domains add example.com

# Список доменов
vercel domains ls

# Удалить домен
vercel domains rm example.com
```

## Логи и мониторинг

```bash
# Логи production
vercel logs <deployment-url>

# Логи в реальном времени
vercel logs <deployment-url> --follow

# Список деплоев
vercel ls
```

## Конфигурация (vercel.json)

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {
    "API_URL": "https://api.example.com"
  },
  "redirects": [
    { "source": "/old", "destination": "/new", "permanent": true }
  ],
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://backend.com/:path*" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" }
      ]
    }
  ]
}
```

## GitHub интеграция

### Автоматический деплой
1. Подключить репозиторий в Vercel Dashboard
2. Выбрать ветку для production (обычно `main`)
3. Каждый push в main → автоматический деплой в production
4. Каждый PR → preview деплой

### Environment Variables в GitHub
- Добавить секреты в GitHub repo settings
- Использовать `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`

## Монорепо (Turborepo)

```json
// vercel.json
{
  "buildCommand": "turbo build",
  "outputDirectory": "apps/web/.next",
  "installCommand": "npm install"
}
```

## Troubleshooting

### Ошибка сборки
```bash
# Проверить локально
npm run build

# Посмотреть логи деплоя
vercel logs <url> --follow
```

### Медленный деплой
- Проверить размер node_modules
- Использовать кеширование (уже включено по умолчанию)
- Оптимизировать build команду

### 404 на страницах
- Проверить `vercel.json` rewrites
- Убедиться что `outputDirectory` правильный
- Для SPA добавить rewrite на `index.html`

## Полезные команды

```bash
# Открыть проект в браузере
vercel open

# Открыть dashboard проекта
vercel dashboard

# Переменные для CI/CD
vercel env pull .env.local

# Промоут preview в production
vercel promote <deployment-url>
```

## Best Practices

1. **Использовать preview деплои** для тестирования перед production
2. **Настроить environment variables** через Dashboard или CLI
3. **Использовать монорепо** для больших проектов
4. **Настроить кастомный домен** для production
5. **Мониторить логи** после каждого деплоя