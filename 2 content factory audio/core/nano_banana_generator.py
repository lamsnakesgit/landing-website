import os
import re
import mimetypes
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from dotenv import load_dotenv
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
NANO_BANANA_MODEL = os.environ.get("NANO_BANANA_MODEL", "models/nano-banana-pro-preview")
DEFAULT_OUTPUT_ROOT = BASE_DIR / "outputs" / "nano_banana_story_exports"

# Initialize the Google GenAI Client
# Nano Banana Pro often requires v1beta
client = None
if GOOGLE_API_KEY:
    client = genai.Client(
        api_key=GOOGLE_API_KEY,
        http_options={'api_version': 'v1beta'}
    )


def _slugify(value):
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "_", str(value).strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "story_set"


def build_nano_banana_prompt(slide, story_context=None):
    story_context = story_context or {}
    script_text = (slide.get("script_text") or "").strip()
    visual_prompt = (slide.get("visual_prompt") or "").strip()
    layout_instructions = (slide.get("layout_instructions") or "").strip()
    audio_suggestion = (slide.get("audio_suggestion") or "").strip()
    stage = slide.get("stage", "Value")
    slide_type = slide.get("type", "photo")
    goal = (story_context.get("goal") or "").strip()
    strategy = (story_context.get("strategy") or "").strip()
    audience = (story_context.get("audience") or "").strip()
    style = (story_context.get("style") or "").strip()

    return (
        "Create one premium Instagram Story slide in vertical 9:16 format. "
        "This must look like a realistic, candid social media story, not a plastic AI poster.\n\n"
        f"Goal of the story set: {goal or 'Not specified'}\n"
        f"Overall Strategy: {strategy or 'Not specified'}\n"
        f"Target audience: {audience or 'Not specified'}\n"
        f"Stage in the funnel: {stage}\n"
        f"Original slide type: {slide_type}\n"
        f"Overall visual style: {style or 'Candid iPhone photography, natural lighting, authentic lifestyle'}\n\n"
        "Use the following on-screen text EXACTLY as written. Preserve language, wording, spelling, and punctuation. "
        "Do not invent extra text, captions, logos, or watermarks. Make the text look like native Instagram/TikTok text overlays.\n"
        f"ON-SCREEN TEXT: {script_text or 'Новый слайд'}\n\n"
        f"Visual concept: {visual_prompt or 'Candid moment, shot on iPhone, natural messy background'}\n"
        f"Layout instructions: {layout_instructions or 'Native social media feel, readable text, authentic composition'}\n"
        f"Audio / mood reference: {audio_suggestion or 'Confident, premium, modern'}\n\n"
        "CRITICAL: Avoid 'plastic' AI looks. Use keywords: shot on iPhone 15 Pro, film grain, natural lighting, candid, authentic, slightly messy background. "
        "If an input photo is attached, use it as the base image, keep the person/product recognizable, "
        "and integrate the text naturally into the image. If the slide was marked as video, convert the idea into a single strong cinematic still frame. "
        "Return only the final finished story image."
    )


def _build_request_parts(slide, prompt):
    parts = []
    source_image_path = slide.get("source_image_path")
    if source_image_path and Path(source_image_path).exists():
        image_path = Path(source_image_path)
        mime_type = mimetypes.guess_type(image_path.name)[0] or "image/jpeg"
        image_bytes = image_path.read_bytes()
        parts.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
        )

    parts.append(types.Part.from_text(text=prompt))
    return parts


def _call_nano_banana(parts):
    if not client:
        raise RuntimeError("GOOGLE_API_KEY не найден или клиент не инициализирован.")

    try:
        response = client.models.generate_content(
            model=NANO_BANANA_MODEL,
            contents=parts,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )
        return response
    except Exception as error:
        raise RuntimeError(f"Nano Banana Pro Error: {error}") from error


def _extract_image_payload(response):
    if not response.candidates:
        raise RuntimeError("Nano Banana Pro вернул пустой ответ (нет кандидатов).")

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            return part.inline_data

    raise RuntimeError("В ответе Nano Banana Pro нет изображения.")


def generate_story_image(slide, output_path, story_context=None):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    prompt = build_nano_banana_prompt(slide, story_context)
    request_parts = _build_request_parts(slide, prompt)
    response = _call_nano_banana(request_parts)
    image_data = _extract_image_payload(response)

    mime_type = image_data.mime_type or "image/jpeg"
    extension = ".png" if "png" in mime_type else ".jpg"
    if output_path.suffix.lower() != extension:
        output_path = output_path.with_suffix(extension)

    output_path.write_bytes(image_data.data)
    
    return {
        "file_path": str(output_path),
        "prompt": prompt,
        "mime_type": mime_type,
        "response_text": response.text if hasattr(response, 'text') else "",
    }


def export_nano_banana_story_set(plan, project_name="story_factory", story_context=None, output_root=None, progress_callback=None):
    import json
    output_root = Path(output_root or DEFAULT_OUTPUT_ROOT)
    output_dir = output_root / f"{_slugify(project_name)[:40]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir.mkdir(parents=True, exist_ok=True)

    stories = plan.get("stories", [])
    total = len(stories)
    files = []
    prompts = []
    
    for index, slide in enumerate(stories, start=1):
        file_stub = output_dir / f"{index:02d}_{_slugify(slide.get('stage', 'slide'))}_{_slugify(slide.get('type', 'photo'))}"
        try:
            result = generate_story_image(slide, file_stub, story_context=story_context)
            files.append(result["file_path"])
            
            if progress_callback:
                progress_callback(index, total, slide.get("stage", "slide"), file_path=result["file_path"])
            prompts.append(
                {
                    "slide_number": slide.get("slide_number", index),
                    "stage": slide.get("stage", "Value"),
                    "script_text": slide.get("script_text", ""),
                    "prompt": result["prompt"],
                }
            )
        except Exception as e:
            print(f"Error generating slide {index}: {e}")
            # Continue with other slides or handle as needed

    prompts_path = output_dir / "nano_banana_prompts.json"
    prompts_path.write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")

    zip_path = output_dir / "nano_banana_story_export.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
        for file_path in files:
            path_obj = Path(file_path)
            archive.write(path_obj, arcname=path_obj.name)
        archive.write(prompts_path, arcname=prompts_path.name)

    return {
        "generator": "nano_banana_pro",
        "output_dir": str(output_dir),
        "files": files,
        "zip_path": str(zip_path),
        "prompts_path": str(prompts_path),
        "prompts": prompts,
        "model": NANO_BANANA_MODEL,
    }
