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
    mp3_path = out_dir / "n8n_http_cannot_be_llm.mp3"
    ogg_path = out_dir / "n8n_http_cannot_be_llm.ogg"

    text = """
Лара, отвечаю прямо: обычный HTTP Request node нельзя подключить к AI Agent как LLM.

AI Agent принимает только специальные LangChain model sub-nodes: OpenAI Chat Model, Anthropic, Gemini, Groq, Ollama и похожие. HTTP Request может быть только tool, то есть инструментом, который агент вызывает уже после того, как у агента есть рабочая LLM.

Поэтому если GRSai не проходит через OpenAI Chat Model, он не станет мозгом агента через обычный HTTP Request.

Рабочие обходы такие. Первый: мозг агента делаем через AIHubMix или OpenRouter, а GRSai подключаем как HTTP Request Tool для конкретных задач: картинки, видео, Nano Banana, Veo.

Второй: не использовать AI Agent node, а собрать мини-агента обычными нодами: Webhook, Code для prompt, HTTP Request к GRSai, Code для парсинга ответа, Telegram reply. Это будет рабочий чат-бот, но без LangChain tools-memory интерфейса.

По GRSai плюс n8n я не нашёл нормального кейса, где его успешно подключили именно как OpenAI Chat Model в AI Agent. Зато нашёл похожие кейсы: OpenAI Chat Model node может падать, потому что он вызывает slash models или ждёт строгий OpenAI-compatible формат. HTTP Request при этом может работать, потому что вызывает только нужный endpoint.

Вывод: GRSai сначала надо проверить простым HTTP Request node. Если он работает — используем как обычный API или tool. Если нужен именно мозг AI Agent — лучше AIHubMix или OpenRouter.
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
        "[VS Code Cline]\n[Agent: N8N]\n🎙️ Почему HTTP Request не может быть LLM для AI Agent",
    )
    print(f"Sent Voice: status={status} ok={ok}")


if __name__ == "__main__":
    asyncio.run(main())