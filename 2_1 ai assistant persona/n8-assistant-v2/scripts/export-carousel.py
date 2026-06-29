#!/usr/bin/env python3
"""Export carousel slides to PNG using Playwright (Python)."""
import asyncio
import os
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).parent.parent.resolve()
HTML_FILE = ROOT / "public/carousels/hormozi-enhance-offer-carousel.html"
OUT_DIR = ROOT / "public/carousels/export/hormozi-enhance"
TOTAL_SLIDES = 8
WIDTH = 1080
HEIGHT = 1350


async def export_slides():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=2,
        )
        page = await context.new_page()

        file_url = "file://" + str(HTML_FILE)
        print(f"Opening: {file_url}")

        await page.goto(file_url, wait_until="networkidle")
        # Ждём загрузку шрифтов и рендер
        await page.wait_for_timeout(15000)

        for i in range(1, TOTAL_SLIDES + 1):
            hash_fragment = f"#slide-{i}"
            await page.goto(file_url + hash_fragment, wait_until="networkidle")
            await page.wait_for_timeout(800)

            out_path = OUT_DIR / f"slide-{i:02d}.png"
            await page.screenshot(
                path=str(out_path),
                clip={"x": 0, "y": 0, "width": WIDTH, "height": HEIGHT},
            )
            print(f"✓ Saved {out_path}")

        await browser.close()
        print(f"\nDone! All {TOTAL_SLIDES} slides exported to {OUT_DIR}")


if __name__ == "__main__":
    asyncio.run(export_slides())