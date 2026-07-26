"""
Карусель «CLAUDE ЗАБАНИЛИ» — Vertex AI Imagen 3.0 (картинки-фоны) + Pillow (текст).
Формат: 1080x1080 (1:1) для Instagram.
"""
import google.auth
from google.auth.transport.requests import Request
import requests
import base64
import os
import time
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# ─── Vertex AI ───────────────────────────────────────────────────
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "vertex_sa.json"
)
credentials, project_id = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
credentials.refresh(Request())

LOCATIONS = ["us-east4", "us-west1", "europe-west1", "europe-west4"]

# ─── Telegram ────────────────────────────────────────────────────
TG_BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN", "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g")
TG_CHAT_ID = "888005446"

# ─── Шрифт ───────────────────────────────────────────────────────
FONT_BOLD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Montserrat-Bold.ttf")
CANVAS = 1080


# ─── Слайды: Imagen_prompt (только фон) + Pillow текст ───────────
SLIDES = [
    {
        "name": "1_HUK",
        "caption": "1️⃣ ХУК — CLAUDE ЗАБАНИЛИ",
        "bg_prompt": (
            "Cinematic close-up mugshot of a sleek humanoid robot in an orange prison uniform, "
            "glowing red eyes, cyberpunk neon prison lighting, gangster movie aesthetic, "
            "dramatic shadows, dark moody atmosphere, photorealistic, vertical composition. "
            "No text, no words, no letters, no writing."
        ),
        "headline": "CLAUDE\nЗАБАНИЛИ.\nКТО\nДАЛЬШЕ?",
        "subtext": "Сначала они молча забанили тысячи\nаккаунтов Claude. Без объяснения причин.\nКто следующий?",
        "watermark": "@lamanopro_  x  @aiconicvibe",
    },
    {
        "name": "2_ESKALACIYA",
        "caption": "2️⃣ ЭСКАЛАЦИЯ — ПЕРМАБАН",
        "bg_prompt": (
            "A futuristic prison cell door slamming shut with glowing red laser bars, "
            "dark moody cinematic gangster style, gritty atmosphere, photorealistic. "
            "No text, no words, no letters, no writing."
        ),
        "headline": "ШАГ ВЛЕВО —\nПЕРМАБАН",
        "subtext": "Цензура ИИ дошла до полного абсурда.\nШаг влево — и ты ловишь пермабан\nбез возврата денег.",
        "watermark": "@lamanopro_  x  @aiconicvibe",
    },
    {
        "name": "3_OSOZNANIE",
        "caption": "3️⃣ ОСОЗНАНИЕ — ИИ НЕ ТВОЙ",
        "bg_prompt": (
            "A ruthless mafia boss in a dark expensive suit burning a 20 dollar bill with a neon lighter, "
            "digital glowing chains breaking around him, dark moody cinematic gangster aesthetic, photorealistic. "
            "No text, no words, no letters, no writing."
        ),
        "headline": "ЭТОТ ИИ\nНЕ ТВОЙ",
        "subtext": "Ты платишь $20 каждый месяц.\nНо этот ИИ тебе НЕ принадлежит.\nТебя могут просто отключить.",
        "watermark": "@lamanopro_  x  @aiconicvibe",
    },
    {
        "name": "4_RESHENIE",
        "caption": "4️⃣ РЕШЕНИЕ — СВОЯ НЕЙРОСЕТЬ",
        "bg_prompt": (
            "A hacker in a sharp mafia suit forcefully cracking a massive glowing digital vault, "
            "bright blue neon light inside, cyberpunk high contrast, symbol of rebellion, photorealistic. "
            "No text, no words, no letters, no writing."
        ),
        "headline": "СВОЯ ЛИЧНАЯ\nНЕЙРОСЕТЬ",
        "subtext": "Никакой цензуры, никаких правил.\nТвой ИИ подчиняется только тебе.",
        "watermark": "@lamanopro_  x  @aiconicvibe",
    },
    {
        "name": "5_CENNOST",
        "caption": "5️⃣ ЦЕННОСТЬ — OPEN-SOURCE",
        "bg_prompt": (
            "A lineup of powerful sleek cyber-mobsters standing outside a prison in rainy streets, "
            "unstoppable and free, cyberpunk neon city background, cinematic photorealistic. "
            "No text, no words, no letters, no writing."
        ),
        "headline": "OPEN-SOURCE\nРВЕТ GPT-4",
        "subtext": "Llama, DeepSeek — бесплатны.\nСтавятся на твой сервер.\nНикто не может забрать.",
        "watermark": "@lamanopro_  x  @aiconicvibe",
    },
    {
        "name": "6_VORONKA",
        "caption": "6️⃣ ВОРОНКА — ОТКРЫТЫЙ",
        "bg_prompt": (
            "A dark VIP mafia room, mysterious figure slides a glowing briefcase across a poker table, "
            "briefcase open with intense blue neon glow inside, cinematic moody photorealistic. "
            "No text, no words, no letters, no writing."
        ),
        "headline": "ПИШИ СЛОВО:\nОТКРЫТЫЙ",
        "subtext": "Хочешь свою независимую нейросеть?\nПиши мне ОТКРЫТЫЙ.",
        "watermark": "@lamanopro_  x  @aiconicvibe",
    },
]


