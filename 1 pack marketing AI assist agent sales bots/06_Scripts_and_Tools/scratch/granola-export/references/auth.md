# Granola Authentication — Reference

> Detail on how Granola authenticates Mac app users to the API. Read this when the auth path needs debugging or when adapting the skill to a new platform.

## TL;DR

- Active IdP: **WorkOS** (since some 2025 migration)
- Legacy IdP: **AWS Cognito** — tokens still stored in `supabase.json` but expired and unused
- Token transport: **Bearer** in `Authorization` header
- Token TTL: ~**1 hour** for the WorkOS access_token; refresh_token is long-lived
- Storage: `~/Library/Application Support/Granola/supabase.json`
- Refresh path: WorkOS OAuth2 token endpoint at `https://auth.granola.ai/oauth2/token`

The Cognito tokens in `supabase.json` are a leftover from before the WorkOS migration. They're typically long-expired but still present in the file — Granola doesn't clean them up. Don't be confused by them; use the WorkOS token instead.

## File location and shape

```
~/Library/Application Support/Granola/supabase.json
```

Top-level keys:
- `cognito_tokens` — string (JSON-encoded). Legacy. Ignore.
- `workos_tokens` — string (JSON-encoded). The active one.
- `session_id` — string. Format: `session_<base64ish>`. Used as a cookie/correlation ID, not for API auth.
- `user_info` — string (JSON-encoded). User profile snapshot (email, id, workspace_ids, scopes, etc.).

**Important quirk:** every value is **JSON-stringified inner JSON**, not nested objects. So you must double-decode:

```python
data = json.loads(open(SUPABASE_FILE).read())
workos = json.loads(data["workos_tokens"])     # second parse
access_token = workos["access_token"]
```

…or in jq:

```bash
jq -r '.workos_tokens' supabase.json | jq -r '.access_token'
```

## WorkOS token shape

`workos_tokens` (after double-decoding) contains:

```json
{
  "access_token": "<jwt>",
  "id_token": "<jwt>",
  "refresh_token": "<opaque-string>",
  "token_type": "Bearer",
  "expires_in": 3600,
  "obtained_at": <ms-since-epoch>,
  "external_id": "<workos-internal>",
  "session_id": "<workos-session>",
  "sign_in_method": "google_oauth" | "microsoft_oauth" | ...
}
```

JWT claims of the access_token:
- `iss`: `https://auth.granola.ai/user_management/<client_id>`
- `client_id`: WorkOS user-management client (format: `client_<base32-ish>`)
- `sub`: WorkOS user ID
- `external_id`: usually empty
- `workos_id`: WorkOS user ID (duplicate of sub)
- `sid`: session ID
- `iat`, `exp`, `jti`

`exp` minus `iat` is consistently 3600 seconds.

## Cognito tokens (legacy, ignore)

`cognito_tokens` contains the standard AWS Cognito flow output (`access_token`, `id_token`, `refresh_token`, `expires_in`, `obtained_at`, `token_type`). The issuer is `https://cognito-idp.us-east-1.amazonaws.com/us-east-1_3dOOyNq16`. These are not used by the current API — they're vestigial.

If you see them as fresh on a recently-migrated account, the API will *probably* still accept them as Bearer tokens (Granola's backend likely supports both during a migration window), but the **WorkOS path is canonical**. Use WorkOS.

## Auth header

Standard:

```
Authorization: Bearer <workos_tokens.access_token>
Content-Type: application/json
Accept: application/json
Accept-Encoding: gzip
User-Agent: Granola/7.155.1 (macOS)
```

The User-Agent doesn't seem to be enforced server-side, but matching the desktop app's identifier is polite and avoids any cargo-culted "no UA = block" rules.

**Always set `Accept-Encoding: gzip`** and decompress on the client (curl: `--compressed`). All Granola JSON responses are gzipped, and without this you'll get binary garbage.

## Refresh flow

When the access_token expires (~1h), use the refresh_token to mint a new one via the standard OAuth2 token endpoint:

```bash
REFRESH=$(jq -r '.workos_tokens' supabase.json | jq -r '.refresh_token')
CLIENT_ID=$(echo "$ACCESS_OLD" | cut -d. -f2 | base64 -d | jq -r '.client_id')

curl -X POST 'https://auth.granola.ai/oauth2/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "grant_type=refresh_token" \
  --data-urlencode "refresh_token=$REFRESH" \
  --data-urlencode "client_id=$CLIENT_ID"
```

Response:

```json
{
  "access_token": "<new-jwt>",
  "token_type": "Bearer",
  "expires_in": 3600,
  ...
}
```

The `scripts/refresh_token.sh` helper does exactly this and prints just the new token.

**Note:** the refresh script does *not* write the new token back to `supabase.json`. Granola's desktop app maintains that file on its own schedule, and rewriting it could confuse the app's state machine. For one-off refreshes, just keep the new token in an env var (`export TOKEN=$(./refresh_token.sh)`).

**Easiest fallback if refresh fails:** open the Granola desktop app for a few seconds. It silently refreshes its own token on launch and writes a fresh one back to `supabase.json`. Then re-run extract.py.

## Why the file is named `supabase.json`

Granola probably bootstrapped on Supabase Auth (which itself wraps multiple IdPs) and kept the filename through the WorkOS migration. The file *contains* WorkOS + Cognito tokens, but the name is a misleading historical artifact. Don't expect Supabase patterns elsewhere — none of their API endpoints look Supabase-shaped.

## Multi-account

`stored-accounts.json` (also in the same dir) has an `accounts` array — Granola supports account switching. The active account's tokens go into `supabase.json`; the rest are stashed in `stored-accounts.json`. The multi-account flow wasn't probed in detail; if you need to extract from a non-active account, either switch in the desktop app first OR parse `stored-accounts.json` to find the right token.

## Auth-related feature flags worth knowing

From `local-state.json`:

| Flag | Default | Meaning |
|------|---------|---------|
| `swap_tokens_enabled` | `true` | Active token rotation |
| `refresh_access_token_backend_enabled` | `false` | Server-side refresh logic disabled — refresh is currently client-driven |
| `auth_handoff_enabled` | `true` | Cross-device auth handoff supported |
| `microsoft_login_enabled`, `real_microsoft_login_enabled` | `true` | MS SSO active |
| `sso_enabled` | `true` | WorkOS SSO active |
| `workos_enabled` | `true` | WorkOS path is on |
| `workos_dsync_enabled` | `true` | WorkOS Directory Sync on |

If `refresh_access_token_backend_enabled` flips to `true` in some future build, the token endpoint or refresh shape may change. Re-test the refresh flow before assuming it still works.

## What this skill does NOT do (intentionally)

- Does not test the OAuth2 login from scratch — uses the existing session
- Does not probe `auth_handoff_complete` or device-session endpoints
- Does not test Microsoft-SSO sign-in
- Does not live-verify the refresh script against an expired token (JWT decode portion is verified; the WorkOS token URL is inferred from the issuer claim)

For a hardened production version, test the refresh path against a real expired access_token to confirm the WorkOS endpoint shape. The most likely deviation is in the path: WorkOS uses `/oauth2/token` for OIDC compliance, but custom-deployed instances sometimes expose `/sso/token` or similar. If 404, try variants.
