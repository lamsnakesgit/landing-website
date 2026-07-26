import asyncio
import os
from playwright.async_api import async_playwright

async def take_screenshots():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Настройка контекста с реальным User-Agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        
        # 1. Скриншот Google
        try:
            print("Navigating to Google...")
            await page.goto("https://www.google.com/search?q=site:threads.net+разработка", wait_until="load", timeout=20000)
            await page.wait_for_timeout(3000)
            google_path = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/google_search.png"
            await page.screenshot(path=google_path)
            print(f"Google screenshot saved to {google_path}")
            print(f"Google title: {await page.title()}")
            print(f"Google URL: {page.url}")
        except Exception as e:
            print(f"Google screenshot failed: {e}")
            
        # 2. Скриншот Bing
        try:
            print("Navigating to Bing...")
            await page.goto("https://www.bing.com/search?q=site:threads.net+разработка", wait_until="load", timeout=20000)
            await page.wait_for_timeout(3000)
            bing_path = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/bing_search.png"
            await page.screenshot(path=bing_path)
            print(f"Bing screenshot saved to {bing_path}")
            print(f"Bing title: {await page.title()}")
            print(f"Bing URL: {page.url}")
        except Exception as e:
            print(f"Bing screenshot failed: {e}")
            
        # 3. Скриншот Adata.kz
        try:
            print("Navigating to pk.adata.kz...")
            await page.goto("https://pk.adata.kz/", wait_until="load", timeout=20000)
            await page.wait_for_timeout(3000)
            adata_path = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/adata.png"
            await page.screenshot(path=adata_path)
            print(f"Adata screenshot saved to {adata_path}")
            print(f"Adata title: {await page.title()}")
            print(f"Adata URL: {page.url}")
        except Exception as e:
            print(f"Adata screenshot failed: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(take_screenshots())
