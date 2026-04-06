import re
import textwrap
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = BASE_DIR / "outputs" / "story_png_exports"
STORY_SIZE = (1080, 1920)
STAGE_PALETTES = {
    "Hook": ((94, 45, 160), (236, 72, 153)),
    "Context": ((13, 71, 161), (38, 198, 218)),
    "Value": ((18, 18, 18), (29, 78, 216)),
    "CTA": ((17, 94, 89), (16, 185, 129)),
}
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]


def _slugify(value):
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "story_set"


def _font(size):
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def _create_gradient_background(size, color_top, color_bottom):
    width, height = size
    image = Image.new("RGB", size, color_top)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        blend = y / max(height - 1, 1)
        row_color = tuple(
            int(color_top[index] * (1 - blend) + color_bottom[index] * blend)
            for index in range(3)
        )
        draw.line((0, y, width, y), fill=row_color)
    return image


def _cover_image(image, size):
    width, height = size
    scale = max(width / image.width, height / image.height)
    resized = image.resize(
        (int(image.width * scale), int(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = max((resized.width - width) // 2, 0)
    top = max((resized.height - height) // 2, 0)
    return resized.crop((left, top, left + width, top + height))


def _load_background(slide):
    stage = slide.get("stage", "Value")
    palette = STAGE_PALETTES.get(stage, STAGE_PALETTES["Value"])
    source_image_path = slide.get("source_image_path")

    if source_image_path and Path(source_image_path).exists():
        try:
            image = Image.open(source_image_path).convert("RGB")
            covered = _cover_image(image, STORY_SIZE)
            return covered.filter(ImageFilter.GaussianBlur(radius=1.5))
        except Exception:
            pass

    return _create_gradient_background(STORY_SIZE, palette[0], palette[1])


def _wrap_text(draw, text, font, max_width):
    words = text.split()
    if not words:
        return [""]

    lines = []
    current_line = words[0]

    for word in words[1:]:
        test_line = f"{current_line} {word}"
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return lines


def _fit_text(draw, text, max_width, max_height, start_size=110, min_size=42):
    safe_text = (text or "Новый слайд").strip()

    for font_size in range(start_size, min_size - 1, -4):
        font = _font(font_size)
        lines = _wrap_text(draw, safe_text, font, max_width)
        line_height = draw.textbbox((0, 0), "Аг", font=font)[3]
        spacing = max(12, font_size // 5)
        total_height = len(lines) * line_height + max(0, len(lines) - 1) * spacing
        widest_line = max(
            draw.textbbox((0, 0), line, font=font)[2] for line in lines
        )

        if total_height <= max_height and widest_line <= max_width:
            return font, lines, spacing, line_height

    font = _font(min_size)
    wrapped = textwrap.wrap(safe_text, width=18) or [safe_text]
    line_height = draw.textbbox((0, 0), "Аг", font=font)[3]
    spacing = max(10, min_size // 5)
    return font, wrapped, spacing, line_height


def _shorten(value, max_chars=180):
    clean = (value or "").strip()
    if len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 1].rstrip() + "…"


def render_story_slide(slide, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    background = _load_background(slide).convert("RGBA")
    overlay = Image.new("RGBA", STORY_SIZE, (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    width, height = STORY_SIZE

    draw_overlay.rectangle((0, 0, width, height), fill=(0, 0, 0, 92))
    draw_overlay.rounded_rectangle(
        (48, 56, width - 48, height - 56),
        radius=44,
        outline=(255, 255, 255, 64),
        width=3,
    )
    draw_overlay.rounded_rectangle(
        (56, height - 720, width - 56, height - 90),
        radius=36,
        fill=(5, 10, 20, 165),
    )

    image = Image.alpha_composite(background, overlay)
    draw = ImageDraw.Draw(image)

    stage = slide.get("stage", "Value")
    slide_type = slide.get("type", "photo").upper()
    stage_font = _font(42)
    badge_font = _font(34)
    meta_font = _font(28)
    prompt_font = _font(26)

    draw.rounded_rectangle((72, 92, 290, 162), radius=26, fill=(255, 255, 255, 42))
    draw.text((102, 108), stage, font=stage_font, fill=(255, 255, 255))

    draw.rounded_rectangle((width - 238, 92, width - 72, 162), radius=26, fill=(255, 255, 255, 30))
    draw.text((width - 200, 110), slide_type, font=badge_font, fill=(255, 255, 255))

    script_text = slide.get("script_text") or "Новый сторис-слайд"
    font, lines, spacing, line_height = _fit_text(
        draw,
        script_text,
        max_width=width - 180,
        max_height=620,
    )
    total_text_height = len(lines) * line_height + max(0, len(lines) - 1) * spacing
    start_y = max(280, height - 640 + (530 - total_text_height) // 2)

    for index, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x = (width - line_width) // 2
        y = start_y + index * (line_height + spacing)
        draw.text((x, y), line, font=font, fill=(255, 255, 255))

    meta_y = height - 320
    draw.text(
        (88, meta_y),
        f"Слайд {slide.get('slide_number', 1)} · {stage}",
        font=meta_font,
        fill=(214, 224, 255),
    )

    prompt_text = _shorten(slide.get("visual_prompt") or "")
    if prompt_text:
        prompt_lines = textwrap.wrap(f"Визуал: {prompt_text}", width=48)[:4]
        current_y = meta_y + 58
        for prompt_line in prompt_lines:
            draw.text((88, current_y), prompt_line, font=prompt_font, fill=(210, 220, 236))
            current_y += 38

    instructions = _shorten(slide.get("layout_instructions") or slide.get("audio_suggestion") or "")
    if instructions:
        draw.text(
            (88, height - 146),
            instructions,
            font=prompt_font,
            fill=(170, 183, 204),
        )

    image.convert("RGB").save(output_path, format="PNG", optimize=True)
    return str(output_path)


def export_story_pngs(plan, project_name="story_factory", output_root=None):
    output_root = Path(output_root or DEFAULT_OUTPUT_ROOT)
    story_dir = output_root / f"{_slugify(project_name)[:40]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    story_dir.mkdir(parents=True, exist_ok=True)

    output_files = []
    for index, slide in enumerate(plan.get("stories", []), start=1):
        stage = _slugify(slide.get("stage", "slide"))
        slide_type = _slugify(slide.get("type", "photo"))
        file_path = story_dir / f"{index:02d}_{stage}_{slide_type}.png"
        output_files.append(render_story_slide(slide, file_path))

    zip_path = story_dir / "story_png_export.zip"
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
        for file_path in output_files:
            path_obj = Path(file_path)
            archive.write(path_obj, arcname=path_obj.name)

    return {
        "output_dir": str(story_dir),
        "files": output_files,
        "zip_path": str(zip_path),
    }
