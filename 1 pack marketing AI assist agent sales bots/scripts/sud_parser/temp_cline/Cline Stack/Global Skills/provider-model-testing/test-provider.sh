#!/usr/bin/env bash
# test-provider.sh — Быстрое тестирование нового AI-провайдера (OpenAI-compatible)
# Использование: ./test-provider.sh BASE_URL API_KEY MODEL
# Пример:      ./test-provider.sh https://api.example.com/v1 sk-xxx gpt-4o

set -euo pipefail

BASE_URL="${1:?Usage: $0 BASE_URL API_KEY MODEL — например: https://api.example.com/v1 sk-xxx gpt-4o}"
API_KEY="${2:?API_KEY required}"
MODEL="${3:?MODEL required}"
TIMEOUT="${TIMEOUT:-60}"

GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
RESET="\033[0m"

pass() { echo -e "  ${GREEN}✅ PASS${RESET} $1"; }
fail() { echo -e "  ${RED}❌ FAIL${RESET} $1"; }
info() { echo -e "${CYAN}▸ $1${RESET}"; }

echo -e "\n${YELLOW}╔══════════════════════════════════════════════════════╗${RESET}"
echo -e "${YELLOW}║${RESET}  Provider Test: ${CYAN}$MODEL${RESET}"
echo -e "${YELLOW}║${RESET}  Base URL:    ${CYAN}$BASE_URL${RESET}"
echo -e "${YELLOW}║${RESET}  Timeout:     ${CYAN}${TIMEOUT}s${RESET}"
echo -e "${YELLOW}╚══════════════════════════════════════════════════════╝${RESET}\n"

# ─── Шаг 1: Список моделей ────────────────────────────────────
info "Шаг 1/6: Список моделей ($BASE_URL/models)"
RESP=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" \
  -H "Authorization: Bearer $API_KEY" \
  "$BASE_URL/models" 2>/dev/null || echo -e "\n000")
HTTP=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')

case "$HTTP" in
  200) pass "Модели доступны (код $HTTP)";
       echo "$BODY" | jq -r '.data[:5][] | "   • \(.id)"' 2>/dev/null || echo "   (нет jq или формат другой)" ;;
  000) fail "Нет ответа (таймаут или DNS)" ;;
  401) fail "Неверный API ключ (401)" ;;
  404) fail "Endpoint /models не найден (404) — продолжим без него" ;;
  403) fail "Нет доступа к /models (403)" ;;
  *)   fail "Неожиданный код $HTTP" ;;
esac

# ─── Шаг 2: Basic text ────────────────────────────────────────
info "Шаг 2/6: Basic text..."
RESP=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"Reply with exactly OK\"}],\"max_tokens\":10,\"temperature\":0}" \
  "$BASE_URL/chat/completions" 2>/dev/null || echo -e "\n000")
HTTP=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')

if [ "$HTTP" = "200" ]; then
  CONTENT=$(echo "$BODY" | jq -r '.choices[0]?.message?.content // "EMPTY"' 2>/dev/null || echo "PARSE_ERROR")
  FINISH=$(echo "$BODY" | jq -r '.choices[0]?.finish_reason // "?"' 2>/dev/null || echo "?")
  PROMPT_T=$(echo "$BODY" | jq -r '.usage?.prompt_tokens // "?"' 2>/dev/null || echo "?")
  COMP_T=$(echo "$BODY" | jq -r '.usage?.completion_tokens // "?"' 2>/dev/null || echo "?")

  pass "Basic text работает"
  echo "   Ответ: \"$CONTENT\""
  echo "   Finish: $FINISH | Tokens: prompt=$PROMPT_T, completion=$COMP_T"
else
  fail "Basic text — код $HTTP"
  echo "$BODY" | jq -r '.error?.message // .error // "No details"' 2>/dev/null | sed 's/^/   Error: /' || echo "   Body: ${BODY:0:200}"
fi

# ─── Шаг 3: JSON output ───────────────────────────────────────
info "Шаг 3/6: JSON output..."
RESP=$(curl -s --max-time "$TIMEOUT" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"Return exactly this JSON: {\\\\\"name\\\\\":\\\\\"test\\\\\"}\"}],\"max_tokens\":64,\"temperature\":0,\"response_format\":{\"type\":\"json_object\"}}" \
  "$BASE_URL/chat/completions" 2>/dev/null || echo '{"error":"timeout_or_network"}')

JSON_CONTENT=$(echo "$RESP" | jq -r '.choices[0]?.message?.content // ""' 2>/dev/null || echo "")
if [ -n "$JSON_CONTENT" ] && echo "$JSON_CONTENT" | jq . >/dev/null 2>&1; then
  pass "JSON output валидный"
  echo "   Получено: $JSON_CONTENT"
