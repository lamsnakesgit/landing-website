# Handoff Document

## Current Status
- The MVP frontend is deployed to Vercel at `https://n8-assistant-v2.vercel.app`.
- Localization (EN/RU) has been implemented and works seamlessly.
- Authentication UI has been split into "Login" and "Signup" tabs (`?mode=login` / `?mode=signup`).
- Supabase SSR Auth is mostly configured: we added `auth/callback/route.ts` to exchange the email OTP code for a session.

## Blockers / User Action Required
- **Supabase Site URL:** The user needs to manually set the Site URL in Supabase Dashboard -> Auth -> URL Configuration to `https://n8-assistant-v2.vercel.app` so that the email verification links redirect to the correct deployed environment rather than `localhost:3000`.

## Next Immediate Steps (For the next AI Agent)
1. **Onboarding Flow:** After a user registers and confirms their email, they should be redirected to a new Onboarding Quiz (`/onboarding`) to collect:
   - Telegram / Instagram handles
   - Referral/Invite Code
   - "What do you want to automate?" preferences.
2. **Database Schema:** We need to apply SQL migrations in Supabase to create the `users` table with these new fields (telegram_id, telegram_username, invite_code, etc.) and set up a trigger to automatically insert a row when a new user signs up in `auth.users`.
3. **Telegram Bot Setup:** We need the user to provide a valid `TELEGRAM_BOT_TOKEN` so we can activate the Webhook and test the actual bot logic.
