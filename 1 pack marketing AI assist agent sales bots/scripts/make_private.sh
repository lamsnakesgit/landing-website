#!/bin/bash
# Удаление публичного доступа для ЭЦП ключей

set -e

BASE_DIR="/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots"
cd "$BASE_DIR"

MATON_API_KEY=$(grep "^MATON_API_KEY=" .env | cut -d'=' -f2- | tr -d '"' | tr -d "'")
BASE_URL="https://gateway.maton.ai/google-drive"

# ID ЭЦП ключей
KEY1="1lXDYvaOJ4NOUS7GNY9TFsKtIuG1jHddy"
KEY2="1XKBqAQMNXs1jTK1_IQDkCX1RlVnhfv5a"

echo "🔒 Удаляем публичный доступ для ЭЦП ключей..."

for FILE_ID in "$KEY1" "$KEY2"; do
    # Получаем список permissions
    PERMS=$(curl -s -X GET \
        -H "Authorization: Bearer $MATON_API_KEY" \
        "$BASE_URL/drive/v3/files/$FILE_ID/permissions?fields=permissions(id,type,role)")

    # Находим permission с type=anyone и удаляем
    ANYONE_PERM=$(echo "$PERMS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data.get('permissions', []):
    if p.get('type') == 'anyone':
        print(p.get('id', ''))
")

    if [ -n "$ANYONE_PERM" ]; then
        echo "  Удаляем permission $ANYONE_PERM для $FILE_ID..."
        curl -s -X DELETE \
            -H "Authorization: Bearer $MATON_API_KEY" \
            "$BASE_URL/drive/v3/files/$FILE_ID/permissions/$ANYONE_PERM"
        echo "  ✅ Закрыто"
    else
        echo "  ℹ️ Публичный доступ не найден для $FILE_ID"
    fi
done

echo ""
echo "🔐 ЭЦП ключи теперь приватные. Доступ только через твой Google аккаунт."