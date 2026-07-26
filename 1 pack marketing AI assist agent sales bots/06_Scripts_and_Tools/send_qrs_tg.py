import requests

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"

def send_photo(file_path, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(file_path, 'rb') as f:
        files = {'photo': f}
        data = {'chat_id': CHAT_ID, 'caption': caption}
        response = requests.post(url, files=files, data=data)
        print(response.json())

send_photo('/Users/higherpower/.gemini/antigravity/brain/2fa02fa9-a75a-44b3-be42-ab46eca2fece/qr1.png', 'QR-код для Инстанса 1 (number1)')
send_photo('/Users/higherpower/.gemini/antigravity/brain/2fa02fa9-a75a-44b3-be42-ab46eca2fece/qr2.png', 'QR-код для Инстанса 2 (number2)')
