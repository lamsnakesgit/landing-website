#!/usr/bin/env bash
# refresh_token.sh — Mint a fresh WorkOS access token for Granola.
#
# Why you'd run this:
#   Granola's WorkOS access token has a ~1h TTL. If extract.py errors with
#   "WorkOS access token expired", you can either re-open the Granola desktop
#   app (which silently refreshes) OR call this script.
#
# What it does:
#   Reads the refresh_token from supabase.json, hits WorkOS's OAuth2 token
#   endpoint, and prints the new access_token to stdout. Does NOT modify
#   supabase.json (the desktop app would get confused). Use the printed
#   token in-process or set it as an env var for one-off curl calls.
#
# Usage:
#   ./refresh_token.sh                      # print new access_token
#   export TOKEN=$(./refresh_token.sh)      # use in shell session
#
# The simplest fallback if this script fails: open the Granola desktop app
# briefly. The app refreshes its own token on launch and writes a fresh one
# back into supabase.json.

set -euo pipefail

SUPABASE_FILE="$HOME/Library/Application Support/Granola/supabase.json"

if [ ! -f "$SUPABASE_FILE" ]; then
  echo "supabase.json not found at $SUPABASE_FILE" >&2
  echo "Is the Granola Mac app installed and logged in?" >&2
  exit 1
fi

REFRESH=$(jq -r '.workos_tokens' "$SUPABASE_FILE" | jq -r '.refresh_token // empty')
ACCESS_OLD=$(jq -r '.workos_tokens' "$SUPABASE_FILE" | jq -r '.access_token // empty')

if [ -z "$REFRESH" ]; then
  echo "No refresh_token in workos_tokens" >&2
  exit 1
fi

# client_id is in the existing access token's claims.
# JWT payloads are base64url-encoded (uses _- instead of /+) and may be unpadded;
# `base64 -d` on macOS is strict, so we translate URL-safe chars and pad to 4 first.
PAYLOAD=$(echo "$ACCESS_OLD" | cut -d. -f2 | tr '_-' '/+')
case $(( ${#PAYLOAD} % 4 )) in
  2) PAYLOAD="${PAYLOAD}==" ;;
  3) PAYLOAD="${PAYLOAD}="  ;;
esac
CLIENT_ID=$(printf '%s' "$PAYLOAD" | base64 -d 2>/dev/null | jq -r '.client_id // empty')

if [ -z "$CLIENT_ID" ]; then
  echo "Could not derive client_id from existing access_token" >&2
  echo "Easiest fix: open the Granola desktop app — it'll silently refresh on launch." >&2
  exit 1
fi

# WorkOS OIDC token endpoint at the auth.granola.ai domain.
# **NOTE**: this exact path is inferred from the issuer claim, not verified live.
# If you get 404 here, falling back to opening the desktop app is the simplest path.
RESPONSE=$(curl -sS -X POST 'https://auth.granola.ai/oauth2/token' \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "User-Agent: Granola/7.155.1 (macOS)" \
  --data-urlencode "grant_type=refresh_token" \
  --data-urlencode "refresh_token=$REFRESH" \
  --data-urlencode "client_id=$CLIENT_ID")

NEW_TOKEN=$(echo "$RESPONSE" | jq -r '.access_token // empty')

if [ -z "$NEW_TOKEN" ]; then
  echo "Refresh failed. Response was:" >&2
  echo "$RESPONSE" >&2
  echo "" >&2
  echo "Try opening the Granola desktop app — it'll silently refresh on launch." >&2
  exit 1
fi

# Print just the token so callers can `export TOKEN=$(./refresh_token.sh)`
echo "$NEW_TOKEN"
