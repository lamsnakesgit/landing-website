import urllib.request
import urllib.parse
import json

BOT_TOKEN = "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g"
CHAT_ID = "888005446"

text = """Ура! Все 5 web-видео успешно загружены на твой YouTube-канал! 🎉 
В их описании прописана твоя ссылка t.me/nnsvt.

Вот полный список с путями к оригиналам и ссылками на загруженные ролики:

🎥 *Видео 1 (736 МБ)*
Оригинал: `/Users/higherpower/Movies/ai_web_onai_2026-02-17 20-27-17.mov`
Ссылка: https://youtu.be/1Ih5IUXFubw

🎥 *Видео 2 (292 МБ)*
Оригинал: `/Users/higherpower/Movies/ai_web_onai_2026-02-17 21-21-34.mov`
Ссылка: https://youtu.be/_DK4FCg7nrs

🎥 *Видео 3 (245 МБ)*
Оригинал: `/Users/higherpower/Movies/ai ddd ai web klin/ai_web_ddd_2025-10-07 23-54-28.mov`
Ссылка: https://youtu.be/kzkauclYrJ0

🎥 *Видео 4 (241 МБ)*
Оригинал: `/Users/higherpower/Movies/ai_web_onai_2026-02-17 21-37-44.mov`
Ссылка: https://youtu.be/5Oe5N6pJsa8

🎥 *Видео 5 (131 МБ)*
Оригинал: `/Users/higherpower/Movies/ai ddd ai web klin/ai_web_ddd_2025-10-07 02-59-58.mov`
Ссылка: https://youtu.be/IfuEjKecg0I

---
*Ранее залитые вертикальные видео:*

🎥 *Вертикальное Видео 1 (1.3 ГБ)*
Оригинал: `/Users/higherpower/Desktop/1_Active_Projects/AI_Marketing/концентрат 2д конец/web_ai_ledovskikh_vertical_ScreenRecording_10-18-2025 17-16-32_1.MP4`
Ссылка: https://youtu.be/lmGKjQd8wDI

🎥 *Вертикальное Видео 2 (942 МБ)*
Оригинал: `/Users/higherpower/Desktop/1_Active_Projects/AI_Marketing/концентрат 2д конец/web_ai_ledovskikh_vertical_ScreenRecording_10-18-2025 14-18-02_1.MP4`
Ссылка: https://youtu.be/S8qP9bQPA_c

Все ссылки в статусе "доступ по ссылке" (unlisted)."""

data = urllib.parse.urlencode({
    'chat_id': CHAT_ID,
    'text': text,
    'disable_web_page_preview': 'true'
}).encode('utf-8')

req = urllib.request.Request(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data=data,
    method='POST'
)

try:
    with urllib.request.urlopen(req, timeout=30) as response:
        print("Success:", json.loads(response.read().decode('utf-8'))['ok'])
except Exception as e:
    print(f"Error: {e}")
