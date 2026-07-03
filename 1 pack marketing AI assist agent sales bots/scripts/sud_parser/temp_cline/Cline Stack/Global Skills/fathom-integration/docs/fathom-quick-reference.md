# Fathom Quick Reference

Короткая practical-шпаргалка по Fathom API, webhook flow и выгрузке видео через `share_url`.

## Официальные страницы
- Главная: `https://developers.fathom.ai/`
- Quickstart: `https://developers.fathom.ai/quickstart`
- API overview: `https://developers.fathom.ai/api-overview`
- List meetings: `https://developers.fathom.ai/api-reference/meetings/list-meetings`
- Get transcript: `https://developers.fathom.ai/api-reference/recordings/get-transcript`
- Webhooks: `https://developers.fathom.ai/webhooks`
- SDKs: `https://developers.fathom.ai/sdks`

## Безопасные env переменные
```env
FATHOM_API_KEY=<stored_in_secret_manager>
FATHOM_WEBHOOK_SECRET=<stored_in_secret_manager>
FATHOM_BEARER_TOKEN=<optional_for_oauth_or_bearer_flows>
```

## База API
```text
https://api.fathom.ai/external/v1
```

## Аутентификация и модель доступа
- REST quickstart использует `X-Api-Key`.
- SDK docs поддерживают `apiKeyAuth` и `bearerAuth`.
- API key — **user-level**, а не org-wide super-token.
- По docs лимит: **60 запросов / 60 секунд**.

## Минимальные curl-паттерны

### 1) Получить недавние встречи
```bash
curl -sS --get "https://api.fathom.ai/external/v1/meetings"   -H "X-Api-Key: ${FATHOM_API_KEY}"   -H "Accept: application/json"
```

### 2) Сузить встречи по датам и сразу включить transcript/summary
```bash
curl -sS --get "https://api.fathom.ai/external/v1/meetings"   -H "X-Api-Key: ${FATHOM_API_KEY}"   -H "Accept: application/json"   --data-urlencode "created_after=2026-04-01T00:00:00Z"   --data-urlencode "created_before=2026-04-30T23:59:59Z"   --data-urlencode "include_transcript=true"   --data-urlencode "include_summary=true"
```

### 3) Пагинация через `next_cursor`
```bash
curl -sS --get "https://api.fathom.ai/external/v1/meetings"   -H "X-Api-Key: ${FATHOM_API_KEY}"   -H "Accept: application/json"   --data-urlencode "cursor=${FATHOM_CURSOR}"
```

### 4) Получить transcript по `recording_id`
```bash
curl -sS "https://api.fathom.ai/external/v1/recordings/${FATHOM_RECORDING_ID}/transcript"   -H "X-Api-Key: ${FATHOM_API_KEY}"   -H "Accept: application/json"
```

### 5) Асинхронно отправить transcript на свой endpoint
```bash
curl -sS --get "https://api.fathom.ai/external/v1/recordings/${FATHOM_RECORDING_ID}/transcript"   -H "X-Api-Key: ${FATHOM_API_KEY}"   -H "Accept: application/json"   --data-urlencode "destination_url=https://example.com/fathom/transcript"
```

## Что возвращает list meetings
Обычно полезны поля:
- `recording_id`
- `title`
- `meeting_title`
- `created_at`
- `url`
- `share_url`
- `recorded_by`
- `calendar_invitees`
- опционально `transcript`, `default_summary`, `action_items`, `crm_matches`

## SDK notes
- TypeScript SDK: `fathom-typescript`
- Python SDK: `fathom-python`
- В docs SDK помечены как beta, поэтому лучше pin exact version.
- SDK автоматически помогает с pagination и ошибками, но REST проще для прозрачных интеграций и дебага.

## Важное ограничение OAuth
Для OAuth apps docs отдельно отмечают: нельзя полагаться на `include_transcript` и `include_summary` в `list meetings`; нужно идти через recording endpoints.

