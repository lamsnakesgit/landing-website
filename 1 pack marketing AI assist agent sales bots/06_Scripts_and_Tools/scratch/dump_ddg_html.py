import asyncio
from playwright.async_api import async_playwright

async def dump_ddg():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        url = "https://lite.duckduckgo.com/lite/?q=site:threads.net+разработка"
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(3000)
        
        html = await page.content()
        dump_path = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/ddg_dump.html"
        with open(dump_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"DDG HTML dumped to {dump_path}")
        print(f"Title: {await page.title()}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(dump_ddg())
