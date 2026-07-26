# scripts/download_broll.py

# Этот скрипт загружает короткие B‑roll‑клипы из YouTube по заранее заданным тематикам.
# Требуется установленный пакет yt‑dlp (через pip) и ffmpeg.
# Скрипт ориентирован на 30 fps (по умолчанию Remotion). При необходимости скорректируйте FPS.

import subprocess, os, sys

FPS = 30

segments = [
    {"id": 1, "query": "pricing table animation", "start": 0, "duration": 48},
    {"id": 2, "query": "AI generated image showcase", "start": 96, "duration": 48},
    {"id": 3, "query": "Qwen interface demo", "start": 192, "duration": 72},
    {"id": 4, "query": "cat chef animation", "start": 264, "duration": 96},
    {"id": 5, "query": "Hunyuan logo animation", "start": 360, "duration": 24},
    {"id": 6, "query": "cinematic AI visual effects", "start": 384, "duration": 96},
    {"id": 7, "query": "LLM model comparison graphic", "start": 528, "duration": 144},
    {"id": 8, "query": "LM Arena UI screenshot", "start": 672, "duration": 48},
    {"id": 9, "query": "superhero side‑by‑side comparison animation", "start": 720, "duration": 120},
]

out_dir = os.path.abspath("public/video")
os.makedirs(out_dir, exist_ok=True)

for s in segments:
    # Получаем URL первого найденного видео с помощью yt‑dlp через python‑модуль
    url_cmd = [sys.executable, "-m", "yt_dlp", f"ytsearch1:{s['query']}", "-f", "best[ext=mp4]/best", "--print", "url", "--skip-download"]
    url = subprocess.check_output(url_cmd, text=True).strip()

    start_sec = s["start"] / FPS
    dur_sec = s["duration"] / FPS
    out_file = os.path.join(out_dir, f"broll_{s['id']}.mp4")

    dl_cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        url,
        "-f",
        "best[ext=mp4]/best",
        "-o",
        out_file,
        "--postprocessor-args",
        f"-ss {start_sec} -t {dur_sec}",
    ]
    subprocess.run(dl_cmd, check=True)

print("B‑roll‑клипы загружены в", out_dir)
