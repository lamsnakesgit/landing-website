import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re

async def test_threads_profile():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        post_url = "https://www.threads.net/t/Cum4jgnuQpF"
        print(f"Navigating to Threads post: {post_url}")
        
        try:
            await page.goto(post_url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(4000) # Даем JS отрендерить страницу
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Сохраним HTML для отладки
            with open("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/threads_post.html", "w") as f:
                f.write(html)
                
            # Ищем юзернеймы. В Threads ссылки на профиль имеют вид /@username
            users = set()
            for a in soup.find_all('a'):
                href = a.get('href', '')
                match = re.search(r'/@([a-zA-Z0-9_\.]+)', href)
                if match:
                    users.add(match.group(1))
                    
            print(f"Found usernames on page: {list(users)}")
            
            # Попробуем найти текст поста
            # Обычно текст лежит в div или span с определенными классами, поищем просто по тексту
            body_text = page.locator("body").inner_text()
            print("Snippet of body text:")
            print(await body_text)
            
        except Exception as e:
            print(f"Failed to load Threads page: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_threads_profile())
