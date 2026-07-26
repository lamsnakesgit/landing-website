import os
import re
import json
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# N8N Encryption Key (получен из docker inspect n8n-n8n-1)
# N8N_ENCRYPTION_KEY = "405672c4692758008257aec4795b777321aa64a5f08720e1"
N8N_ENCRYPTION_KEY_HEX = "405672c4692758008257aec4795b777321aa64a5f08720e1"

# n8n хеширует ключ перед использованием (берет SHA256 от ключа)
derived_key = hashlib.sha256(N8N_ENCRYPTION_KEY_HEX.encode('utf-8')).digest()

def decrypt_n8n_data(encrypted_text):
    try:
        # В n8n зашифрованные данные обычно хранятся в формате iv:ciphertext
        # но в БД они могут лежать в виде строки, содержащей двоеточие
        if not encrypted_text or ":" not in encrypted_text:
            return None
            
        parts = encrypted_text.split(":")
        if len(parts) != 2:
            return None
            
        iv_hex, ciphertext_hex = parts
        iv = bytes.fromhex(iv_hex)
        ciphertext = bytes.fromhex(ciphertext_hex)
        
        # n8n использует AES-256-GCM
        # В AESGCM в python auth tag уже включен в конец ciphertext (в JS/Node.js tag возвращается отдельно, но n8n конкатенирует его)
        aesgcm = AESGCM(derived_key)
        decrypted = aesgcm.decrypt(iv, ciphertext, None)
        return decrypted.decode('utf-8')
    except Exception as e:
        return f"Error: {str(e)}"

# Читаем дамп
dump_path = "06_Scripts_and_Tools/scratch/n8n_creds_dump.txt"
if not os.path.exists(dump_path):
    print("Дамп не найден")
    exit(1)

with open(dump_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Ищем Supabase credentials...")

for line in lines:
    # Ищем строки, где есть supabase
    if "supabase" in line.lower() or "database" in line.lower():
        # Строка в формате psql вывода: id | name | type | data
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 4:
            cid, name, ctype, enc_data = parts[0], parts[1], parts[2], parts[3]
            print(f"\nID: {cid}\nName: {name}\nType: {ctype}\nEncrypted Data: {enc_data[:50]}...")
            
            decrypted = decrypt_n8n_data(enc_data)
            print(f"Decrypted: {decrypted}")
