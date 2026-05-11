import urllib.request
import json
import ssl

url = "https://wapi.aiconicagepro.duckdns.org/instance/create"
headers = {
    "apikey": "evolAPISecretKey_2026",
    "Content-Type": "application/json"
}
data = {
    "instanceName": "SalesBot",
    "qrcode": True,
    "integration": "WHATSAPP-BAILEYS"
}

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
# Ignoring SSL warnings if any (shouldn't be, since we have let's encrypt setup)
context = ssl.create_default_context()

try:
    with urllib.request.urlopen(req, context=context) as response:
        resp_data = json.loads(response.read().decode('utf-8'))
        
        if 'qrcode' in resp_data and 'base64' in resp_data['qrcode']:
            base64_qr = resp_data['qrcode']['base64']
            html_content = f"""
            <html>
                <body>
                    <h2>Scan this QR Code with your WhatsApp</h2>
                    <p>Open WhatsApp > Linked Devices > Link a Device.</p>
                    <img src="{base64_qr}" />
                </body>
            </html>
            """
            with open("whatsapp_qr.html", "w") as f:
                f.write(html_content)
            print("QR Code generated successfully! Saved to whatsapp_qr.html")
        else:
            print("Response didn't contain QR base64:", resp_data)
except Exception as e:
    print("Failed to create instance:", e)
