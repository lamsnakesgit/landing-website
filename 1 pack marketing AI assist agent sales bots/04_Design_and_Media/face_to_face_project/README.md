# Face to Face — Проект презентации

## Структура проекта

```
face_to_face_project/
├── brandbook/              ← PDF брендбук от дизайнера
│   └── Brandbook. Face to Face by C. Atelier.pdf
├── presentation/           ← Готовая веб-презентация (v3 с водяным знаком)
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   ├── assets/images/     ← Изображения для слайдов
│   └── vercel.json        ← Конфиг для деплоя на Vercel
└── assets/                ← Медиа-ресурсы (для будущих материалов)
```

## Как посмотреть локально

```bash
cd presentation
python3 -m http.server 8089
# → http://localhost:8089
```

## Как выложить на Vercel (публичная ссылка)

### Способ 1 — через браузер (без регистрации разработчика):
1. Перейти на https://app.netlify.com/drop
2. Перетащить папку `presentation/` в браузер
3. Готово — получите ссылку вида `https://xxxx.netlify.app`

### Способ 2 — через Vercel CLI:
```bash
# Установить CLI (один раз)
npm install -g vercel

# Деплой из папки presentation
cd presentation
vercel --prod

# После первого деплоя — просто:
vercel --prod
```

## Контакт / водяной знак
Telegram: @buycryptocash1
