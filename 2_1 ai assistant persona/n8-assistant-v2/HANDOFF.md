# Handoff Summary for Cline

## Project Context
Building "N8 Assistant" (ИИ с руками) - a B2B SaaS AI Assistant within a Telegram Mini App.
Architecture: Next.js (App Router) + Tailwind CSS + Node.js AI Orchestrator (@langchain/langgraph for JS expected) + Supabase (Auth & DB).

## Current State
- [x] Initialized Next.js project.
- [x] Created `globals.css` with premium glassmorphism UI styles.
- [x] Built the Landing Page (`src/app/page.tsx`).
- [x] Built the User Dashboard Layout with Sidebar (`src/app/dashboard/layout.tsx`).
- [x] Built the User Dashboard Page with credit balance and quick actions (`src/app/dashboard/page.tsx`).
- [x] Deployed MVP frontend to Vercel (Production URL: `https://n8-assistant-v2.vercel.app`).
- [x] Programmatically added Supabase Environment Variables to Vercel production to ensure middleware functionality.
- [x] Patched and restored `src/utils/supabase/middleware.ts` and `src/bot/index.ts` to allow successful builds on Vercel.

## Next Steps (Phase 2)
1. **Supabase Integration**: Ensure `@supabase/ssr` connection is fully working on Vercel with real Auth.
2. **Authentication**: Implement Auth flow (Telegram Web App Auth / Email) in the UI.
3. **Database Schema**: Create tables for `users` (with credit balance `balance_cr`), `generations_log`, and `chat_history` on the Supabase dashboard.
4. **Telegram Bot Initialization**: Apply a valid `TELEGRAM_BOT_TOKEN` in the environment variables (Vercel & local) to unblock the `/api/bot` route.
5. **AI Orchestrator**: Implement `src/app/api/chat/route.ts` using Vercel AI SDK or LangGraph JS.

## Blockers
- None at the moment for frontend, but to test Auth/Bot, we need the actual `TELEGRAM_BOT_TOKEN` and to run migrations on Supabase.

## Architecture Note
n8n is DEPRECATED for this flow. We are building the orchestration logic natively in TypeScript (Node.js) using tools via Maton.ai MCP and WhatsApp via Evolution API (later).
