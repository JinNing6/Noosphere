import asyncio
from playwright.async_api import async_playwright
import time

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 800x500 is the player container size in index.html
        context = await browser.new_context(
            viewport={'width': 800, 'height': 500},
            record_video_dir="recorded_videos/",
            record_video_size={'width': 800, 'height': 500}
        )
        page = await context.new_page()
        print("Opening localhost...")
        await page.goto("http://localhost:8081/")
        
        # Wait for asciinema player to finish rendering frame and playing
        # Wait exactly 15 seconds as determined by previous experiments
        print("Waiting 15 seconds for animation to play...")
        await page.wait_for_timeout(15000)
        
        print("Closing context...")
        await context.close()
        await browser.close()
        print("Finished.")

asyncio.run(main())
