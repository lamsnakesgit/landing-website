Проект: 1 pack marketing AI assist agent sales bots
Завершённость: [███████████░░] 85% — ComfyUI Colab notes

# Схема: Google Colab → ComfyUI → Cloudflare Tunnel → API

Краткая памятка по тому, как работает запуск ComfyUI в Google Colab через Cloudflare Tunnel и как проверять API.

---

## 1. Общая схема

```text
Браузер пользователя
        ↓ HTTPS
https://xxxxx.trycloudflare.com
        ↓ Cloudflare Tunnel
cloudflared внутри Google Colab
        ↓ HTTP
http://127.0.0.1:8188
        ↓
ComfyUI server
```

То есть Cloudflare не запускает ComfyUI сам. Он только прокидывает внешний URL к локальному серверу ComfyUI внутри Colab.

---

## 2. Где живёт ComfyUI в Colab

Обычно ComfyUI запускается внутри Colab так:

```bash
python main.py --listen 127.0.0.1 --port 8188
```

или лучше для tunnel-сценариев:

```bash
python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header "*"
```

Локальный адрес внутри Colab:

```text
http://127.0.0.1:8188
```

Порт:

```text
8188
```

---

## 3. Где живёт внешний URL

Cloudflare Tunnel запускается примерно так:

```bash
cloudflared tunnel --url http://127.0.0.1:8188 --no-autoupdate
```

Он выдаёт временную ссылку вида:

```text
https://vanilla-sign-covering-difficulty.trycloudflare.com
```

Важно: ссылки `trycloudflare.com` временные.

Если перезапустить:

- Colab runtime;
- `cloudflared`;
- ячейку запуска;
- весь notebook;

то старая ссылка может умереть и появится новая.

---

## 4. API ComfyUI

Если локально ComfyUI доступен тут:

```text
http://127.0.0.1:8188
```

а Cloudflare дал ссылку:

```text
https://xxxxx.trycloudflare.com
```

то API доступно по таким адресам:

```text
https://xxxxx.trycloudflare.com/system_stats
https://xxxxx.trycloudflare.com/queue
https://xxxxx.trycloudflare.com/object_info
```

---

## 5. Основные endpoints

### `/`

Frontend ComfyUI.

Проверка:

```bash
curl -I https://xxxxx.trycloudflare.com/
```

Если живой — вернёт `200` и HTML страницы ComfyUI.

---

### `/system_stats`

Проверяет backend, версию ComfyUI, Python, PyTorch, GPU и VRAM.

Проверка:

```bash
curl -s https://xxxxx.trycloudflare.com/system_stats
```

Пример подтверждённого ответа:

```json
{
  "system": {
    "os": "linux",
    "comfyui_version": "0.24.0",
    "python_version": "3.12.13",
    "pytorch_version": "2.11.0+cu128"
  },
  "devices": [
    {
      "name": "cuda:0 Tesla T4 : cudaMallocAsync",
      "type": "cuda",
      "vram_total": 15637086208
    }
  ]
}
```

Если этот endpoint отвечает `200`, значит ComfyUI backend живой.

---

### `/queue`

Показывает очередь генераций.

Проверка:

```bash
curl -s https://xxxxx.trycloudflare.com/queue
```

Пример ответа, когда задач нет:

```json
{
  "queue_running": [],
  "queue_pending": []
}
```

---

### `/object_info`

Показывает список доступных нод ComfyUI.

Проверка:

```bash
curl -s https://xxxxx.trycloudflare.com/object_info
```

Если workflow ругается на missing custom nodes, этот endpoint помогает понять, какие ноды реально установлены.

---

## 6. Как отличать типы ошибок

### Ошибка Cloudflare Tunnel: `1033` / `530`

Пример:

```text
Error 1033
Cloudflare Tunnel error
HTTP 530
The host is configured as a Cloudflare Tunnel, but Cloudflare is currently unable to reach it.
```

Что значит:

```text
Браузер → Cloudflare есть
Cloudflare → cloudflared в Colab нет
```

Причины:

- `cloudflared` умер;
- Colab runtime перезапустился;
- старая ссылка устарела;
- tunnel временно отвалился;
- открыта неактуальная вкладка.

Это не ошибка моделей и не ошибка workflow.

Фикс:

```bash
pkill -f cloudflared || true

nohup cloudflared tunnel \
  --url http://127.0.0.1:8188 \
  --no-autoupdate \
  > /content/cloudflared.log 2>&1 &

sleep 10

grep -o "https://[-a-zA-Z0-9.]*trycloudflare.com" /content/cloudflared.log | tail -1
```

---

### Ошибка ComfyUI UI: `Reconnecting`

Если интерфейс ComfyUI открылся, но сверху красное сообщение:

```text
Reconnecting
```

Что значит:

