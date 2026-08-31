// CH-13B - record the real codification worksheet being read.
//
// The brief asks for one realistic execution walked through from start to finish.
// The deck can show a picture of the artifact; this shows the artifact. A browser
// opens docs/worksheet/index.html and scrolls it, slowly, with no cursor, no
// clicking and no highlight boxes drawn over it. The page is the evidence.
//
//   node docs/video/record_worksheet.js
//
// Writes dist/screencast/worksheet.webm plus worksheet.json, and prints the
// storyboard it actually executed - every scroll target resolved to a pixel offset,
// so the recording can be checked against the page rather than described.
// dist/ is git-ignored.
//
// The sidecar records what the WALL CLOCK saw. build_video.py does NOT trim or time the
// captions from it - an earlier version of this comment said it did, and that was the
// bug. Playwright's capture drops frames under load, so wall-clock offsets do not map
// onto video time; the tape's own beat stamp (see MARK below) is what the builder reads.
// The sidecar survives so the report can print both clocks side by side.
//
// The page is 14,791px tall at this viewport - 14,951 with the tail spacer below - so
// the scrolling is real: the recording travels about 13,870px of a document that does
// not fit on any screen. The script prints both figures; do not trust these.

const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');

const REPO = path.resolve(__dirname, '..', '..');
const { chromium } = require(path.join(REPO, 'scraper', 'node_modules', 'playwright'));

const PAGE = pathToFileURL(path.join(REPO, 'docs', 'worksheet', 'index.html')).href;
const OUT_DIR = path.join(REPO, 'dist', 'screencast');
const OUT = path.join(OUT_DIR, 'worksheet.webm');

const STEP_MS = 40;          // one scroll tick - a real scroll, not a jump
const VIEW = { width: 1920, height: 1080 };

// The recording carries its own clock. Chromium's capture drops frames under load, so
// wall-clock offsets do not map onto video time - the first build timed the screencast
// captions off this script's clock and put a caption naming 49 CFR 1150.35 over
// 47 CFR 80.905. So a patch in the bottom-left changes grey at the start of each beat,
// and build_video.py reads it back per frame. It is never seen: it sits at y=1000-1080,
// inside the strip the caption band paints over, and build_video.py asserts that rather
// than assuming it. These constants are duplicated there; both sides state it.
const MARK = { x: 0, y: 1000, w: 120, h: 80 };
const MARK_LEVELS = [20, 70, 120, 170, 220];
const MARK_IDLE = 255;

// The caption band is opaque and covers the bottom 150px of every recorded frame. At the
// final scroll position that strip lands on page y 14641-14791, and the worksheet's LAST
// paragraph - "What this page is not. It is not a filing, not a legal opinion, and not a
// reviewed document." - sits at 14692-14734. The band was erasing the one paragraph in
// the artifact that states its own limits, in a submission whose whole argument is that
// limits get stated. So the page is given 160px of scrollable air at the foot; the
// assertion below proves the paragraph then clears the band instead of assuming it.
const BAND_H = 150;
const TAIL_SPACER_PX = 160;

// The storyboard. Each leg names what the viewer is meant to be reading, how long
// the scroll to it takes, and how long the page then holds still.
const STORYBOARD = [
  // 3.4s, not the 2s first drafted. This beat carries a caption, and no caption in
  // this video is on screen for less than 3.0s - build_video.py fails the build if one
  // would be. The floor wins over the hold; the card sanctions holding longer.
  { name: 'the top of the page - title, the NOT A FILING band, and what it is drawn from',
    scrollMs: 0, holdMs: 3400, target: () => 0 },

  { name: '40 CFR 75.6 - the failing designation (a)(38) and its failure class',
    scrollMs: 5000, holdMs: 3000,
    target: () => document.getElementById('05-8447--75.6').offsetTop - 40 },

  { name: "49 CFR 1150.35 - the trace row where cfr_resolve returned found=false, "
        + 'level=none, and the page says why',
    scrollMs: 4000, holdMs: 4000,
    target: () => {
      const item = document.getElementById('2016-03298--1150.35');
      const trace = item.querySelector('table.trace');
      return trace.getBoundingClientRect().top + window.scrollY - 120;
    } },

  { name: 'the human-checkpoint queue - 16 of 82, each with its reason verbatim',
    scrollMs: 5000, holdMs: 4000,
    target: () => {
      const h = [...document.querySelectorAll('h2')]
        .find(n => n.textContent.includes('Human-checkpoint queue'));
      return h.getBoundingClientRect().top + window.scrollY - 40;
    } },

  { name: 'the provenance footer - the three input hashes, both commits, arm and model',
    scrollMs: 4000, holdMs: 3000,
    target: () => document.querySelector('footer').getBoundingClientRect().top
                  + window.scrollY - 40 },
];

async function glide(page, toY, ms) {
  if (ms <= 0) return;
  const steps = Math.max(1, Math.round(ms / STEP_MS));
  await page.evaluate(
    async ({ toY, steps, stepMs }) => {
      const from = window.scrollY;
      const delta = toY - from;
      const sleep = (t) => new Promise((r) => setTimeout(r, t));
      for (let i = 1; i <= steps; i++) {
        window.scrollTo(0, Math.round(from + (delta * i) / steps));
        await sleep(stepMs);
      }
    },
    { toY, steps, stepMs: STEP_MS },
  );
}