def generate_bg(prompt):
    """Генерация фона через Vertex AI Imagen 3.0."""
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    data = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1, "aspectRatio": "1:1"},
    }
    for loc in LOCATIONS:
        url = (
            f"https://{loc}-aiplatform.googleapis.com/v1/projects/{project_id}"
            f"/locations/{loc}/publishers/google/models/imagen-3.0-generate-001:predict"
        )
        try:
            res = requests.post(url, headers=headers, json=data, timeout=120)
            if res.status_code == 200:
                rj = res.json()
                if "predictions" in rj and rj["predictions"]:
                    return base64.b64decode(rj["predictions"][0]["bytesBase64Encoded"])
            else:
                print(f"    ⚠️ {loc} → {res.status_code}")
        except Exception as e:
            print(f"    ❌ {loc} → {e}")
    return None


def draw_text_block(draw, text, y, font, canvas_w=CANVAS, fill="white"):
    """Рисует текст по центру холста."""
    for line in text.split("\n"):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (canvas_w - tw) // 2
        # Тень для читаемости
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                draw.text((x + dx, y + dy), line, font=font, fill="black")
        draw.text((x, y), line, font=font, fill=fill)
        y += bbox[3] - bbox[1] + 8
    return y


def compose_slide(bg_bytes, slide):
    """Накладывает текст на фон Pillow-ом."""
    img = Image.open(BytesIO(bg_bytes)).convert("RGB")
    img = img.resize((CANVAS, CANVAS), Image.LANCZOS)

    # Полупрозрачный оверлей сверху и снизу для читаемости
    overlay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    # Верхний градиент
    for i in range(CANVAS // 2):
        alpha = int(160 * (1 - i / (CANVAS // 2)))
        draw_ov.rectangle([(0, i), (CANVAS, i + 1)], fill=(0, 0, 0, alpha))
    # Нижний градиент
    for i in range(CANVAS // 3):
        alpha = int(180 * (i / (CANVAS // 3)))
        draw_ov.rectangle([(0, CANVAS - CANVAS // 3 + i), (CANVAS, CANVAS - CANVAS // 3 + i + 1)], fill=(0, 0, 0, alpha))

    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(img)

    # Шрифты
    try:
        font_headline = ImageFont.truetype(FONT_BOLD, 72)
        font_sub = ImageFont.truetype(FONT_BOLD, 30)
        font_watermark = ImageFont.truetype(FONT_BOLD, 22)
    except Exception:
        font_headline = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_watermark = ImageFont.load_default()

    # Заголовок — по центру
    y = 280
    y = draw_text_block(draw, slide["headline"], y, font_headline, fill="white")

    # Подзаголовок
    y += 30
    draw_text_block(draw, slide["subtext"], y, font_sub, fill=(220, 220, 220))

    # Водяной знак — внизу
    wm_bbox = draw.textbbox((0, 0), slide["watermark"], font=font_watermark)
    wm_w = wm_bbox[2] - wm_bbox[0]
    wm_x = (CANVAS - wm_w) // 2
    draw.text((wm_x, CANVAS - 60), slide["watermark"], font=font_watermark, fill=(180, 180, 180))

    # Сохраняем
    out = BytesIO()
    img.save(out, format="PNG", quality=95)
    return out.getvalue()


def send_tg(img_bytes, caption):
    """Отправка в Telegram."""
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto"
    files = {"photo": ("slide.png", img_bytes, "image/png")}
    data = {"chat_id": TG_CHAT_ID, "caption": caption}
    try:
        r = requests.post(url, files=files, data=data, timeout=30)
        return r.status_code == 200
    except Exception:
        return False


def main():
    print("=" * 60)
    print("🎨 КАРУСЕЛЬ «CLAUDE ЗАБАНИЛИ» — Imagen + Pillow текст")
    print("=" * 60)

    for i, slide in enumerate(SLIDES, 1):
        print(f"\n🖼  Слайд {i}/6: {slide['caption']}")

        # Генерируем фон
        bg = generate_bg(slide["bg_prompt"])
        if not bg:
            print(f"    💥 Фон не сгенерирован!")
            continue

        print(f"    ✅ Фон сгенерирован ({len(bg)//1024} КБ)")

        # Накладываем текст
        final = compose_slide(bg, slide)

        # Сохраняем локально
        fname = f"carousel_v2_{i}.png"
        with open(fname, "wb") as f:
            f.write(final)
        print(f"    ✅ Сохранён: {fname} ({len(final)//1024} КБ)")

        # Отправляем в Telegram
        if send_tg(final, slide["caption"]):
            print(f"    📤 Отправлено в Telegram")
        else:
            print(f"    ❌ Ошибка Telegram")

        if i < len(SLIDES):
            print("    ⏳ Пауза 3 сек...")
            time.sleep(3)

    print(f"\n{'='*60}")
    print("🎉 Готово!")

    # Финальное сообщение
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TG_CHAT_ID,
        "text": "🎯 <b>Карусель готова!</b>\n\n6 слайдов • 1080×1080 • Imagen 3.0 + Pillow\nКириллица читается идеально!",
        "parse_mode": "HTML",
    })


if __name__ == "__main__":
    main()