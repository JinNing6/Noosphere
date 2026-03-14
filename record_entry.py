"""Record the cinematic entry animation."""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            record_video_dir="recorded_videos",
            record_video_size={"width": 1200, "height": 500},
            viewport={"width": 1200, "height": 500},
        )
        page = await context.new_page()
        print("📹 Recording cinematic entry...")
        await page.goto("http://localhost:8081/cinematic_entry.html", wait_until="domcontentloaded")
        await asyncio.sleep(18)  # Full animation cycle ~16s + buffer
        await context.close()
        video_path = await page.video.path()
        print(f"✅ Saved: {video_path}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
