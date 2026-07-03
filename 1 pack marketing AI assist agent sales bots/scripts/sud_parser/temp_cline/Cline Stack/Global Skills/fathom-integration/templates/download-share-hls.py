#!/usr/bin/env python3
"""Скачивает HLS playlist и ts-чанки из Fathom share_url, а при желании собирает mp4."""

from __future__ import annotations

import argparse
import html
import re
import subprocess
from pathlib import Path
from urllib.parse import urljoin


M3U8_PATTERN = re.compile(r"https://fathom\.video/share/[A-Za-z0-9_\-]+/video\.m3u8")


def run_command(command: list[str], capture: bool = True) -> str:
    """Запускает системную команду и возвращает stdout."""
    result = subprocess.run(
        command,
        check=True,
        text=True,
        capture_output=capture,
    )
    return result.stdout if capture else ""


def fetch_text(url: str) -> str:
    """Качает текстовый ресурс через curl, чтобы не упираться в локальные SSL-особенности Python."""
    return run_command(["curl", "-skS", url])


def extract_m3u8_url(share_url: str) -> str:
    """Достаёт ссылку на HLS playlist из HTML share page."""
    html_text = fetch_text(share_url)
    html_text = html.unescape(html_text)
    match = M3U8_PATTERN.search(html_text)
    if not match:
        raise RuntimeError("Не удалось найти video.m3u8 в share page")
    return match.group(0)


def download_file(url: str, output_path: Path) -> None:
    """Скачивает бинарный файл на диск."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    run_command(["curl", "-skS", "-L", url, "-o", str(output_path)], capture=False)


def parse_segment_urls(m3u8_text: str, m3u8_url: str) -> list[str]:
    """Собирает абсолютные URL всех HLS-сегментов из playlist."""
    segment_urls: list[str] = []
    for line in m3u8_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        segment_urls.append(urljoin(m3u8_url, line))
    return segment_urls


def build_mp4(m3u8_url: str, output_path: Path) -> None:
    """Собирает mp4 через ffmpeg без перекодирования."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    run_command(
        [
            "ffmpeg",
            "-y",
            "-protocol_whitelist",
            "file,http,https,tcp,tls,crypto",
            "-i",
            m3u8_url,
            "-c",
            "copy",
            "-bsf:a",
            "aac_adtstoasc",
            str(output_path),
        ],
        capture=False,
    )


def main() -> int:
    """Основной workflow: share_url -> m3u8 -> playlist -> chunks -> optional mp4."""
    parser = argparse.ArgumentParser()
    parser.add_argument("share_url", help="Публичная Fathom share_url")
    parser.add_argument("output_dir", help="Куда сохранить playlist/chunks/mp4")
    parser.add_argument(
        "--build-mp4",
        action="store_true",
        help="Дополнительно собрать единый mp4 через ffmpeg",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    m3u8_url = extract_m3u8_url(args.share_url)
    m3u8_text = fetch_text(m3u8_url)
    playlist_path = output_dir / "video.m3u8"
    playlist_path.write_text(m3u8_text, encoding="utf-8")

    segment_urls = parse_segment_urls(m3u8_text, m3u8_url)
    chunks_dir = output_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    for index, segment_url in enumerate(segment_urls, start=1):
        output_path = chunks_dir / f"segment_{index:05d}.ts"
        download_file(segment_url, output_path)

    print(f"m3u8_url={m3u8_url}")
    print(f"playlist={playlist_path}")
    print(f"segments_downloaded={len(segment_urls)}")
    print(f"chunks_dir={chunks_dir}")

    if args.build_mp4:
        mp4_path = output_dir / "output.mp4"
        build_mp4(m3u8_url, mp4_path)
        print(f"mp4={mp4_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