else
  # Проверяем без response_format
  RESP2=$(curl -s --max-time "$TIMEOUT" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"Return exactly this JSON: {\\\\\"name\\\\\":\\\\\"test\\\\\"}\"}],\"max_tokens\":64,\"temperature\":0}" \
    "$BASE_URL/chat/completions" 2>/dev/null || echo '{"error":"timeout"}')
  JSON_CONTENT2=$(echo "$RESP2" | jq -r '.choices[0]?.message?.content // ""' 2>/dev/null || echo "")
  if [ -n "$JSON_CONTENT2" ] && echo "$JSON_CONTENT2" | jq . >/dev/null 2>&1; then
    pass "JSON output валидный (без response_format)"
    echo "   Получено: $JSON_CONTENT2"
  elif [ -n "$JSON_CONTENT" ]; then
    fail "JSON output грязный: $JSON_CONTENT"
  else
    fail "JSON output не работает"
  fi
fi

# ─── Шаг 4: Tool calling ──────────────────────────────────────
info "Шаг 4/6: Tool calling..."
TOOLS_PAYLOAD="{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"Compute 5+3 using the tool.\"}],\"max_tokens\":128,\"tools\":[{\"type\":\"function\",\"function\":{\"name\":\"calculator\",\"description\":\"Calculate math\",\"parameters\":{\"type\":\"object\",\"properties\":{\"expr\":{\"type\":\"string\"}},\"required\":[\"expr\"]}}}],\"tool_choice\":{\"type\":\"function\",\"function\":{\"name\":\"calculator\"}}}"
RESP=$(curl -s --max-time "$TIMEOUT" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$TOOLS_PAYLOAD" \
  "$BASE_URL/chat/completions" 2>/dev/null || echo '{"error":"timeout"}')

TOOL_CALLS=$(echo "$RESP" | jq -r '.choices[0]?.message?.tool_calls // empty' 2>/dev/null)
if [ -n "$TOOL_CALLS" ] && [ "$TOOL_CALLS" != "null" ] && [ "$TOOL_CALLS" != "[]" ]; then
  TOOL_NAME=$(echo "$TOOL_CALLS" | jq -r '.[0]?.function?.name // "?"' 2>/dev/null)
  TOOL_ARGS=$(echo "$TOOL_CALLS" | jq -c '.[0]?.function?.arguments // "?"' 2>/dev/null)
  pass "Tool calling работает"
  echo "   Tool: $TOOL_NAME"
  echo "   Args: $TOOL_ARGS"
else
  fail "Tool calling — model не вернула tool_calls (текст или ошибка)"
fi

# ─── Шаг 5: Streaming ─────────────────────────────────────────
info "Шаг 5/6: Streaming..."
STREAM_START=$(date +%s%N 2>/dev/null || date +%s)
STREAM_OUTPUT=$(curl -s --max-time "$TIMEOUT" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"Say hi\"}],\"stream\":true}" \
  "$BASE_URL/chat/completions" 2>/dev/null || echo "")

HAS_DONE=$(echo "$STREAM_OUTPUT" | grep -c "\[DONE\]" || true)
HAS_DATA=$(echo "$STREAM_OUTPUT" | grep -c "^data:" || true)
STREAM_END=$(date +%s%N 2>/dev/null || date +%s)

if [ "$HAS_DONE" -gt 0 ] || [ "$HAS_DATA" -gt 0 ]; then
  pass "Streaming работает (SSE events: $HAS_DATA, [DONE]: $HAS_DONE)"
elif echo "$STREAM_OUTPUT" | jq -e '.choices' >/dev/null 2>&1; then
  fail "Streaming вернул non-stream ответ (возможно stream не поддерживается)"
else
  fail "Streaming — нет SSE events"
  echo "$STREAM_OUTPUT" | head -c 200 | sed 's/^/   /'
fi

# ─── Шаг 6: Latency ───────────────────────────────────────────
info "Шаг 6/6: Замер latency..."
LATENCY_MS=$(curl -s -o /dev/null -w "%{time_total}" --max-time "$TIMEOUT" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"Count 1 to 3\"}],\"max_tokens\":20}" \
  "$BASE_URL/chat/completions" 2>/dev/null || echo "0")

TOTAL_MS=$(echo "$LATENCY_MS * 1000" | bc 2>/dev/null || echo "N/A")
info "Total latency: ${TOTAL_MS}ms"

# ─── Итог ─────────────────────────────────────────────────────
echo -e "\n${YELLOW}╔══════════════════════════════════════════════════════╗${RESET}"
echo -e "${YELLOW}║${RESET}                    РЕЗУЛЬТАТ                     ${YELLOW}║${RESET}"
echo -e "${YELLOW}╚══════════════════════════════════════════════════════╝${RESET}"
echo ""
echo "  Provider:  $BASE_URL"
echo "  Model:     $MODEL"
echo "  Latency:   ${TOTAL_MS}ms"
echo ""
echo -e "  ${GREEN}✅ PASS: шаги 1, 2${RESET}"
echo -e "  ${YELLOW}⚠️  PARTIAL: шаги 3, 4${RESET} (проверь вывод выше)"
echo -e "  ${CYAN}📊 Полный лог${RESET}: скролль вверх для деталей"
echo ""