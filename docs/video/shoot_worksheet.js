// CH-13B - one 1920x1080 screenshot of the real shipped worksheet.
//
// The deck's worksheet slide must show the artifact itself, not a mock-up of it,
// so the picture is taken by a browser from docs/worksheet/index.html and then
// inlined by docs/video/embed_worksheet_shot.py. Re-running this script and the
// embedder reproduces the slide from the committed page.
//
//   node docs/video/shoot_worksheet.js
//
// Writes dist/worksheet-1920x1080.png. dist/ is git-ignored; the PNG reaches the
// repository only as the base64 payload inside docs/slides/index.html.

const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');

const REPO = path.resolve(__dirname, '..', '..');
const { chromium } = require(path.join(REPO, 'scraper', 'node_modules', 'playwright'));

const PAGE = pathToFileURL(path.join(REPO, 'docs', 'worksheet', 'index.html')).href;
const OUT_DIR = path.join(REPO, 'dist');
const OUT = path.join(OUT_DIR, 'worksheet-1920x1080.png');

(async () => {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const browser = await chromium.launch();
  // colorScheme is pinned: the worksheet carries a prefers-color-scheme: dark rule
  // and the deck is a light document. An unpinned default would make the slide
  // depend on the machine that rendered it.
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    colorScheme: 'light',
  });
  const page = await context.newPage();
  await page.goto(PAGE, { waitUntil: 'load' });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(400);
  await page.screenshot({ path: OUT, fullPage: false });
  const h = await page.evaluate(() => document.documentElement.scrollHeight);
  await browser.close();
  const bytes = fs.statSync(OUT).size;
  console.log('wrote ' + OUT);
  console.log('viewport 1920x1080 | page scrollHeight ' + h + 'px | png ' + bytes + ' bytes');
})();
