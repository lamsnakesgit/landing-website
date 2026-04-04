# Автоматизация Google Vids (docs.google.com/videos)

Google Vids — это новый инструмент в Google Workspace, который использует Gemini для создания видео. На данный момент (апрель 2026) **официального API для Google Vids не существует**, но есть способы его автоматизировать, используя тот факт, что это веб-приложение.

## Почему Google Vids?
- **Бесплатно**: Входит в подписку Google Workspace (Business/Enterprise).
- **Длительность**: До 30 минут в одном проекте.
- **AI-функции**: "Help me create" генерирует структуру, сценарий и подбирает стоковые видео/музыку.

---

## Способ 1: UI Автоматизация (Playwright / Puppeteer) — САМЫЙ РЕАЛЬНЫЙ
Так как API нет, единственный способ — имитация действий пользователя.

### Как это работает:
1. **Авторизация**: Используем `storage_state` в Playwright, чтобы не вводить логин/пароль каждый раз (Google блокирует ботов на странице логина).
2. **Создание**: Переходим на `docs.google.com/videos/create`.
3. **Промпт**: Вставляем текст в поле "Help me create".
4. **Генерация**: Ждем появления элементов сцен.
5. **Экспорт**: Нажимаем "File" -> "Download" -> "MP4".

### Пример скрипта (Python + Playwright):
```python
import time
from playwright.sync_api import sync_playwright

def automate_vids(prompt):
    with sync_playwright() as p:
        # Используем существующий профиль браузера, чтобы избежать капчи
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(storage_state="google_auth.json")
        page = context.new_page()
        
        page.goto("https://docs.google.com/videos/create")
        
        # Клик в поле ввода промпта
        page.wait_for_selector("textarea")
        page.fill("textarea", prompt)
        page.keyboard.press("Enter")
        
        print("Генерируем структуру видео...")
        # Ждем кнопку "Create video" (появляется после генерации структуры)
        page.wait_for_selector("button:has-text('Create video')", timeout=120000)
        page.click("button:has-text('Create video')")
        
        print("Видео создано. Начинаем рендеринг...")
        # Здесь можно добавить логику ожидания полной загрузки всех сцен
        time.sleep(30) 
        
        # Экспорт (примерные селекторы, могут меняться)
        page.click("#file-menu")
        page.hover("text='Download'")
        page.click("text='MP4 video (.mp4)'")
        
        print("Загрузка началась!")
```

---

## Способ 2: "Хак" через Google Drive API
Google Vids сохраняет проекты как файлы в Google Drive. 
- Можно попробовать **копировать** существующий "шаблонный" проект Vids через Drive API.
- Однако, на текущий момент Google Drive API не позволяет редактировать *содержимое* файла Vids (это проприетарный бинарный/JSON формат, как у Google Slides).

---

## Способ 3: Использование AppScript (Перспективно)
Google часто добавляет поддержку новых сервисов в AppScript.
- Проверь в редакторе AppScript, появился ли сервис `VidsApp` (по аналогии с `SlidesApp` или `DriveApp`).
- Если он появился, можно будет создавать видео одной строчкой кода: `Vids.create("My Video", prompt)`.

---

## Сравнение с Vertex AI (Твой текущий стек)

| Характеристика | Google Vids (UI) | Vertex AI (Твой n8n) |
| :--- | :--- | :--- |
| **Цена** | Бесплатно (Workspace) | Платно (но есть кредиты) |
| **Автоматизация** | Сложно (Playwright) | Легко (API/n8n) |
| **Контроль** | Ограничен шаблонами | Полный контроль |
| **Лимиты** | До 30 мин | Без ограничений |

## ИТОГ:
Если нужно **максимально бесплатно** и именно в Google Vids:
1. Настрой **Playwright** с сохранением сессии (`auth.json`).
2. Напиши скрипт-прослойку, который берет сценарий из твоего n8n и "вбивает" его в браузер.
3. Это даст тебе доступ к бесплатным стокам Google и их движку рендеринга.

**Файлы для работы:**
- `google_auth.json` — создай его, один раз зайдя в Google вручную через Playwright.
- `vids_bot.py` — используй пример выше.
