"""
Record 4 individual terminal animation effects using Playwright.

Each animation is served via a local HTTP server and recorded as a WebM video.
"""
import asyncio
from playwright.async_api import async_playwright

ANIMATIONS = [
    {"name": "matrix_rain", "url": "http://localhost:8081/matrix_rain.html", "duration": 6, "width": 720, "height": 400},
    {"name": "particle_burst", "url": "http://localhost:8081/particle_burst.html", "duration": 6, "width": 720, "height": 400},
    {"name": "ascii_logo", "url": "http://localhost:8081/ascii_logo.html", "duration": 5, "width": 820, "height": 400},
    {"name": "progress_bars", "url": "http://localhost:8081/progress_bars.html", "duration": 8, "width": 720, "height": 400},
]


async def record_animation(anim):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            record_video_dir="recorded_videos",
            record_video_size={"width": anim["width"], "height": anim["height"]},
            viewport={"width": anim["width"], "height": anim["height"]},
        )
        page = await context.new_page()
        print(f"  📹 Recording {anim['name']} ...")
        await page.goto(anim["url"], wait_until="domcontentloaded")
        await asyncio.sleep(anim["duration"])
        await context.close()
        video_path = await page.video.path()
        print(f"  ✅ Saved: {video_path}")
        await browser.close()
        return str(video_path)


async def main():
    print("🎬 Starting individual animation recordings...\n")
    results = {}
    for anim in ANIMATIONS:
        path = await record_animation(anim)
        results[anim["name"]] = path
    print("\n🏁 All recordings complete!")
    for name, path in results.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    asyncio.run(main())
