#!/bin/bash
# Загрузка файлов на Google Drive через maton.ai API Gateway

set -e

BASE_DIR="/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots"
cd "$BASE_DIR"

# Загружаем ключ из .env
MATON_API_KEY=$(grep "^MATON_API_KEY=" .env | cut -d'=' -f2- | tr -d '"' | tr -d "'")
if [ -z "$MATON_API_KEY" ]; then
    echo "❌ MATON_API_KEY не найден в .env"
    exit 1
fi

echo "🔑 API ключ загружен"

BASE_URL="https://gateway.maton.ai/google-drive"

# Создаём папку
echo "📁 Создаём папку 'ИИ Юрист'..."
FOLDER_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $MATON_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"name":"ИИ Юрист","mimeType":"application/vnd.google-apps.folder"}' \
    --max-time 30 \
    "$BASE_URL/drive/v3/files")

FOLDER_ID=$(echo "$FOLDER_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))")
if [ -z "$FOLDER_ID" ]; then
    echo "❌ Ошибка создания папки: $FOLDER_RESPONSE"
    exit 1
fi
echo "✅ Папка создана: $FOLDER_ID"

# Файлы для загрузки
FILES=(
    "2 1 контент план_/ilovepdf_converted/Vnesudebnoe-bankrotstvo-v-Kazahstane.pdf"
    "2 1 контент план_/ilovepdf_converted/Bankrotstvo-fizicheskih-lic.pdf"
    "2 1 контент план_/26 12 25 - охват /Долг_Пять_Шагов_До_Банкротства.pdf"
    "2 1 контент план_/26 12 25 - охват /Упрощённый_режим_2026_Кто_исключён карусель номера.pdf"
    "2 1 контент план_/26 12 25 - охват /УПРОЩЁННЫЙ_РЕЖИМ_2026_ИСКЛЮЧЕНИЯ_И_РИСКИ 4 5 горизональо.pdf"
    "2 1 контент план_/26 12 25 - охват /УСН_2026_Обязательный_переход 2я карусель.pdf"
    "2 1 контент план_/26 12 25 - охват /УСН_2026_Ограничения карусель 7-8 1 .pdf"
)

RESULTS_JSON='{"folder_id":"'$FOLDER_ID'","folder_link":"https://drive.google.com/drive/folders/'$FOLDER_ID'","files":['
FIRST=true

for FILE_PATH in "${FILES[@]}"; do
    FULL_PATH="$BASE_DIR/$FILE_PATH"
    if [ ! -f "$FULL_PATH" ]; then
        echo "⚠️ Файл не найден: $FILE_PATH"
        continue
    fi

    FILENAME=$(basename "$FILE_PATH")
    echo "📤 Загружаем: $FILENAME..."

    # Multipart upload через curl
    BOUNDARY="----FormBoundary$(date +%s)"
    METADATA="{\"name\":\"$FILENAME\",\"parents\":[\"$FOLDER_ID\"]}"

    # Создаём временный файл для multipart body
    TMP_BODY=$(mktemp)
    {
        echo "--$BOUNDARY"
        echo "Content-Type: application/json; charset=UTF-8"
        echo "Content-Disposition: form-data; name=\"metadata\""
        echo ""
        echo "$METADATA"
        echo "--$BOUNDARY"
        echo "Content-Type: application/pdf"
        echo "Content-Disposition: form-data; name=\"file\"; filename=\"$FILENAME\""
        echo ""
        cat "$FULL_PATH"
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

        # По умолчанию файлы приватные (безопасность)
        # Чтобы сделать публичным — раскомментируй блок ниже:
        # curl -s -X POST \
        #     -H "Authorization: Bearer $MATON_API_KEY" \
        #     -H "Content-Type: application/json" \
        #     -d '{"role":"reader","type":"anyone"}' \
        #     --max-time 15 \
        #     "$BASE_URL/drive/v3/files/$FILE_ID/permissions" > /dev/null
        # LINK="https://drive.google.com/file/d/$FILE_ID/view?usp=sharing"
        # echo "🔗 Публичная ссылка: $LINK"

        LINK="https://drive.google.com/file/d/$FILE_ID/view (приватно)"
        echo "🔒 Файл приватный (доступ только через Google аккаунт)"

        if [ "$FIRST" = true ]; then
            FIRST=false
        else
            RESULTS_JSON="$RESULTS_JSON,"
        fi
        RESULTS_JSON="$RESULTS_JSON{\"name\":\"$FILENAME\",\"id\":\"$FILE_ID\",\"link\":\"$LINK\"}"
    else
        echo "❌ Ошибка загрузки $FILENAME: $RESPONSE"
    fi
done

RESULTS_JSON="$RESULTS_JSON]}"

# Сохраняем результаты
echo "$RESULTS_JSON" > drive_upload_results.json
echo ""
echo "📊 Готово! Результаты сохранены в drive_upload_results.json"
echo "📁 Папка: https://drive.google.com/drive/folders/$FOLDER_ID"