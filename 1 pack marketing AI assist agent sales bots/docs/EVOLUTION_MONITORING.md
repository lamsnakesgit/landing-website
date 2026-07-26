Проект: 1 pack marketing AI assist agent sales bots
Завершённость: [███████████░░░] 80% — monitoring rollout

# Мониторинг Evolution Instance

## Что это

Добавлен отдельный Python-сервис `06_Scripts_and_Tools/evolution_instance_monitor.py`.

Он:
- раз в `EVOLUTION_MONITOR_POLL_SECONDS` секунд ходит в `GET /instance/fetchInstances`;
- отслеживает статус нужного инстанса `EVOLUTION_INSTANCE` или всех инстансов сразу;
- шлёт уведомление в Telegram, если инстанс ушёл в `disconnected / close / offline / error / unknown / missing`;
- шлёт уведомление, когда инстанс восстановился;
- пишет причины и сырые статусы в лог `logs/evolution_instance_monitor.log`;
- хранит состояние/cooldown в `scratch/evolution_monitor_state.json`.

## Какие env использует

Основные:
- `EVOLUTION_BASE_URL`
- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`

Для Telegram:
- `NOTIFICATION_BOT_TOKEN` или `TG_REALSTATE_SMM_BOT` или `TELEGRAM_BOT_TOKEN`
- `TG_REALSTATE_SMM_CHAT_ID` или `TELEGRAM_CHAT_ID` или `TG_CHAT_ID`

Опционально:
- `EVOLUTION_MONITOR_POLL_SECONDS=60`
- `EVOLUTION_MONITOR_ALERT_COOLDOWN_SECONDS=900`
- `EVOLUTION_MONITOR_TIMEOUT_SECONDS=20`

## Локальный запуск

```bash
python3 06_Scripts_and_Tools/evolution_instance_monitor.py
```

## Рекомендованный запуск на VPS через systemd

Создай unit, например `/etc/systemd/system/evolution-instance-monitor.service`:

```ini
[Unit]
Description=Evolution Instance Monitor
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/your-project
EnvironmentFile=/opt/your-project/.env
ExecStart=/usr/bin/python3 /opt/your-project/06_Scripts_and_Tools/evolution_instance_monitor.py
Restart=always
RestartSec=10
StandardOutput=append:/opt/your-project/logs/evolution_instance_monitor.log
StandardError=append:/opt/your-project/logs/evolution_instance_monitor.log

[Install]
WantedBy=multi-user.target
```

Дальше:

```bash
sudo systemctl daemon-reload
sudo systemctl enable evolution-instance-monitor
sudo systemctl start evolution-instance-monitor
sudo systemctl status evolution-instance-monitor --no-pager
```

## Если хочешь через Coolify

Самый простой вариант — не отдельный веб-сервис, а background service / worker:

- Build Pack: Python
- Start command:

```bash
python3 06_Scripts_and_Tools/evolution_instance_monitor.py
```

- Env variables пробросить из проекта.

Важно: для такого монитора `systemd` на VPS обычно надёжнее и проще, чем Coolify, потому что:
- это бесконечный loop без HTTP;
- удобнее хранить локальные логи;
- меньше лишних слоёв между падением и рестартом.

## Как проверить

1. Запустить монитор.
2. Посмотреть текущий лог:

```bash
tail -f logs/evolution_instance_monitor.log
```

3. Искусственно дисконнектнуть инстанс или выключить его.
4. Проверить, что в Telegram пришло:
   - имя инстанса;
   - статус;
   - причина / диагностический текст.
5. Поднять инстанс обратно и проверить recovery-alert.

## Что ещё можно добавить потом

- отправку последних `docker logs`/`journalctl` к алерту, если монитор крутится прямо на VPS рядом с Evolution;
- отдельный health endpoint для внешнего uptime-monitor;
- запись инцидентов в Supabase;
- n8n workflow на базе этих алертов.