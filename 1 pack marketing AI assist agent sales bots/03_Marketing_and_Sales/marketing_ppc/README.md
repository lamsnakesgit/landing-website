# Marketing PPC: Meta Ads Automation (n8n)

Этот модуль предназначен для автоматизации Meta Ads через n8n, Google Sheets и AI-агентов.

## Структура воркфлоу
- `MetaAds-MainAISystem.json`: AI-оркестратор на базе Gemini.
- `FbAdsPosting-Automation.json`: Узел для создания кампаний и объявлений.
- `MCP-FbAds-Server.json`: MCP-сервер для связи AI с Facebook API.

## Как запустить
1. Создайте копию [Google Sheet шаблона](https://docs.google.com/spreadsheets/d/1TfaTeOto0ZQG_OmvVdVz82S3_4C-DGYHibh7fidX0ys/).
2. В n8n импортируйте все JSON файлы.
3. Настройте Credentials:
    - Facebook Graph API (Access Token).
    - Google Sheets OAuth2.
    - Google Gemini API Key.
4. **ВАЖНО**: Замените Account ID (`act_XXXXXXXXX`) в нодах MetaAdsData и Fb-Ads-Posting на свои.

## Аналитика производительности
Система использует формулу для оценки эффективности объявлений:
`Score = 0.40×ROAS + 0.20×CTR + 0.15×(1-CPC) + 0.15×Conversions + 0.10×Spend`
