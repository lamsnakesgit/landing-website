import asyncio
import mimetypes
import subprocess
import urllib.request
import uuid
from pathlib import Path

import edge_tts


def read_env(path=".env"):
    env = {}
    env_path = Path(path)
    if not env_path.exists():
        return env

    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        value = line.strip()
        if not value or value.startswith("#") or "=" not in value:
            continue

        key, raw_value = value.split("=", 1)
        env[key.strip()] = raw_value.strip().strip("\"'")

    return env


async def make_mp3(text, audio_path):
    communicate = edge_tts.Communicate(text=text, voice="ru-RU-DmitryNeural", rate="+5%")
    await communicate.save(str(audio_path))


def multipart_form(fields, files):
    boundary = "----ClineBoundary" + uuid.uuid4().hex
    body = bytearray()

    for name, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.extend(str(value).encode())
        body.extend(b"\r\n")

    for name, path_value in files.items():
        path = Path(path_value)
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"; filename="{path.name}"\r\n'.encode())
        body.extend(f"Content-Type: {mime}\r\n\r\n".encode())
        body.extend(path.read_bytes())
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode())
    return bytes(body), boundary


def send_voice(bot_token, chat_id, voice_path, caption):
    body, boundary = multipart_form({"chat_id": chat_id, "caption": caption}, {"voice": voice_path})
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{bot_token}/sendVoice",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=90) as response:
        result = response.read().decode("utf-8", "replace")
        return response.status, '"ok":true' in result


async def main():
    env = read_env()
    bot_token = env.get("TG_REALSTATE_SMM_BOT")
    chat_id = env.get("TG_CHAT_ID_MAIN") or env.get("TG_REALSTATE_SMM_CHAT_ID")

    if not bot_token or not chat_id:
        print("Missing Telegram env")
        return

    out_dir = Path("scratch/voice_notes")
    out_dir.mkdir(parents=True, exist_ok=True)
    mp3_path = out_dir / "n8n_grsai_correct_host_fix.mp3"
    ogg_path = out_dir / "n8n_grsai_correct_host_fix.ogg"

    text = """
Лара, уточнение по GRSai. Если не работает ни slash v1, ни slash chat completions, причина, похоже, не в n8n, а в host или model id.

По публичным материалам GRSai, international host указан как grsaiapi точка com. Не api точка grsai точка com. Поэтому в n8n OpenAI credential попробуй Base URL: https двоеточие slash slash grsaiapi точка com slash v1.

Для китайского прямого хоста в их материалах указан grsai точка dakka точка com точка cn. Тогда Base URL: https двоеточие slash slash grsai точка dakka точка com точка cn slash v1.

В n8n OpenAI node не ставь полный путь slash chat slash completions и не ставь singular completion. Base URL — только host плюс slash v1. Сам node добавит chat completions.

Отключи Use Responses API. И главное: модель gemini три точка один flash lite я не вижу в публичном списке GRSai. Там есть, например, gemini-3-pro, gpt-5.4, gpt-5.5. Если model id не существует, будет тот же resource not found, даже с правильным host.

Если после этого всё ещё resource not found, значит GRSai не отдаёт OpenAI chat completions совместимый endpoint для этой модели. Тогда в n8n надо не OpenAI Chat Model node, а HTTP Request node по их native API, либо использовать AIHubMix/OpenRouter для чата.

И важное: ключ засветился на скрине. После тестов лучше перевыпустить API key.
""".strip()

    await make_mp3(text, mp3_path)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp3_path),
            "-vn",
            "-c:a",
            "libopus",
            "-b:a",
            "32k",
            "-ar",
            "48000",
            str(ogg_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    status, ok = send_voice(
        bot_token,
        chat_id,
        ogg_path,
        "[VS Code Cline]\n[Agent: N8N]\n🎙️ GRSai в n8n: неверный host/model или нет chat-compatible endpoint",
    )
    print(f"Sent Voice: status={status} ok={ok}")


if __name__ == "__main__":
    asyncio.run(main())