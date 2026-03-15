"""
Record the complete consciousness journey from GitHub Pages:
  SplashScreen → 3D Globe → Click consciousness node → Detail panel → Close

Produces a WebM video that can be converted to animated WebP for README.
"""
import asyncio
from playwright.async_api import async_playwright

GITHUB_PAGES_URL = "https://jinning6.github.io/Noosphere/"

async def record_full_journey():
    """Recording 1: Full SplashScreen → Globe → Click Node → Detail Panel"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            record_video_dir="recorded_videos",
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720},
        )
        page = await context.new_page()
        
        print("📹 Recording #1: Full Consciousness Journey...")
        print("   Loading GitHub Pages...")
        await page.goto(GITHUB_PAGES_URL, wait_until="domcontentloaded")
        
        # Phase 1-3: SplashScreen (~6s)
        print("   ⏳ SplashScreen animating...")
        await asyncio.sleep(7)
        
        # Main scene cinematic push-in (~5s)
        print("   ⏳ 3D Globe materializing...")
        await asyncio.sleep(6)
        
        # Click on a consciousness node in the globe area
        print("   🖱️ Clicking consciousness node...")
        await page.mouse.click(750, 400)
        await asyncio.sleep(1)
        
        # If first click didn't hit a node, try another position
        # Check if detail panel appeared
        panel = await page.query_selector('[style*="slideIn"]')
        if not panel:
            print("   🖱️ Retrying click at different position...")
            await page.mouse.click(680, 350)
            await asyncio.sleep(1)
        if not panel:
            await page.mouse.click(600, 420)
            await asyncio.sleep(1)
        if not panel:
            await page.mouse.click(720, 480)
            await asyncio.sleep(1)
            
        # Show detail panel (~4s)
        print("   📖 Detail panel displayed...")
        await asyncio.sleep(4)
        
        # Close detail panel — click ✕ button (top-right area of right panel)
        print("   ❌ Closing panel...")
        close_btn = await page.query_selector('button')
        if close_btn:
            await close_btn.click()
        else:
            # Fallback: click approximate position of close button
            await page.mouse.click(1240, 30)
        await asyncio.sleep(3)
        
        print("   ✅ Recording complete!")
        await context.close()
        video_path = await page.video.path()
        print(f"   📁 Saved: {video_path}")
        await browser.close()
        return str(video_path)


async def record_globe_interaction():
    """Recording 2: Globe interaction close-up (no splash, jump straight to scene)"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            record_video_dir="recorded_videos",
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720},
        )
        page = await context.new_page()
        
        print("\n📹 Recording #2: Globe Interaction Close-up...")
        print("   Loading GitHub Pages...")
        await page.goto(GITHUB_PAGES_URL, wait_until="domcontentloaded")
        
        # Wait for splash to complete
        print("   ⏳ Waiting for splash to complete...")
        await asyncio.sleep(8)
        
        # Wait for scene to settle
        print("   ⏳ Scene settling...")
        await asyncio.sleep(5)
        
        # Smooth rotate showcase (the globe auto-rotates)
        print("   🌍 Globe auto-rotating showcase...")
        await asyncio.sleep(3)
        
        # Click different nodes
        print("   🖱️ Clicking node #1...")
        await page.mouse.click(700, 380)
        await asyncio.sleep(0.5)
        await page.mouse.click(650, 350)
        await asyncio.sleep(0.5)
        await page.mouse.click(750, 420)
        await asyncio.sleep(3)
        
        # Close panel
        close_btn = await page.query_selector('button')
        if close_btn:
            await close_btn.click()
        await asyncio.sleep(2)
        
        # Click another node
        print("   🖱️ Clicking node #2...")
        await page.mouse.click(550, 300)
        await asyncio.sleep(0.5)
        await page.mouse.click(500, 400)
        await asyncio.sleep(3)
        
        # Close again
        close_btn = await page.query_selector('button')
        if close_btn:
            await close_btn.click()
        await asyncio.sleep(2)
        
        print("   ✅ Recording complete!")
        await context.close()
        video_path = await page.video.path()
        print(f"   📁 Saved: {video_path}")
        await browser.close()
        return str(video_path)


async def main():
    print("🎬 === Noosphere Consciousness Journey Recorder ===\n")
    
    path1 = await record_full_journey()
    path2 = await record_globe_interaction()
    
    print(f"\n🏁 All recordings complete!")
    print(f"   Journey: {path1}")
    print(f"   Globe:   {path2}")
    print(f"\n💡 Convert to WebP with:")
    print(f"   ffmpeg -i {path1} -vf \"fps=12,scale=1280:-1\" -loop 0 -quality 80 assets/splash_cinematic.webp")
    print(f"   ffmpeg -i {path2} -vf \"fps=12,scale=1280:-1\" -loop 0 -quality 80 assets/globe_demo.webp")


if __name__ == "__main__":
    asyncio.run(main())
