# Business Plan: AI Video Cloning & Regeneration Platform

## 1. Product Overview
A SaaS platform that allows users to upload a reference video (e.g., a high-end commercial) and "clone" it using Google Veo 3.1. The system analyzes the original, extracts technical prompts, and generates a new version with the user's branding/products.

---

## 2. Technical Architecture

### A. Core Components
1.  **Web Dashboard (Streamlit/Next.js):**
    *   Video upload & preview.
    *   Prompt customization interface.
    *   Gallery of generated clips.
2.  **Telegram Bot (Aiogram/Python-Telegram-Bot):**
    *   Mobile-first interface for quick generation.
    *   Notifications when video is ready.
    *   Subscription management.
3.  **Backend (FastAPI):**
    *   Orchestrates Gemini (Analysis) and Veo (Generation).
    *   Handles Long-Running Operations (LRO) polling.
4.  **Database & Storage (Supabase):**
    *   PostgreSQL for user data and prompt history.
    *   S3-compatible storage for video files.
5.  **Payment Gateway (Stripe/Crypto):**
    *   Pay-per-generation or monthly subscription.

### B. Workflow
`User Upload` -> `Gemini Multimodal Analysis` -> `Prompt Engineering` -> `Veo 3.1 Generation` -> `Cloud Storage` -> `TG/Web Notification`.

---

## 3. Man-Hour Estimation (MVP vs. Production)

| Phase | Task | MVP (Hours) | Production (Hours) |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Architecture & API Integration (Veo/Gemini) | 10 | 20 |
| **Phase 2** | Telegram Bot Development | 15 | 30 |
| **Phase 3** | Web Dashboard (Streamlit for MVP) | 10 | 60 (Next.js) |
| **Phase 4** | Database, Auth & Storage | 10 | 25 |
| **Phase 5** | Payment Integration & Billing | 5 | 20 |
| **Phase 6** | Testing, DevOps & Deployment | 10 | 30 |
| **Total** | | **60 Hours** | **185+ Hours** |

*Note: 60 hours is roughly 2 weeks for one senior developer.*

---

## 4. Monetization Strategy
*   **Starter:** $29/mo (10 generations).
*   **Pro:** $99/mo (50 generations + 4K).
*   **Agency:** $499/mo (Unlimited + API access).

---

## 5. Next Steps for Implementation
1.  Finalize the "Master Prompting" logic (Current Task).
2.  Set up a basic FastAPI wrapper for the generation script.
3.  Connect a Telegram Bot to the FastAPI endpoint.
