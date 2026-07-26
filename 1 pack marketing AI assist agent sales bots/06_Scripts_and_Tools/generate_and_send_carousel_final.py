"""
Генерация 6 слайдов карусели "CLAUDE ЗАБАНИЛИ" через GRSAI (nano-banana-2)
и отправка в Telegram.
"""
import os
import requests
import time
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ─── Конфигурация ────────────────────────────────────────────────
GRSAI_KEY = os.getenv("GRSAI_API_KEY")
TG_BOT_TOKEN = os.getenv("ANTIGRAVITY_BOT_TOKEN")
TG_CHAT_ID = "888005446"
MODEL_PRIMARY = "nano-banana-2"
MODEL_FALLBACK = "nano-banana-pro"
ENDPOINTS = [
    "https://api.grsai.com/v1/images/generations",
    "https://grsai.dakka.com.cn/v1/images/generations",
]

# ─── Промпты (точные от пользователя) ────────────────────────────
PROMPTS = [
    # Слайд 1 — Хук
    'Vertical 3:4 aspect ratio. Hyper-viral Instagram feed cover, highly clickable and catchy. A cinematic close-up mugshot of a sleek humanoid robot in an orange prison uniform, looking directly at the viewer with glowing red eyes. The robot holds a large sign with big bold viral typography text "CLAUDE ЗАБАНИЛИ. КТО ДАЛЬШЕ?" and smaller readable typography text below it: "Сначала они молча забанили тысячи аккаунтов Claude Fabl5. Без объяснения причин. Ты думаешь, это просто сбой? Нет, это предупреждение. Кто следующий?". Cyberpunk neon prison lighting, gangster movie aesthetic, dramatic shadows. At the very bottom center, small clear typography text "@lamanopro_ x @aiconicvibe ✔️".',

    # Слайд 2 — Эскалация
    'Vertical 3:4 aspect ratio. A futuristic prison cell door slamming shut. A stylish AI mobster sitting inside behind glowing red laser bars. Big bold neon typography graffiti glowing on the wall reads: "ШАГ ВЛЕВО — ПЕРМАБАН" and smaller clear text below it reads: "Цензура ИИ дошла до полного абсурда. Модели отказываются писать код и тексты из-за выдуманных нарушений. Шаг влево — и ты ловишь пермабан без возврата денег. Твой бизнес может встать в любую секунду.". Gritty, cinematic gangster style, dark moody atmosphere. At the very bottom center, small clear typography text "@lamanopro_ x @aiconicvibe ✔️".',

    # Слайд 3 — Осознание
    'Vertical 3:4 aspect ratio. A ruthless mafia boss in a dark expensive suit burning a 20 dollar bill with a neon lighter. Digital glowing chains breaking around him. Big bold typography text overlay reads: "ЭТОТ ИИ НЕ ТВОЙ" and a readable typography text block below: "Ты платишь по $20 каждый месяц. Ты встраиваешь их API в свои процессы. Но этот ИИ тебе НЕ принадлежит. Тебя могут просто отключить, стерев всю твою работу и промпты нажатием одной кнопки.". Dark moody lighting, cinematic gangster aesthetic. At the very bottom center, small clear typography text "@lamanopro_ x @aiconicvibe ✔️".',

    # Слайд 4 — Решение
    'Vertical 3:4 aspect ratio. A hacker in a sharp mafia suit forcefully cracking a massive glowing digital vault. Inside the vault, a bright blue neon light representing absolute freedom. Big bold typography text overlay reads: "СВОЯ ЛИЧНАЯ НЕЙРОСЕТЬ" and a smaller text block: "Выход только один. Поднять свою ЛИЧНУЮ, абсолютно независимую нейросеть. Никакой цензуры, никаких правил, никаких внезапных блокировок. Твой ИИ подчиняется только тебе.". Cyberpunk, high contrast, symbol of rebellion. At the very bottom center, small clear typography text "@lamanopro_ x @aiconicvibe ✔️".',

    # Слайд 5 — Ценность
    'Vertical 3:4 aspect ratio. A lineup of powerful, sleek cyber-mobsters standing outside the prison in the rainy streets. They look unstoppable, heavily armed and free. Big bold typography text overlay reads: "OPEN-SOURCE РВЕТ GPT-4" and a clear text paragraph reads: "Открытые модели (Llama, DeepSeek) уже нагоняют, а местами и обходят GPT-4. Главное — они бесплатны. Они ставятся на твой личный сервер. Никто не может их забрать или ограничить.". Cyberpunk neon city background, cinematic. At the very bottom center, small clear typography text "@lamanopro_ x @aiconicvibe ✔️".',

    # Слайд 6 — Воронка (CTA)
    'Vertical 3:4 aspect ratio. A dark VIP mafia room. A mysterious figure slides a glowing briefcase across a poker table. The briefcase is open, glowing intensely blue from the inside. Big bold neon typography text in the background reads: "ПИШИ СЛОВО: ОТКРЫТЫЙ" and a smaller readable text block says: "Хочешь развернуть свой независимый, нецензурируемый ИИ? Пиши мне в Директ кодовое слово ОТКРЫТЫЙ. Я скину секретную подборку топовых моделей и пошаговую инструкцию по их установке.". Cinematic, highly detailed, moody. At the very bottom center, small clear typography text "@lamanopro_ x @aiconicvibe ✔️".',
]


