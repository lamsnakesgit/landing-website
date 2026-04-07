# Quick Start: Content Factory (Native HTTP Workflow)

Этот гайд поможет вам запустить автоматизацию создания видео с использованием нативных узлов n8n, что гарантирует стабильность работы.

## 1. Предварительные требования
- **n8n** (Desktop или Docker).
- **FFmpeg** установлен в системе (`ffmpeg -version` должен работать).
- **Google Cloud Project** с активным бесплатным пробным периодом ($300).

## 2. Настройка API (5 минут)
Следуйте `API_SETUP_GUIDE.md` для:
1. Включения **Vertex AI** и **Cloud TTS** API.
2. Создания **Service Account** с ролями `Vertex AI User` и `Cloud TTS User`.
3. Скачивания **JSON ключа**.

## 3. Импорт ворклоу
1. Откройте n8n.
2. Нажмите **Workflows** > **Import from File**.
3. Выберите `CONTENT_FACTORY_WORKFLOW.json`.
4. **Настройка узла Config:**
   - Найдите узел `Config: Google Cloud`.
   - Впишите ваш `google_project_id` (ID проекта из консоли Google).
   - Укажите регион (по умолчанию `us-central1`).
5. **Учетные данные (Credentials):**
   - Создайте **OpenAI API** credential (для GPT-4o).
   - Создайте **Google Cloud Service Account** credential и вставьте содержимое вашего JSON ключа.

## 4. Запуск первого видео
1. Нажмите **Execute Workflow**.
2. В стартовом узле (или при запросе) используйте JSON:
   ```json
   {
     "niche": "kamchatka",
     "format": "shorts"
   }
   ```
3. Ворклоу автоматически:
   - Сгенерирует сценарий.
   - Создаст изображения через Imagen 3 (HTTP Request).
   - Создаст озвучку через Google TTS (HTTP Request).
   - Соберет видео через FFmpeg.
4. Финальное видео будет сохранено как `final_video.mp4` в рабочей директории n8n.

## Почему это лучше?
- **Нет "вопросительных знаков":** Мы используем `HTTP Request` вместо специфичных узлов Google, которые могут не поддерживаться в вашей версии n8n.
- **Прозрачность:** Вы видите точные API-запросы, которые отправляются в Google Cloud.
- **Гибкость:** Легко менять параметры моделей (например, версию Imagen или голос TTS) прямо в теле запроса.

## Исправление проблем
- **Ошибка "Unrecognized node type: n8n-nodes-base.executeCommand":**
  Узел `Execute Command` часто отключен по умолчанию в целях безопасности. Чтобы его включить:
  1. Если вы используете **Docker**, добавьте переменную окружения: `N8N_BLOCK_NODES=none` или убедитесь, что `n8n-nodes-base.executeCommand` не в списке `N8N_NODES_EXCLUDE_LIST`.
  2. Перезапустите n8n.
- **Где запускается FFmpeg?**
  FFmpeg запускается прямо на том же сервере или в том же Docker-контейнере, где установлен n8n. 
  - Если n8n в Docker: FFmpeg должен быть установлен *внутри* образа n8n (используйте кастомный Dockerfile или образ `n8nio/n8n:latest-debian`).
  - Если n8n Desktop: FFmpeg должен быть установлен в Windows/Mac и добавлен в PATH.
- **Ошибка 403/401:** Проверьте, что Service Account имеет нужные роли и API включены.
- **Пустое видео:** Проверьте логи узлов `Base64 to Image/Audio`, приходят ли данные от Google.
