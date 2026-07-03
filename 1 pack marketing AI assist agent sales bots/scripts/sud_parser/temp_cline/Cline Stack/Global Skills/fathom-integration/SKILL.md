---
name: fathom-integration
description: Интеграция с Fathom API для работы со встречами, transcript/summary, webhook-событиями, SDK, OAuth и выгрузкой video/HLS через share_url. Используй при выгрузке meeting data из Fathom, настройке webhook processing и построении интеграций вокруг Fathom.
---

> **Примечание для экспортной версии:** ниже чувствительные IP, домены, пути, SSH-цели и другие infra-значения заменены на примеры и placeholders вида `<YOUR_...>`. Если ИИ-агенту нужны реальные значения, он должен **подставить реальные данные пользователя** или **сначала запросить их у пользователя**, а не использовать примеры как есть.


# Fathom Integration

Коротко: Fathom даёт REST API, SDK и webhooks для встреч, транскриптов, summary и action items. Дополнительно через публичные `share_url` можно встретить HLS-поток (`video.m3u8`) и `.ts`-чанки, которые реально скачать и собрать в MP4.

## Когда использовать
- нужно получить список встреч из Fathom;
- нужно вытащить transcript, summary или action items по встречам;
- нужно настроить webhook на новые записи встреч;
- нужно выбрать между REST, SDK и OAuth-интеграцией;
- нужно встроить Fathom в backend, n8n, AI-agent pipeline или внутреннюю аналитику;
- нужно попробовать скачать **само видео** по публичному `share_url`;
- нужны **HLS-чанки** записи, а не только итоговый mp4.

## Когда НЕ использовать
- задача вообще не связана с Fathom;
- у тебя уже есть готовый transcript-файл и не нужен доступ к API;
- задача только про generic webhook security без специфики Fathom;
- нужен только fully-supported documented download endpoint: на исследованных official pages прямой first-party endpoint «скачать mp4» не подтверждён.

## Источник истины
- official docs: `https://developers.fathom.ai/`
- quickstart: `https://developers.fathom.ai/quickstart`
- API overview: `https://developers.fathom.ai/api-overview`
- webhooks: `https://developers.fathom.ai/webhooks`
- SDK docs: `https://developers.fathom.ai/sdks`
- reference: `https://developers.fathom.ai/api-reference/meetings/list-meetings`
- reference: `https://developers.fathom.ai/api-reference/recordings/get-transcript`

## Что подтверждено live
- API key реально даёт доступ к `meetings` с пагинацией через `next_cursor`.
- Public `share_url` может отдавать страницу с HLS-ссылкой `video.m3u8`.
- HLS playlist может содержать относительные `video_chunk?...ts` сегменты примерно по 6 секунд.
- `ffmpeg` может собрать этот поток в локальный mp4 без перекодирования.
- `calls/...` URL может требовать логин, а `share_url` при этом оставаться externally viewable.
- Во время сборки возможны предупреждения `Cannot reuse HTTP connection for different host`, `Packet corrupt`, `Non-monotonic DTS` — они часто не фатальны для итогового файла.

## Что важно помнить
- API key создаётся на уровне пользователя и даёт доступ только к встречам, записанным этим пользователем, или встречам, расшаренным на команду.
- Даже admin API key не открывает чужие **unshared** встречи автоматически.
- В REST API базовая аутентификация идёт через заголовок `X-Api-Key`.
- Глобальный rate limit по docs: **60 запросов за 60 секунд**.
- Для API key flow можно получать transcript/summary прямо из `list meetings` через `include_transcript=true` и `include_summary=true`.
- Для OAuth apps transcript и summary нужно получать через recording endpoints, а не через include-поля в `list meetings`.
- `GET /recordings/{recording_id}/transcript` умеет работать синхронно или асинхронно через `destination_url`.
- Webhook verification требует **raw body** до любого JSON parsing.
- `share_url → HLS` — это **практически подтверждённый runtime pattern**, но не надо считать его навсегда стабильным публичным контрактом API.
- Никогда не храни `FATHOM_API_KEY` и `FATHOM_WEBHOOK_SECRET` в коде, skill-файлах, rules, docs или git.

## Рекомендуемый workflow
1. Сначала определить модель доступа: single-user API key или multi-user OAuth.
2. Начать с `GET /external/v1/meetings`, чтобы найти нужные встречи и `recording_id`.
3. Сузить выборку фильтрами: `created_after`, `created_before`, `recorded_by[]`, `teams[]`, `calendar_invitees_domains[]`.
4. Если нужен transcript:
   - API key flow: либо `include_transcript=true` в meetings, либо `GET /recordings/{recording_id}/transcript`;
   - OAuth flow: использовать recording transcript endpoint.
5. Если нужна автоматизация после каждой встречи — поднимать webhook и проверку подписи.
6. Если нужна именно **видеозапись**:
   - взять `share_url` из meetings response;
   - скачать HTML share page;
   - извлечь `video.m3u8`;
   - либо сохранить `.m3u8` и чанки `.ts`, либо собрать mp4 через `ffmpeg`.
7. Если интеграция production-grade — сразу продумывать pagination, retries, 401/403/429 handling, idempotency на webhook consumer и fallback на runtime checks.

## Быстрые рабочие паттерны
- **"Покажи недавние встречи"** → `list meetings`
- **"Найди transcript конкретной встречи"** → `list meetings` → `recording_id` → `get transcript`
- **"Автоматически забирать новые meeting notes"** → `create webhook` → signature verify → queue/worker
- **"Node/TypeScript интеграция"** → REST или `fathom-typescript`
- **"Python backend / cron / ETL"** → REST или `fathom-python`
- **"Скачать видео по share_url"** → share page → `video.m3u8` → `ffmpeg`
- **"Нужны сами куски потока"** → share page → `video.m3u8` → скачать `.ts` сегменты отдельно

## Bundled files
- `docs/fathom-quick-reference.md`
- `templates/list-meetings.ts`
- `templates/list-meetings.py`
- `templates/verify-webhook-node.ts`
- `templates/download-share-hls.py`

## Smoke tests
- Список встреч читается через `X-Api-Key` и возвращает `items` + `next_cursor`.
- Transcript по `recording_id` читается отдельно.
- Webhook signature валидируется по raw body.
- `share_url` при необходимости раскрывается до `video.m3u8`.
- HLS playlist можно сохранить локально и либо скачать чанки, либо собрать mp4.
- 429 и pagination обрабатываются без silent-fail.

## Red flags
- хардкод API key / webhook secret;
- JSON.parse(body) до проверки подписи вебхука;
- ожидание, что admin API key видит все встречи компании;
- игнорирование `next_cursor` и 429;
- использование `include_transcript` в OAuth-сценарии без проверки ограничений;
- слепое предположение, что любой `share_url` всегда даст рабочий `video.m3u8`.
