# Progress

## Wins
- Setup Telegram Webhook integration via Vercel Edge API routes.
- Created `Mini App` UI for `Контент Завод` (Carousel Generator).
- Integrated `html-to-image` for generating final rendered slides.
- Setup `Nano Banana 2` (gemini-3.1-flash-image) integration in `/api/generate-carousel` with `responseModalities=["IMAGE"]`.
- Solved Telegram Mini App direct download blocking by routing image generation back through Telegram Bot API (`sendPhoto`).
- Added Telegram Bot inline generation hook `/carousel` that seamlessly integrates with our draft generation route and prompts users to start visual generation.
- Implemented robust `sendAdminNotification` logging for Bot, Draft generation, and Image rendering.

## Issues / Blockers
- **Vercel Serverless Max Duration:** Generating 6 high-quality Vertex AI images inline takes ~60 seconds, risking standard Vercel function timeouts. We moved to a two-step prompt-drafting and callback generation mechanism to alleviate this, but 60s is still tight for image batch generation.
- **Maton.ai Integration:** Need exact `.env` credentials and workflow design to integrate Maton.ai MCP successfully.

## ПРОГРЕСС НА РУССКОМ
- **Успехи:** Развернули Telegram-бота, сделали Mini App интерфейс каруселей, внедрили логику Vertex AI (Nano Banana 2), сделали отправку фото в обход блокировки браузера прямо в бота. Настроили логи админу.
- **Проблемы:** Vercel может обрывать долгие генерации картинок (лимит 60 сек). Ждем ключи от Maton для внедрения MCP сервера.
