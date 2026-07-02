# Architecture

## Core Technologies
- **Next.js 14+ (App Router):** Full-stack React framework.
- **Vercel:** Hosting platform and Serverless/Edge Functions.
- **Telegram Bot API:** Interacting with users directly and serving Mini App.
- **Google Vertex AI:** Using `gemini-3.1-flash-image` (Nano Banana 2) for rapid image generation with text rendering capabilities, and `gemini-1.5-pro` for draft/text generation.

## Workflows
### Mini App Carousel Generation
1. User enters Topic in the frontend.
2. Draft is generated via `/api/draft-carousel` (calls Gemini API).
3. User approves Draft.
4. Images are generated via `/api/generate-carousel` (calls Vertex AI).
5. Frontend renders final UI with `html-to-image` overlaying text on the generated background.
6. User clicks "Send to Bot", which sends base64 back to `/api/bot/send-images`, which relays it to Telegram Bot API `sendPhoto`.

### Telegram Bot Inline Generation
1. User sends `/carousel [topic]`.
2. Bot Webhook (`/api/bot/route.ts`) processes command and immediately replies.
3. Bot fetches Draft via internal API and sends to user with Inline Keyboard.
4. User clicks "Сгенерировать картинки" (Pending implementation of Callback Query handler).

## Logging / Observability
- Implemented primitive "Admin Notifications" sending critical errors and user interactions directly to the Admin's Telegram Chat via `sendAdminNotification` in `@/lib/telegram`.
