// اسکرین‌شات کامل یک صفحهٔ HTML (برای جدول هفتگی). استفاده: node tools/screenshot.js in.html out.png
const { chromium } = require('playwright');
const { pathToFileURL } = require('url');
(async () => {
  const [inp, out] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1560, height: 900 }, deviceScaleFactor: 2 });
  await page.goto(pathToFileURL(inp).href, { waitUntil: 'load' });
  await page.evaluate(async () => { await document.fonts.ready; });
  await page.screenshot({ path: out, fullPage: true });
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
