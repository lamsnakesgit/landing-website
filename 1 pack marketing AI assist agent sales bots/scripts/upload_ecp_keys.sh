#!/bin/bash
# Загрузка ЭЦП ключей на Google Drive через maton.ai

set -e

BASE_DIR="/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots"
cd "$BASE_DIR"

MATON_API_KEY=$(grep "^MATON_API_KEY=" .env | cut -d'=' -f2- | tr -d '"' | tr -d "'")
if [ -z "$MATON_API_KEY" ]; then
    echo "❌ MATON_API_KEY не найден"
    exit 1
fi

BASE_URL="https://gateway.maton.ai/google-drive"

# ID папки "ИИ Юрист" (из предыдущей загрузки)
FOLDER_ID="12ttgoADDaYSL27lvSSFDDoV-6dbGcUIf"

# Файлы ЭЦП
KEYS=(
    "/Users/higherpower/Downloads/GOST512_29d29484fbd0d48f561ca129fa2190b46e8592a5.p12"
    "/Users/higherpower/Downloads/GOST512_2b70d42839078d60ab76e96e51be0316a12cb425.p12"
)

echo "🔑 Загружаем ЭЦП ключи в папку 'ИИ Юрист'..."

for KEY_PATH in "${KEYS[@]}"; do
    if [ ! -f "$KEY_PATH" ]; then
        echo "⚠️ Файл не найден: $KEY_PATH"
        continue
    fi

    FILENAME=$(basename "$KEY_PATH")
    echo "📤 Загружаем: $FILENAME..."

    BOUNDARY="----FormBoundary$(date +%s)"
    METADATA="{\"name\":\"$FILENAME\",\"parents\":[\"$FOLDER_ID\"]}"

    TMP_BODY=$(mktemp)
    {
        echo "--$BOUNDARY"
        echo "Content-Type: application/json; charset=UTF-8"
        echo "Content-Disposition: form-data; name=\"metadata\""
        echo ""
        echo "$METADATA"
        echo "--$BOUNDARY"
        echo "Content-Type: application/x-pkcs12"
        echo "Content-Disposition: form-data; name=\"file\"; filename=\"$FILENAME\""
        echo ""
        cat "$KEY_PATH"
        echo ""
        echo "--$BOUNDARY--"
    } > "$TMP_BODY"

    RESPONSE=$(curl -s -X POST \
        -H "Authorization: Bearer $MATON_API_KEY" \
        -H "Content-Type: multipart/form-data; boundary=$BOUNDARY" \
        --data-binary @"$TMP_BODY" \
        --max-time 60 \
        "$BASE_URL/upload/drive/v3/files?uploadType=multipart")

    rm -f "$TMP_BODY"

    FILE_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))")

    if [ -n "$FILE_ID" ]; then
        echo "✅ Загружено: $FILENAME → $FILE_ID"
        echo "🔒 Файл приватный (доступ только через Google аккаунт)"
    else
        echo "❌ Ошибка: $RESPONSE"
    fi
done

echo ""
echo "✅ ЭЦП ключи загружены!"