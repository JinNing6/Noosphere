import puppeteer from 'puppeteer';
import * as path from 'path';

(async () => {
  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();
  
  // Navigate to local dev server
  await page.goto('http://localhost:5173/Noosphere/');
  
  // Wait for the main globe to load
  await page.waitForTimeout(2000);
  
  // Click the 🌌 button to open the contribution graph
  // It's a div containing the 🌌 emoji
  await page.evaluate(() => {
    const emojis = document.querySelectorAll('div');
    for (const el of emojis) {
      if (el.textContent === '🌌') {
        el.click();
        break;
      }
    }
  });
  
  // Wait for the panel's animation to finish
  await page.waitForTimeout(1000);
  
  // take a screenshot
  const shotPath = path.resolve('titles_screenshot.png');
  await page.screenshot({ path: shotPath, fullPage: true });
  console.log(`Screenshot saved to ${shotPath}`);
  
  await browser.close();
})();
