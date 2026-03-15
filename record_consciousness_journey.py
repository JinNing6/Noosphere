"""
Record the complete consciousness journey from GitHub Pages.
Uses HEADED mode with GPU args for proper WebGL/Three.js rendering.

Recording 1 (splash_cinematic): Full SplashScreen → 3D Globe → Click node → Detail panel
Recording 2 (globe_demo):       Skip splash → 3D Globe interaction showcase
"""
import asyncio
from playwright.async_api import async_playwright

GITHUB_PAGES_URL = "https://jinning6.github.io/Noosphere/"

# Chromium args to enable proper WebGL rendering
GPU_ARGS = [
    "--enable-webgl",
    "--use-gl=angle",
    "--enable-gpu",
    "--enable-features=Vulkan",
    "--ignore-gpu-blocklist",
]


async def record_full_journey():
    """Recording 1: SplashScreen → Globe → Click Node → Detail Panel (splash_cinematic.webp)"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=GPU_ARGS,
        )
        context = await browser.new_context(
            record_video_dir="recorded_videos/journey",
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720},
        )
        page = await context.new_page()

        print("📹 [Recording 1] Full Consciousness Journey")
        print("   Loading GitHub Pages...")
        await page.goto(GITHUB_PAGES_URL, wait_until="networkidle", timeout=30000)

        # Phase 1-3: SplashScreen (~7s)
        print("   ⏳ SplashScreen phases 1-3...")
        await asyncio.sleep(8)

        # 3D Globe cinematic push-in (~6s)
        print("   🌍 3D Globe materializing + cinematic push-in...")
        await asyncio.sleep(7)

        # Try clicking multiple positions on the globe to hit a node
        print("   🖱️ Clicking consciousness nodes...")
        positions = [
            (640, 360), (700, 340), (580, 400),
            (720, 420), (550, 320), (660, 380),
            (750, 350), (600, 450), (680, 300),
        ]
        panel_found = False
        for x, y in positions:
            await page.mouse.click(x, y)
            await asyncio.sleep(0.3)
            # Check for detail panel
            panel = await page.query_selector('div[style*="animation: slideIn"]')
            if not panel:
                panel = await page.evaluate("""
                    () => {
                        const el = document.querySelector('div[style*="420"]');
                        return el && el.querySelector('h2') ? true : false;
                    }
                """)
            if panel:
                panel_found = True
                print(f"   ✅ Node hit at ({x},{y})! Detail panel opened.")
                break

        if not panel_found:
            print("   ⚠️ No node hit, trying more positions...")
            for x, y in [(500, 350), (400, 300), (800, 400), (650, 450), (700, 280)]:
                await page.mouse.click(x, y)
                await asyncio.sleep(0.4)

        # Show detail panel content
        print("   📖 Displaying detail panel...")
        await asyncio.sleep(5)

        # Close panel
        print("   ❌ Closing panel...")
        buttons = await page.query_selector_all('button')
        for btn in buttons:
            text = await btn.text_content()
            if '✕' in (text or ''):
                await btn.click()
                break
        else:
            # fallback
            if buttons:
                await buttons[0].click()

        # Final globe rotation showcase
        print("   🌐 Final globe rotation...")
        await asyncio.sleep(3)

        print("   ✅ Recording 1 complete!")
        await context.close()
        video_path = await page.video.path()
        print(f"   📁 Saved: {video_path}")
        await browser.close()
        return str(video_path)


async def record_globe_close_up():
    """Recording 2: Skip splash, start from globe, show multi-node interactions (globe_demo.webp)"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=GPU_ARGS,
        )
        context = await browser.new_context(
            record_video_dir="recorded_videos/globe",
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720},
        )
        page = await context.new_page()

        print("\n📹 [Recording 2] Globe Interaction Close-up")
        print("   Loading GitHub Pages + waiting for splash to finish...")
        await page.goto(GITHUB_PAGES_URL, wait_until="networkidle", timeout=30000)

        # Wait for splash + scene to fully settle
        await asyncio.sleep(15)

        # Now the 3D globe should be fully visible and settled
        print("   🌍 Globe showcase — auto-rotation...")
        await asyncio.sleep(4)

        # Drag rotate the globe to show it from different angles
        print("   🖱️ Interactive orbit rotation...")
        await page.mouse.move(640, 360)
        await page.mouse.down()
        for i in range(30):
            await page.mouse.move(640 + i * 5, 360 + i * 1, steps=2)
            await asyncio.sleep(0.03)
        await page.mouse.up()
        await asyncio.sleep(2)

        # Click node attempt 1
        print("   🖱️ Clicking node #1...")
        for x, y in [(650, 370), (700, 340), (580, 400), (720, 420), (600, 300)]:
            await page.mouse.click(x, y)
            await asyncio.sleep(0.3)
        await asyncio.sleep(3)

        # Close panel if opened
        buttons = await page.query_selector_all('button')
        for btn in buttons:
            text = await btn.text_content()
            if '✕' in (text or ''):
                await btn.click()
                break
        await asyncio.sleep(2)

        # Drag rotate in opposite direction
        print("   🖱️ Rotating globe in opposite direction...")
        await page.mouse.move(800, 360)
        await page.mouse.down()
        for i in range(30):
            await page.mouse.move(800 - i * 6, 360 - i * 2, steps=2)
            await asyncio.sleep(0.03)
        await page.mouse.up()
        await asyncio.sleep(2)

        # Click node attempt 2
        print("   🖱️ Clicking node #2...")
        for x, y in [(550, 320), (480, 380), (610, 440), (520, 350), (680, 280)]:
            await page.mouse.click(x, y)
            await asyncio.sleep(0.3)
        await asyncio.sleep(3)

        # Close panel
        buttons = await page.query_selector_all('button')
        for btn in buttons:
            text = await btn.text_content()
            if '✕' in (text or ''):
                await btn.click()
                break
        await asyncio.sleep(2)

        print("   ✅ Recording 2 complete!")
        await context.close()
        video_path = await page.video.path()
        print(f"   📁 Saved: {video_path}")
        await browser.close()
        return str(video_path)


async def main():
    print("🎬 === Noosphere Consciousness Journey Recorder v2 ===")
    print("   Mode: HEADED (GPU-accelerated WebGL)\n")

    path1 = await record_full_journey()
    path2 = await record_globe_close_up()

    print(f"\n🏁 All recordings complete!")
    print(f"   Journey:  {path1}")
    print(f"   Globe:    {path2}")
    print(f"\n💡 Convert to WebP:")
    print(f'   ffmpeg -y -i "{path1}" -vf "fps=15,scale=1280:-1" -loop 0 -quality 80 assets/splash_cinematic.webp')
    print(f'   ffmpeg -y -i "{path2}" -vf "fps=15,scale=1280:-1" -loop 0 -quality 80 assets/globe_demo.webp')


if __name__ == "__main__":
    asyncio.run(main())
