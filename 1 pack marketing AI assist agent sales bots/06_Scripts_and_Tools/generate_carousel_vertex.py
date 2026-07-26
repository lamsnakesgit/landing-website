"""
Генерация 6 слайдов карусели через Vertex AI Imagen 3.0 (service account)
и отправка в Telegram.
"""
import google.auth
from google.auth.transport.requests import Request
import requests
import base64
import os
import time

# ─── Vertex AI Service Account ───────────────────────────────────
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "vertex_sa.json"
)

credentials, project_id = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
credentials.refresh(Request())

# ─── Telegram ────────────────────────────────────────────────────
TG_BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN", "6240637727:AAGZsu3ZOAinWoAJwTP11eJJv2M4qzCtx_g")
TG_CHAT_ID = "888005446"

# ─── Регионы (пробуем по очереди) ────────────────────────────────
LOCATIONS = [
    "us-east4", "us-west1", "europe-west1",
    "europe-west4", "asia-southeast1", "us-central1",
]

# ─── Промпты (точные от пользователя) ────────────────────────────
PROMPTS = [
    {
        "name": "1_HUK",
        "caption": "1️⃣ ХУК — CLAUDE ЗАБАНИЛИ. КТО ДАЛЬШЕ?",
        "prompt": (
            'Vertical 3:4 aspect ratio. Hyper-viral Instagram feed cover, highly clickable and catchy. '
            'A cinematic close-up mugshot of a sleek humanoid robot in an orange prison uniform, looking '
            'directly at the viewer with glowing red eyes. The robot holds a large sign with big bold viral '
            'typography text "CLAUDE ЗАБАНИЛИ. КТО ДАЛЬШЕ?" and smaller readable typography text below it: '
            '"Сначала они молча забанили тысячи аккаунтов Claude Fabl5. Без объяснения причин. Ты думаешь, '
            'это просто сбой? Нет, это предупреждение. Кто следующий?". Cyberpunk neon prison lighting, '
            'gangster movie aesthetic, dramatic shadows. At the very bottom center, small clear typography '
            'text "@lamanopro_ x @aiconicvibe ✔️".'
        ),
    },
    {
        "name": "2_ESKALACIYA",
        "caption": "2️⃣ ЭСКАЛАЦИЯ — ШАГ ВЛЕВО — ПЕРМАБАН",
        "prompt": (
            'Vertical 3:4 aspect ratio. A futuristic prison cell door slamming shut. A stylish AI mobster '
            'sitting inside behind glowing red laser bars. Big bold neon typography graffiti glowing on the '
            'wall reads: "ШАГ ВЛЕВО — ПЕРМАБАН" and smaller clear text below it reads: "Цензура ИИ дошла '
            'до полного абсурда. Модели отказываются писать код и тексты из-за выдуманных нарушений. '
            'Шаг влево — и ты ловишь пермабан без возврата денег. Твой бизнес может встать в любую секунду.". '
            'Gritty, cinematic gangster style, dark moody atmosphere. At the very bottom center, small clear '
            'typography text "@lamanopro_ x @aiconicvibe ✔️".'
        ),
    },
    {
        "name": "3_OSOZNANIE",
        "caption": "3️⃣ ОСОЗНАНИЕ — ЭТОТ ИИ НЕ ТВОЙ",
        "prompt": (
            'Vertical 3:4 aspect ratio. A ruthless mafia boss in a dark expensive suit burning a 20 dollar '
            'bill with a neon lighter. Digital glowing chains breaking around him. Big bold typography text '
            'overlay reads: "ЭТОТ ИИ НЕ ТВОЙ" and a readable typography text block below: "Ты платишь по '
            '$20 каждый месяц. Ты встраиваешь их API в свои процессы. Но этот ИИ тебе НЕ принадлежит. '
            'Тебя могут просто отключить, стерев всю твою работу и промпты нажатием одной кнопки.". '
            'Dark moody lighting, cinematic gangster aesthetic. At the very bottom center, small clear '
            'typography text "@lamanopro_ x @aiconicvibe ✔️".'
        ),
    },
    {
        "name": "4_RESHENIE",
        "caption": "4️⃣ РЕШЕНИЕ — СВОЯ ЛИЧНАЯ НЕЙРОСЕТЬ",
        "prompt": (
            'Vertical 3:4 aspect ratio. A hacker in a sharp mafia suit forcefully cracking a massive glowing '
            'digital vault. Inside the vault, a bright blue neon light representing absolute freedom. Big bold '
            'typography text overlay reads: "СВОЯ ЛИЧНАЯ НЕЙРОСЕТЬ" and a smaller text block: "Выход только '
            'один. Поднять свою ЛИЧНУЮ, абсолютно независимую нейросеть. Никакой цензуры, никаких правил, '
            'никаких внезапных блокировок. Твой ИИ подчиняется только тебе.". Cyberpunk, high contrast, '
            'symbol of rebellion. At the very bottom center, small clear typography text '
            '"@lamanopro_ x @aiconicvibe ✔️".'
        ),
    },
    {
        "name": "5_CENNOST",
        "caption": "5️⃣ ЦЕННОСТЬ — OPEN-SOURCE РВЕТ GPT-4",
        "prompt": (
            'Vertical 3:4 aspect ratio. A lineup of powerful, sleek cyber-mobsters standing outside the '
            'prison in the rainy streets. They look unstoppable, heavily armed and free. Big bold typography '
            'text overlay reads: "OPEN-SOURCE РВЕТ GPT-4" and a clear text paragraph reads: "Открытые '
            'модели (Llama, DeepSeek) уже нагоняют, а местами и обходят GPT-4. Главное — они бесплатны. '
            'Они ставятся на твой личный сервер. Никто не может их забрать или ограничить.". Cyberpunk '
            'neon city background, cinematic. At the very bottom center, small clear typography text '
            '"@lamanopro_ x @aiconicvibe ✔️".'
        ),
    },
    {
        "name": "6_VORONKA",
        "caption": "6️⃣ ВОРОНКА — ПИШИ СЛОВО: ОТКРЫТЫЙ",
        "prompt": (
            'Vertical 3:4 aspect ratio. A dark VIP mafia room. A mysterious figure slides a glowing briefcase '
            'across a poker table. The briefcase is open, glowing intensely blue from the inside. Big bold neon '
            'typography text in the background reads: "ПИШИ СЛОВО: ОТКРЫТЫЙ" and a smaller readable text block '
            'says: "Хочешь развернуть свой независимый, нецензурируемый ИИ? Пиши мне в Директ кодовое слово '
            'ОТКРЫТЫЙ. Я скину секретную подборку топовых моделей и пошаговую инструкцию по их установке.". '
            'Cinematic, highly detailed, moody. At the very bottom center, small clear typography text '
            '"@lamanopro_ x @aiconicvibe ✔️".'
        ),
    },
]