(async () => {
  fs.rmSync(OUT_DIR, { recursive: true, force: true });
  fs.mkdirSync(OUT_DIR, { recursive: true });

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: VIEW,
    deviceScaleFactor: 1,
    colorScheme: 'light',              // the worksheet has a dark-mode rule; the deck is light
    recordVideo: { dir: OUT_DIR, size: VIEW },
  });
  const recordingStartedAt = Date.now();   // the context is open; the tape is rolling
  const page = await context.newPage();
  await page.goto(PAGE, { waitUntil: 'load' });
  await page.evaluate((mark) => {
    window.scrollTo(0, 0);
    // Kill smooth-scroll if the page ever asks for it: the glide below owns the
    // motion, and two easings fighting each other reads as a stutter.
    document.documentElement.style.scrollBehavior = 'auto';
    const spacer = document.createElement('div');
    spacer.id = '__bandspacer';
    spacer.style.cssText = `height:${mark.tail}px`;
    document.body.appendChild(spacer);
    const el = document.createElement('div');
    el.id = '__beatmark';
    el.style.cssText = `position:fixed;left:${mark.x}px;top:${mark.y}px;`
      + `width:${mark.w}px;height:${mark.h}px;z-index:2147483647;`
      + `background:rgb(${mark.idle},${mark.idle},${mark.idle})`;
    document.body.appendChild(el);
  }, { ...MARK, idle: MARK_IDLE, tail: TAIL_SPACER_PX });

  // measured, not assumed: the last footer paragraph must clear the band at max scroll
  const tail = await page.evaluate((bandH) => {
    const ps = [...document.querySelectorAll('footer p')];
    const last = ps[ps.length - 1];
    const bottom = last.getBoundingClientRect().bottom + window.scrollY;
    const maxY = document.documentElement.scrollHeight - window.innerHeight;
    return { bottom, bandCoversFrom: maxY + (1080 - bandH),
             text: last.textContent.trim().slice(0, 40) };
  }, BAND_H);
  if (tail.bottom >= tail.bandCoversFrom) {
    throw new Error(`the caption band would cover the worksheet's last paragraph `
      + `("${tail.text}...": ends at ${tail.bottom}, band starts at ${tail.bandCoversFrom}) `
      + `- raise TAIL_SPACER_PX`);
  }

  const height = await page.evaluate(() => document.documentElement.scrollHeight);
  await page.waitForTimeout(600);          // let the first paint settle before beat 1
  const leadInMs = Date.now() - recordingStartedAt;
  // Every boundary below is a MEASURED offset into the recording, not a planned
  // one. 40ms of requested setTimeout is never 40ms of real time, so an 18-second
  // plan came out 3 seconds long the first time this ran - and a caption timed off
  // the plan would then have sat over the wrong part of the page.
  const now = () => (Date.now() - recordingStartedAt) / 1000;
  const started = [];

  for (const [k, leg] of STORYBOARD.entries()) {
    const toY = await page.evaluate(leg.target);
    await page.evaluate((v) => {
      document.getElementById('__beatmark').style.background = `rgb(${v},${v},${v})`;
    }, MARK_LEVELS[k]);
    const t0 = now();
    await glide(page, toY, leg.scrollMs);
    const holdFrom = now();
    await page.waitForTimeout(leg.holdMs);
    const holdTo = now();
    const y = await page.evaluate(() => window.scrollY);
    started.push({ leg, toY, y, t0, holdFrom, holdTo });
  }
  const elapsed = started[started.length - 1].holdTo;

  const video = page.video();
  await context.close();
  await browser.close();
  const produced = await video.path();
  if (produced !== OUT) fs.renameSync(produced, OUT);

  const sidecar = {
    lead_in_s: +(leadInMs / 1000).toFixed(3),
    ends_at_s: +elapsed.toFixed(3),
    measured_duration_s: +(elapsed - leadInMs / 1000).toFixed(3),
    page_height_px: height,
    scrolled_px: started[started.length - 1].y,
    viewport: VIEW,
    step_ms: STEP_MS,
    beats: started.map((s) => ({
      name: s.leg.name,
      scroll_from_s: +s.t0.toFixed(3),
      hold_from_s: +s.holdFrom.toFixed(3),
      hold_to_s: +s.holdTo.toFixed(3),
      scroll_y: s.y,
    })),
  };
  fs.writeFileSync(path.join(OUT_DIR, 'worksheet.json'), JSON.stringify(sidecar, null, 2));

  console.log(`page height        ${height}px at ${VIEW.width}x${VIEW.height}`);
  console.log(`tail spacer        ${TAIL_SPACER_PX}px, so the band clears the last `
    + `paragraph by ${Math.round(tail.bandCoversFrom - tail.bottom)}px`);
  console.log(`lead-in measured   ${(leadInMs / 1000).toFixed(2)}s (trimmed off by build_video.py)`);
  console.log(`scrolled through   ${started[started.length - 1].y}px`);
  console.log(`measured duration  ${(elapsed - leadInMs / 1000).toFixed(2)}s after the trim`);
  console.log('');
  for (const s of started) {
    console.log(`  ${s.t0.toFixed(1).padStart(5)}s -> ${s.holdTo.toFixed(1).padStart(5)}s  `
      + `y=${String(s.y).padStart(6)}  hold ${s.holdFrom.toFixed(1)}-${s.holdTo.toFixed(1)}s`);
    console.log(`         ${s.leg.name}`);
  }
  console.log('');
  console.log(`wrote ${OUT}  ${fs.statSync(OUT).size} bytes`);
})();
