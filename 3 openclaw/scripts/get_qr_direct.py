import urllib.request
import json
import ssl
import os
import time

url_connect = "https://wapi.aiconicagepro.duckdns.org/instance/connect/salesbot1"
headers = {
    "apikey": "evolAPISecretKey_2026",
    "Content-Type": "application/json"
}

context = ssl.create_default_context()
req_connect = urllib.request.Request(url_connect, headers=headers, method='GET')

print("Ожидание генерации QR-кода от WhatsApp (может занять до 20 секунд)...")

for i in range(10):
    try:
        with urllib.request.urlopen(req_connect, context=context) as response:
            resp_data = json.loads(response.read().decode('utf-8'))
            if 'base64' in resp_data and resp_data['base64']:
                base64_qr = resp_data['base64']
                
                # Сохраняем прямо на рабочий стол в папку проекта!
                project_dir = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/3 openclaw"
                html_path = os.path.join(project_dir, "whatsapp_qr_code.html")
                
                html_content = f"""
                <html>
                    <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
                        <h2>Step 1: Open WhatsApp on your phone</h2>
                        <p>Menu > Linked Devices > Link a Device.</p>
                        <img src="{base64_qr}" style="border: 2px solid #ccc; padding: 10px; border-radius: 10px; max-width: 400px;" />
                        <p><i>If the code expires, ask AI to generate a new one.</i></p>
                    </body>
                </html>
                """
                
                with open(html_path, "w") as f:
                    f.write(html_content)
                    
                print(f"✅ УРА! QR-код успешно получен и сохранен в файл:")
                print(f"👉 {html_path}")
                print("\nСейчас файл откроется в вашем браузере автоматически...")
                
                # Открываем через встроенную утилиту Mac
                os.system(f"open '{html_path}'")
                exit(0)
            else:
                print(f"[{i+1}/10] QR-код еще не сгенерирован (инициализация сессии)... Ждем 4 секунды.")
                time.sleep(4)
    except Exception as e:
        print(f"[{i+1}/10] Ошибка связи с сервером:", e)
        time.sleep(4)

print("❌ Не удалось получить QR-код. Возможно, сессия зависла в контейнере.")