```text
Frontend загрузился, но связь с backend / websocket потеряна.
```

Частые причины:

- умер `cloudflared`;
- умер ComfyUI backend;
- tunnel плохо держит websocket;
- старая вкладка открыта по старой ссылке.

Проверка локально в Colab:

```bash
curl -s http://127.0.0.1:8188/system_stats | head -c 1000
```

Если локально JSON есть — ComfyUI жив, чинить надо tunnel.

---

### Ошибка workflow: отсутствующие ноды

Пример из интерфейса:

```text
Отсутствующие пакеты узлов (1)
Неизвестный пакет (2)
```

Что значит:

```text
Workflow использует custom nodes, которых нет в текущем ComfyUI.
```

Это уже не ошибка Cloudflare.

Фиксы:

1. Установить ComfyUI Manager.
2. Установить missing custom nodes.
3. Перезапустить ComfyUI.
4. Либо заменить workflow на тот, где используются только стандартные ноды.

---

### Ошибка workflow: отсутствующие входные данные

Пример:

```text
Отсутствующие входные данные
Изображения (1)
Загрузить изображение
```

Что значит:

```text
Workflow ждёт input image, но файл не загружен.
```

Фикс:

- загрузить PNG/JPEG/WebP в поле `Загрузить изображение`;
- либо изменить workflow так, чтобы он не требовал входную картинку.

---

## 7. Быстрая диагностика внутри Colab

```bash
echo "=== ComfyUI локально ==="
curl -s http://127.0.0.1:8188/system_stats | head -c 1000 || true

echo ""
echo "=== Очередь ==="
curl -s http://127.0.0.1:8188/queue | head -c 1000 || true

echo ""
echo "=== Процессы ==="
ps aux | grep -E "main.py|cloudflared" | grep -v grep || true

echo ""
echo "=== Последняя Cloudflare ссылка ==="
grep -o "https://[-a-zA-Z0-9.]*trycloudflare.com" /content/cloudflared.log 2>/dev/null | tail -1

echo ""
echo "=== Cloudflare logs ==="
tail -80 /content/cloudflared.log 2>/dev/null || true

echo ""
echo "=== ComfyUI logs ==="
tail -80 /content/comfyui.log 2>/dev/null || true
```

---

## 8. Быстрая внешняя проверка API

На любой машине с интернетом:

```bash
BASE="https://xxxxx.trycloudflare.com"

curl -I "$BASE/"
curl -s "$BASE/system_stats"
curl -s "$BASE/queue"
curl -s "$BASE/object_info" | head -c 1000
```

Ожидаемо:

- `/` → HTML ComfyUI;
- `/system_stats` → JSON с системой/GPU;
- `/queue` → JSON очереди;
- `/object_info` → JSON со списком нод.

---

## 9. Подтверждённый текущий кейс

Было проверено:

Старая ссылка:

```text
https://creation-aggregate-innovative-terms.trycloudflare.com
```

Результат:

```text
HTTP 530
Error 1033
Cloudflare Tunnel error
```

Вывод:

```text
Старый tunnel умер или ссылка устарела.
```

Новая ссылка:

```text
https://vanilla-sign-covering-difficulty.trycloudflare.com
```

Результат API-проверки:

```text
/             → 200, HTML ComfyUI
/system_stats → 200, ComfyUI 0.24.0, Tesla T4, PyTorch 2.11.0+cu128
/queue        → 200, queue_running: [], queue_pending: []
/object_info  → 200, список нод доступен
```

Вывод:

```text
ComfyUI backend и Cloudflare tunnel живые.
Текущие проблемы workflow — missing custom nodes и missing input image.
```

---

## 10. Мини-чеклист запуска

1. Дождаться установки зависимостей.
2. Дождаться скачивания моделей до 100%.
3. Запустить ComfyUI на `8188`.
4. Убедиться локально:

```bash
curl -s http://127.0.0.1:8188/system_stats | head -c 500
```

5. Запустить `cloudflared`.
6. Взять последнюю ссылку:

```bash
grep -o "https://[-a-zA-Z0-9.]*trycloudflare.com" /content/cloudflared.log | tail -1
```

7. Проверить извне:

```bash
curl -s https://xxxxx.trycloudflare.com/system_stats
```

8. Если `1033` — перезапустить только tunnel.
9. Если `Reconnecting` — проверить `/system_stats` локально и перезапустить tunnel.
10. Если missing nodes — ставить custom nodes / ComfyUI Manager.
11. Если missing input — загрузить нужную картинку в workflow.

---

## 11. Короткая формула

```text
Если /system_stats локально работает, а публичная ссылка нет → проблема tunnel.
Если /system_stats публично работает, а workflow красный → проблема workflow/custom nodes/input files.
Если /system_stats локально не работает → проблема ComfyUI process.
```