def generate_slide(slide_num: int, prompt: str, model: str) -> Optional[str]:
    """Генерация одного слайда. Возвращает путь к файлу или None."""
    headers = {
        "Authorization": f"Bearer {GRSAI_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": "768x1024",
    }
    output = f"carousel_final_{slide_num}.png"

    for url in ENDPOINTS:
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=120)
            if resp.status_code == 200:
                data = resp.json()
                img_url = data["data"][0]["url"]
                img_bytes = requests.get(img_url, timeout=60).content
                with open(output, "wb") as f:
                    f.write(img_bytes)
                print(f"  ✅ Слайд {slide_num} сохранён: {output} ({len(img_bytes)//1024} КБ)")
                return output
            else:
                print(f"  ⚠️ {url} → {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            print(f"  ❌ {url} → {e}")
    return None


def send_photo_to_tg(filepath: str, caption: str) -> bool:
    """Отправка фото в Telegram."""
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto"
    with open(filepath, "rb") as f:
        resp = requests.post(
            url,
            data={"chat_id": TG_CHAT_ID, "caption": caption, "parse_mode": "HTML"},
            files={"photo": f},
            timeout=30,
        )
    if resp.status_code == 200:
        print(f"  📤 Отправлено в Telegram: {filepath}")
        return True
    else:
        print(f"  ❌ Telegram ошибка {resp.status_code}: {resp.text[:200]}")
        return False


def main():
    print("=" * 60)
    print("🎨 ГЕНЕРАЦИЯ КАРУСЕЛИ: CLAUDE ЗАБАНИЛИ")
    print("=" * 60)

    captions = [
        "1️⃣ ХУК — CLAUDE ЗАБАНИЛИ. КТО ДАЛЬШЕ?",
        "2️⃣ ЭСКАЛАЦИЯ — ШАГ ВЛЕВО — ПЕРМАБАН",
        "3️⃣ ОСОЗНАНИЕ — ЭТОТ ИИ НЕ ТВОЙ",
        "4️⃣ РЕШЕНИЕ — СВОЯ ЛИЧНАЯ НЕЙРОСЕТЬ",
        "5️⃣ ЦЕННОСТЬ — OPEN-SOURCE РВЕТ GPT-4",
        "6️⃣ ВОРОНКА — ПИШИ СЛОВО: ОТКРЫТЫЙ",
    ]

    for i, prompt in enumerate(PROMPTS, 1):
        print(f"\n🖼  Слайд {i}/6: {captions[i-1]}")

        # Пробуем nano-banana-2, при неудаче — nano-banana-pro
        path = generate_slide(i, prompt, MODEL_PRIMARY)
        if not path:
            print(f"  🔄 Ретрай с {MODEL_FALLBACK}...")
            path = generate_slide(i, prompt, MODEL_FALLBACK)

        if path:
            send_photo_to_tg(path, captions[i-1])
        else:
            print(f"  💥 Слайд {i} не сгенерирован!")

        # Пауза между генерациями
        if i < len(PROMPTS):
            print("  ⏳ Пауза 3 сек...")
            time.sleep(3)

    # Финальное сообщение
    final_text = (
        "🎯 <b>Карусель готова!</b>\n\n"
        "6 слайдов по теме «Claude забанили — кто дальше?»\n"
        "Формат: 768×1024 (3:4)\n"
        "Модель: nano-banana-2\n\n"
        "⚡ Сохрани и выложи как карусель в Instagram!"
    )
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TG_CHAT_ID, "text": final_text, "parse_mode": "HTML"})
    print("\n🎉 Готово! Все слайды отправлены в Telegram.")


if __name__ == "__main__":
    main()