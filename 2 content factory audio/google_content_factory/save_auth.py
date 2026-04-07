import asyncio
from playwright.async_api import async_playwright

async def save_auth():
    async with async_playwright() as p:
        # Launch browser with arguments to make it look more like a real browser
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream",
            ]
        )
        # Set a realistic user agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Execute script to further hide automation
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("Opening Google Login...")
        # Try logging in via YouTube or StackOverflow, sometimes it's easier
        await page.goto("https://accounts.google.com/ServiceLogin?hl=en&passive=true&continue=https://www.google.com/")
        
        print("\n!!! ACTION REQUIRED !!!")
        print("1. Log in to your Google account in the opened browser window.")
        print("2. Once you are logged in and see your account dashboard, come back here.")
        print("3. Press Enter in this terminal to save the session and close the browser.")
        
        input("\nPress Enter after you have logged in...")
        
        # Save storage state to a file
        await context.storage_state(path="google_auth.json")
        print("\nSuccess! Session saved to 'google_auth.json'.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(save_auth())
