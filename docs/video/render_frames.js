// CH-13B - render every still frame of the video.
//
// Reads the plan written by docs/video/build_video.py and screenshots one
// 1920x1080 PNG per caption segment. The caption is written INTO the page - the
// deck carries the band, hidden, and this script adds body.cap and fills it -
// so what ffmpeg later concatenates is a picture of a laid-out document, not a
// picture with text stamped on top of it.
//
//   node docs/video/render_frames.js dist/plan.json
//
// It reports the measured height of every caption it renders. A caption that runs
// to three lines would overflow the 150px band, and the builder fails on that
// rather than shipping a clipped word.

const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');

const REPO = path.resolve(__dirname, '..', '..');
const { chromium } = require(path.join(REPO, 'scraper', 'node_modules', 'playwright'));

const PLAN = JSON.parse(fs.readFileSync(process.argv[2], 'utf-8'));
const OUT_DIR = path.join(REPO, PLAN.frames_dir);
const VIEW = { width: 1920, height: 1080 };

const url = (rel) => pathToFileURL(path.join(REPO, rel)).href;

(async () => {
  fs.rmSync(OUT_DIR, { recursive: true, force: true });
  fs.mkdirSync(OUT_DIR, { recursive: true });

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: VIEW, deviceScaleFactor: 1, colorScheme: 'light',
  });
  const page = await context.newPage();
  const measured = [];

  for (const frame of PLAN.frames) {
    // A hash-only change does not reload, so the deck's start-up code would not
    // re-read it. The cache-busting query forces a real navigation; the deck
    // ignores everything but the hash.
    const target = frame.source === 'deck'
      ? url('docs/slides/index.html') + '?f=' + frame.index + '#' + frame.slide + '.' + frame.step
      : url(frame.source);
    await page.goto(target, { waitUntil: 'load' });

    const info = await page.evaluate((caption) => {
      const root = document.querySelector('#stage') || document.body;
      const band = document.querySelector('#caption');
      // The end card is not the deck and carries no band. It still gets measured for
      // overflow, because a card that does not fit 1920x1080 is a card with a
      // scrollbar in the middle of the video.
      if (!band) {
        return { caption_h: 0, band_top: null, content_bottom: null, has_band: false,
                 overflow_w: root.scrollWidth, overflow_h: root.scrollHeight };
      }
      const span = band.querySelector('span');
      if (caption) {
        document.body.classList.add('cap');
        span.textContent = caption;
      } else {
        document.body.classList.remove('cap');
        span.textContent = '';
      }
      const on = document.querySelector('.slide.on');
      const content = on ? (on.querySelector('.area') || on.querySelector('.centre')) : null;
      return {
        caption_h: caption ? span.getBoundingClientRect().height : 0,
        band_top: caption ? band.getBoundingClientRect().top : null,
        content_bottom: content ? content.getBoundingClientRect().bottom : null,
        overflow_w: on ? on.scrollWidth : 1920,
        overflow_h: on ? on.scrollHeight : 1080,
        has_band: true,
      };
    }, frame.caption || '');

    await page.waitForTimeout(90);
    const file = path.join(OUT_DIR, String(frame.index).padStart(3, '0') + '.png');
    await page.screenshot({ path: file });
    measured.push({ index: frame.index, file, ...info, words: frame.words || 0 });
  }

  await browser.close();
  fs.writeFileSync(path.join(OUT_DIR, '_measured.json'), JSON.stringify(measured, null, 2));
  const lines = measured.filter((m) => m.caption_h > 0).map((m) => m.caption_h);
  console.log(`rendered ${measured.length} frames into ${PLAN.frames_dir}`);
  if (lines.length) {
    console.log(`caption heights: min ${Math.min(...lines)}px  max ${Math.max(...lines)}px`
      + `  (one line = 43.5px, two = 87px, the band holds 124px of text)`);
  }
})();
