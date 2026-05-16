# Установка и настройка Hermes Assistant (Личный + Маркетинг)

Этот документ фиксирует шаги по развёртыванию системы на VPS (Ubuntu 24.04).

## 1. Среда (Infrastructure)
- **VPS IP:** `151.241.100.226`
- **ОС:** Ubuntu 24.04 LTS (Noble)
- **Контейнеризация:** Docker 29.1.3 (уже был на борту)
- **Окружение:** n8n, Evolution API, Traefik.

## 2. Установка Hermes Agent
Мы использовали официальный инсталлятор от Nous Research:
```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

**Результат:**
- Исполняемый файл: `/usr/local/bin/hermes`
- Конфигурация: `/root/.hermes/config.yaml`
- Окружение: `/root/.hermes/.env`

## 3. Конфигурация Ключей
В файл `/root/.hermes/.env` добавлены:
- `GOOGLE_API_KEY` — для работы с Gemini 1.5 Flash (основной мозг).
- `TELEGRAM_BOT_TOKEN` — токен от @BotFather (`8764670738:AAFhAW...`).
- `GATEWAY_ALLOW_ALL_USERS=true` — временный доступ для первичной настройки.

## 4. Настройка Ядра (Core Settings)
Через CLI были применены следующие настройки:
```bash
hermes config set provider google
hermes config set model gemini-1.5-flash
hermes config set system_instructions "Ты — мощный личный ассистент и эксперт по маркетингу. Отвечай всегда на русском языке."
```

## 5. Запуск Gateway (Telegram)
Агент запущен как системная служба (systemd user service):
```bash
hermes gateway install
hermes gateway start
```
Включен `linger`, чтобы служба не засыпала после закрытия SSH-сессии.

## 6. Ожидаемые реакции бота (FAQ)
- **"/sethome"**: Бот просит назначить текущий чат «домашним». Это нужно для того, чтобы он знал, куда присылать ежедневные отчеты (Pulse) и напоминания.
- **"Confirm /new"**: Это стандартная мера безопасности при сбросе сессии.
- **Команды**: Все команды начинающиеся на `/` — это инструменты управления агентом.

---
**Статус:** ✅ Установка завершена, идет этап калибровки и настройки скиллов.