## Webhooks: практический чек-лист
- Fathom может отправлять webhook после готовности meeting content.
- В payload можно включать transcript, summary и action items.
- В dev можно временно не проверять подпись, но в prod — обязательно.
- Для валидации нужен **raw body**, а не уже распарсенный JSON.

### Заголовки верификации
- `webhook-id`
- `webhook-timestamp`
- `webhook-signature`

### Алгоритм проверки подписи
1. Взять `webhook-id`, `webhook-timestamp`, `webhook-signature` из headers.
2. Собрать строку: `{webhook-id}.{webhook-timestamp}.{raw_body}`.
3. Удалить префикс `whsec_` у секрета и base64-декодировать остаток.
4. Посчитать `HMAC-SHA256` от signed content.
5. Полученный digest закодировать в base64.
6. Сравнить с каждой подписью из `webhook-signature` constant-time способом.
7. Проверить timestamp tolerance, обычно 5 минут.

## Практически подтверждённый HLS-pattern через share_url
Что было подтверждено live на реальной записи:
- `share_url` страница может содержать ссылку на `video.m3u8`.
- Playlist может содержать относительные `.ts` сегменты вида `video_chunk?...00001.ts`.
- `calls/...` URL может редиректить на sign_in, а `share_url` при этом быть externally viewable.
- `audio_url` тоже может присутствовать в данных share page.

### Что это значит practically
- Если нужен **итоговый mp4**, можно использовать `ffmpeg`.
- Если наоборот нужны **сами чанки**, можно сохранить `.m3u8` и скачать перечисленные `.ts`-сегменты отдельно.
- Это полезно для:
  - локального архива,
  - chunk-level обработки,
  - пост-анализа по сегментам,
  - нестандартных pipeline’ов, где mp4 не нужен сразу.

### Как найти `video.m3u8`
Самый простой практический путь:
1. скачать HTML `share_url`;
2. unescape HTML entities;
3. найти строку `.../video.m3u8`;
4. скачать playlist.

### Скачать mp4 из `video.m3u8`
```bash
ffmpeg -y   -protocol_whitelist file,http,https,tcp,tls,crypto   -i "https://fathom.video/share/<TOKEN>/video.m3u8"   -c copy   -bsf:a aac_adtstoasc   output.mp4
```

### Оставить чанки, а не только mp4
1. сохранить сам playlist `.m3u8`;
2. распарсить все строки без `#`;
3. превратить относительные пути в абсолютные URL;
4. скачать `.ts` сегменты по одному.

Готовый шаблон смотри в:
- `templates/download-share-hls.py`

## Что означают warning'и ffmpeg
### `Cannot reuse HTTP connection for different host`
- playlist мог открываться с `fathom.video`, а сами сегменты фактически отдаваться через другое storage/backend-host;
- ffmpeg просто открывает новое соединение;
- обычно это не фатально.

### `Packet corrupt`
- некоторые `.ts` сегменты могут иметь неидеальные transport packets;
- для HLS на стыках чанков это бывает;
- часто файл всё равно собирается успешно.

### `Non-monotonic DTS`
- у части пакетов таймкоды шли неидеально по порядку;
- ffmpeg обычно сам чинит timestamps при mux/remux;
- это warning упаковки потока, а не обязательный признак сломанного видео.

## Практические рекомендации
- Для новых интеграций начинай с REST + curl/httpx/fetch, потом при необходимости переходи на SDK.
- На ingestion pipeline используй idempotency по `webhook-id`.
- Transcript и summary могут быть довольно большими — продумай storage и chunking заранее.
- Для аналитики не тащи весь transcript в память пачками без pagination/streaming стратегии.
- Если ключ уже был передан в чат или shared вне secret manager — лучше его ротировать.
- `share_url → HLS` удобно считать рабочим runtime-паттерном, но не обещай это как вечный стабильный API-контракт без live-проверки.
