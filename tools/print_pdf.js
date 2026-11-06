// چاپ HTML به PDF با Chromium (Playwright).
// استفاده: node tools/print_pdf.js in1.html out1.pdf [in2.html out2.pdf ...]
// اندازه و حاشیهٔ صفحه از @page در CSS خوانده می‌شود (preferCSSPageSize).
const { chromium } = require('playwright');
const { pathToFileURL } = require('url');

(async () => {
  const args = process.argv.slice(2);
  if (args.length < 2 || args.length % 2) {
    console.error('usage: node print_pdf.js in.html out.pdf [...]');
    process.exit(2);
  }
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (let i = 0; i < args.length; i += 2) {
    await page.goto(pathToFileURL(args[i]).href, { waitUntil: 'load' });
    await page.evaluate(async () => {
      await document.fonts.ready;
      await Promise.all(Array.from(document.images).map(im =>
        im.complete ? null : new Promise(r => { im.onload = im.onerror = r; })));
    });
    await page.pdf({ path: args[i + 1], preferCSSPageSize: true, printBackground: true });
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
