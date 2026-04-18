import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.environ.get("GOOGLE_API_KEY")
DEFAULT_MODEL = "veo-3.1-lite-generate-preview"


def _ensure_client():
    if not API_KEY:
        raise RuntimeError("GOOGLE_API_KEY не найден. Добавьте ключ в .env")
    return genai.Client(api_key=API_KEY)


def _download_video(client, video_file, output_path: Path):
    if hasattr(video_file, "video") and hasattr(video_file.video, "data"):
        output_path.write_bytes(video_file.video.data)
        return

    if hasattr(video_file, "video") and hasattr(video_file.video, "uri"):
        uri = video_file.video.uri
        file_id = None
        if "/files/" in uri:
            file_id = uri.split("/files/")[1].split(":")[0]

        try:
            if file_id:
                try:
                    file_content = client.files.download(file_id)
                except Exception:
                    import urllib.request
                    req = urllib.request.Request(uri)
                    req.add_header("X-Goog-Api-Key", API_KEY)
                    with urllib.request.urlopen(req) as response:
                        file_content = response.read()
                output_path.write_bytes(file_content)
                return
        except Exception as error:
            raise RuntimeError(f"Failed to download video: {error}") from error

        import urllib.request
        req = urllib.request.Request(uri)
        req.add_header("X-Goog-Api-Key", API_KEY)
        with urllib.request.urlopen(req) as response:
            output_path.write_bytes(response.read())
        return

    raise RuntimeError("Unexpected video payload from Veo.")


def _generate_clip(client, prompt: str, output_path: Path, model: str = DEFAULT_MODEL):
    operation = client.models.generate_videos(
        model=model,
        prompt=prompt,
        config=types.GenerateVideosConfig(number_of_videos=1),
    )

    while not operation.done:
        time.sleep(10)
        operation = client.operations.get(operation)

    if operation.error:
        raise RuntimeError(f"Generation failed: {operation.error}")

    result = operation.result
    if not result or not result.generated_videos:
        raise RuntimeError("No generated videos returned.")

    _download_video(client, result.generated_videos[0], output_path)


def generate_batch(prompts_path: Path, output_dir: Path):
    client = _ensure_client()
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = json.loads(prompts_path.read_text(encoding="utf-8"))
    clips = payload.get("clips", [])
    model = payload.get("model", DEFAULT_MODEL)

    clips_txt_lines = []
    for clip in clips:
        clip_id = clip.get("clip_id")
        slug = clip.get("slug", f"clip_{clip_id}")
        prompt = clip.get("prompt")
        if not prompt:
            print(f"Skipping clip {clip_id}: empty prompt")
            continue

        filename = f"{clip_id:02d}_{slug}.mp4"
        output_path = output_dir / filename

        print(f"\nGenerating {filename}...")
        _generate_clip(client, prompt, output_path, model=model)
        print(f"Saved: {output_path}")
        clips_txt_lines.append(f"file '{filename}'")

    clips_txt_path = output_dir / "clips.txt"
    clips_txt_path.write_text("\n".join(clips_txt_lines), encoding="utf-8")
    print(f"\nGenerated clips list: {clips_txt_path}")


if __name__ == "__main__":
    prompts = BASE_DIR / "outputs" / "sen_sulu_batch_prompts.json"
    output_dir = BASE_DIR / "outputs" / "sen_sulu_clips"
    generate_batch(prompts, output_dir)