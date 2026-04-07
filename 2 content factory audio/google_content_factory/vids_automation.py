import asyncio
import os
from playwright.async_api import async_playwright

async def create_google_vid(prompt, output_auth="google_auth.json"):
    if not os.path.exists(output_auth):
        print(f"Error: {output_auth} not found. Please run save_auth.py first.")
        return

    async with async_playwright() as p:
        # Launch browser (headless=False to see what's happening, can be True later)
        browser = await p.chromium.launch(headless=False)
        
        # Load the saved session
        context = await browser.new_context(storage_state=output_auth)
        page = await context.new_page()
        
        print(f"Navigating to Google Vids...")
        try:
            await page.goto("https://docs.google.com/videos/create", wait_until="networkidle", timeout=60000)
        except:
            print("Timeout waiting for networkidle, proceeding anyway...")
        
        # Debug: Save initial state
        await page.screenshot(path="vids_initial.png")
        print(f"Current URL: {page.url}")

        # Check if we are on a login page instead of Vids
        if "accounts.google.com" in page.url:
            print("!!! ERROR: Session expired or invalid. Please run save_auth.py again.")
            await browser.close()
            return

        # Wait for the "Help me create" textarea or input
        try:
            print("Step 1: Looking for prompt input...")
            # Try multiple common selectors for Google AI inputs
            selectors = [
                "textarea", 
                "div[role='textbox']", 
                "div[contenteditable='true']",
                "[aria-label*='Help me create']",
                ".docs-vids-prompt-input" # Hypothetical class
            ]
            
            input_element = None
            for selector in selectors:
                try:
                    input_element = await page.wait_for_selector(selector, timeout=5000)
                    if input_element:
                        print(f"Found input with selector: {selector}")
                        break
                except:
                    continue
            
            if not input_element:
                print("Could not find input field. Checking for 'Help me create' button first...")
                # Sometimes you have to click a button to open the AI prompt
                help_button = page.get_by_role("button", name=lambda x: "Help me create" in x or "Gemini" in x)
                if await help_button.is_visible():
                    await help_button.click()
                    await asyncio.sleep(2)
                    input_element = await page.wait_for_selector("textarea, div[role='textbox']", timeout=10000)

            if input_element:
                await input_element.click()
                await input_element.fill(prompt)
                await page.keyboard.press("Enter")
            else:
                raise Exception("Failed to find the prompt input field.")
            
            print("Generating video structure...")
            # Wait for the 'Create video' button to appear
            # This button appears after Gemini generates the outline/scenes
            create_button_selector = "button:has-text('Create video')"
            await page.wait_for_selector(create_button_selector, timeout=180000)
            await page.click(create_button_selector)
            
            print("Video project created! Waiting for assets to load...")
            # Wait for the editor to be fully loaded
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(15) # Extra buffer for UI elements
            
            print("Attempting to export the video...")
            # 1. Click on 'File' menu
            # Google Vids UI often uses a top menu bar. 
            # We'll try to find the File menu by text or common ID.
            file_menu = page.get_by_role("menuitem", name="File")
            if await file_menu.is_visible():
                await file_menu.click()
            else:
                # Fallback to searching for text if role fails
                await page.click("text='File'")
            
            await asyncio.sleep(2) # Wait for menu to open
            
            # 2. Hover over 'Download'
            download_menu = page.get_by_role("menuitem", name="Download")
            if await download_menu.is_visible():
                await download_menu.hover()
            else:
                await page.hover("text='Download'")
            
            # 3. Click 'MP4 video (.mp4)'
            # This usually triggers a 'Preparing download' or 'Rendering' dialog
            # We set a long timeout (e.g., 10 minutes) because rendering can take time
            async with page.expect_download(timeout=600000) as download_info:
                await page.click("text='MP4 video (.mp4)'")
                
                print("Waiting for video to render and download to start (this may take several minutes)...")
                # Google Vids might show a progress bar for rendering. 
                # Playwright's expect_download() will wait until the browser actually starts the download.
                # For long videos, we might need a very long timeout.
                download = await download_info.value
                
                # Wait for the download process to complete and save the file
                path = os.path.join(os.getcwd(), download.suggested_filename)
                await download.save_as(path)
                print(f"Video downloaded successfully to: {path}")

            print(f"Successfully completed automation for: {page.url}")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            # Take a screenshot for debugging
            await page.screenshot(path="vids_error.png")
            print("Screenshot saved to vids_error.png")
        
        # Keep browser open for a moment to see result
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    import sys
    test_prompt = "Create a 1-minute video about the benefits of AI automation for small businesses."
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        # Check if the argument is a path to a text file
        if os.path.exists(arg) and arg.endswith(".txt"):
            with open(arg, "r", encoding="utf-8") as f:
                test_prompt = f.read()
        else:
            test_prompt = " ".join(sys.argv[1:])
    
    asyncio.run(create_google_vid(test_prompt))