def generate_with_vertex(prompt_text: str):
    """Генерация изображения через Vertex AI Imagen 3.0. Возвращает bytes или None."""
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    data = {
        "instances": [{"prompt": prompt_text}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "3:4",
        },
    }

    for loc in LOCATIONS:
        url = (
            f"https://{loc}-aiplatform.googleapis.com/v1/projects/{project_id}"
            f"/locations/{loc}/publishers/google/models/imagen-3.0-generate-001:predict"
        )
        try:
            res = requests.post(url, headers=headers, json=data, timeout=120)
            if res.status_code == 200:
                res_json = res.json()
                if "predictions" in res_json and len(res_json["predictions"]) > 0:
                    b64 = res_json["predictions"][0]["bytesBase64Encoded"]
                    return base64.b64decode(b64)
            else:
                print(f"    ⚠️ {loc} → {res.status_code}: {res.text[:120]}")
        except Exception as e:
            print(f"    ❌ {loc} → {e}")

    return None


def send_to_tg(image_bytes: bytes, caption: str) -> bool:
    """Отправка фото в Telegram."""
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto"
    files = {"photo": ("slide.png", image_bytes, "image/png")}
    data = {"chat_id": TG_CHAT_ID, "caption": caption}
    try:
        r = requests.post(url, files=files, data=data, timeout=30)
        if r.status_code == 200:
            print(f"    📤 Отправлено в Telegram")
            return True
        else:
            print(f"    ❌ Telegram {r.status_code}: {r.text[:150]}")
    except Exception as e:
        print(f"    ❌ Telegram ошибка: {e}")
    return False


def main():
    print("=" * 60)
    print("🎨 КАРУСЕЛЬ «CLAUDE ЗАБАНИЛИ» — Vertex AI Imagen 3.0")
    print("=" * 60)
    print(f"Проект: {project_id}")
    print(f"Регионы: {', '.join(LOCATIONS[:3])}...\n")

    success_count = 0

    for i, slide in enumerate(PROMPTS, 1):
        print(f"🖼  Слайд {i}/6: {slide['caption']}")

        img_bytes = generate_with_vertex(slide["prompt"])

        if img_bytes:
            # Сохраняем локально
            filename = f"vertex_slide_{i}.png"
            with open(filename, "wb") as f:
                f.write(img_bytes)
            print(f"    ✅ Сохранён: {filename} ({len(img_bytes)//1024} КБ)")

            # Отправляем в Telegram
            send_to_tg(img_bytes, slide["caption"])
            success_count += 1
        else:
            print(f"    💥 Слайд {i} не сгенерирован ни в одном регионе!")

        # Пауза между запросами
        if i < len(PROMPTS):
            print("    ⏳ Пауза 3 сек...")
            time.sleep(3)

    # Финальное сообщение
    print(f"\n{'='*60}")
    print(f"🎉 Готово! Успешно: {success_count}/6 слайдов")

    if success_count > 0:
        final_text = (
            f"🎯 <b>Карусель готова!</b>\n\n"
            f"Успешно сгенерировано: {success_count}/6 слайдов\n"
            f"Формат: 3:4 (вертикальный)\n"
            f"Модель: Vertex AI Imagen 3.0\n\n"
            f"⚡ Сохрани и выложи как карусель в Instagram!"
        )
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TG_CHAT_ID, "text": final_text, "parse_mode": "HTML"})


if __name__ == "__main__":
    main()