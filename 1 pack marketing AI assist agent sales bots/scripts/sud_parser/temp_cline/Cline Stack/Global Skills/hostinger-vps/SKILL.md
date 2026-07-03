---
name: hostinger-vps
description: Управление Hostinger VPS через SSH, Docker, systemd и PM2. Используй при live-аудите VPS, работе с контейнерами, сервисами, логами, портами и инфраструктурой пользователя.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Hostinger VPS Management

## Когда использовать
- Используй этот skill, когда задача касается VPS, Docker, systemd, PM2, сервисов или портов на сервере.
- Для любых архитектурных решений по VPS считай source of truth = live VPS + read-only аудит.
- Не полагайся только на старые markdown-файлы на Desktop, если не сверил их с сервером.

## Источник истины
- Полный подтверждённый inventory VPS смотри в `docs/live-vps-inventory.md`.
- Если есть расхождение между markdown и live VPS — верь live VPS.
- Перед изменениями сначала делай read-only аудит, потом уже предлагай правки.

## Подключение к серверу
```bash
ssh -i ~/.ssh/id_ed25519 <SSH_USER>@<YOUR_VPS_IP>
```

## Быстрый read-only аудит
```bash
# Активные контейнеры
docker ps

# Все контейнеры
docker ps -a

# Прослушиваемые порты
ss -tulpn | grep LISTEN

# Запущенные systemd-сервисы
systemctl list-units --type=service --state=running --no-pager

# PM2 процессы
pm2 list

# compose / env файлы
find /opt /docker -maxdepth 2 \( -name docker-compose.yml -o -name compose.yml -o -name compose.yaml -o -name .env -o -name "*.env" \)
```

## Docker операции
```bash
# Просмотр логов
docker logs <container_name> --tail 100
docker logs <container_name> -f

# Проверка конфигурации compose
cd /opt/<service> && docker compose config

# Перезапуск сервиса
cd /opt/<service> && docker compose restart
```

## Systemd / процессы
```bash
# Статус сервиса
systemctl status <service> --no-pager

# Включён ли сервис
systemctl is-enabled <service>

# Активен ли сервис
systemctl is-active <service>

# Проверить конкретный PID
ps -p <pid> -o pid,ppid,user,cmd --no-headers
```

## Правила безопасности
- Не копируй реальные секреты в markdown, rules, skill docs или отчёты.
- Если нужно описать секрет — фиксируй путь / env key, но не значение.
- Для risky-действий (restart, edit, deploy) сначала делай read-only аудит и объясняй, что меняется.
- Если сервис «есть на диске», это не значит, что он реально активен в проде.

## Что важно помнить про этот VPS
- Здесь активно используются **Docker**, **systemd**, **PM2** и отдельные процессы без systemd.
- На сервере есть как продуктовые сервисы, так и старые директории / архивы / тестовые остатки.
- При документировании разделяй:
  1. активные сервисы,
  2. внутренние wrapper/agent-сервисы,
  3. директории/архивы/остатки, не подтверждённые как активные.
