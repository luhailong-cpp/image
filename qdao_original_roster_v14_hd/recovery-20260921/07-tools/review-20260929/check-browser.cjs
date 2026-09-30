const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { chromium } = require('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const out = __dirname;
const root = path.resolve(out, '..');
const source = path.join(root, 'candidate/07_moon_shadow_assassin_girl');
const prior = JSON.parse(fs.readFileSync(path.join(root, 'acceptance-status-20260928.json'), 'utf8'));
const url = 'http://127.0.0.1:8891/qdao_original_roster_v14_hd/recovery-20260921/07-delivery-preview/final-candidates-20260928/index.html';
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const evidence = { character: prior.character, startedAt: new Date().toISOString(), url,
  browser: 'isolated installed Chrome, Playwright headless', scope: 'Actual local browser playback and rendered-frame captures; visual acceptance is recorded separately.',
  formalApproval: false, clientIntegration: false, visualAcceptance: 'pending_review_of_rendered_frames',
  bindings: prior.bindings, errors: [], directions: [], responses: [] };
const requireOk = (ok, message) => { if (!ok) throw new Error(message); };

(async () => {
  for (const b of prior.bindings) requireOk(sha(fs.readFileSync(path.join(source, b.slot))) === b.sha256, 'Source changed: ' + b.slot);
  fs.mkdirSync(path.join(out, 'screenshots'), { recursive: true });
  const browser = await chromium.launch({ headless: true, executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
  try {
    const page = await browser.newPage({ viewport: { width: 1600, height: 1500 }, deviceScaleFactor: 1 });
    page.on('pageerror', e => evidence.errors.push(e.message));
    page.on('response', r => { if (r.url().includes('/candidate/') && r.url().endsWith('.png')) evidence.responses.push({ url: r.url(), status: r.status() }); });
    await page.goto(url, { waitUntil: 'networkidle' });
    const canvas = page.locator('#canvas');
    async function screen(name) {
      const p = path.join(out, 'screenshots', name + '.png');
      await canvas.screenshot({ path: p });
      return { path: p, sha256: sha(fs.readFileSync(p)) };
    }
    async function observe(ms) {
      const observed = [];
      const start = Date.now();
      while (Date.now() - start < ms) {
        const line = await page.locator('#info').innerText();
        const slot = line.split(' · ')[0];
        if (!observed.length || observed.at(-1).slot !== slot) observed.push({ ms: Date.now() - start, slot });
        await page.waitForTimeout(8);
      }
      return observed;
    }
    for (const dir of ['N','NE','E','SE','S','SW','W','NW']) {
      const result = { direction: dir, playback: [], captures: [], idle: [] };
      await page.locator('#direction').selectOption(dir);
      await page.locator('#action').selectOption('walk');
      await page.locator('#size').selectOption('512');
      for (const speed of ['30','120']) {
        await page.locator('#speed').selectOption(speed);
        await page.locator('#timeline button').first().click();
        await page.locator('#play').click();
        requireOk((await page.locator('#play').innerText()) === '暂停', 'Playback did not start');
        const observed = await observe(speed === '30' ? 1650 : 2250);
        const distinct = [...new Set(observed.map(x => x.slot))];
        requireOk(distinct.length === 16, `${dir} speed ${speed}: observed ${distinct.length}/16 frames`);
        const capture = await screen(`${dir}-playing-${speed}ms`);
        await page.locator('#play').click();
        result.playback.push({ requestedFrameMs: Number(speed), observed, distinctFrames: distinct.length, capture });
      }
      for (const [label,bg] of [['light','#f0eee4'],['dark','#20262e']]) {
        await page.locator('#bg').selectOption(bg);
        await page.locator('#size').selectOption('512');
        for (let n=1; n<=16; n++) {
          await page.locator('#timeline button').nth(n-1).click();
          const expected = `walk/${dir}/${String(n).padStart(2,'0')}.png`;
          requireOk((await page.locator('#info').innerText()).startsWith(expected), 'Wrong displayed slot');
          result.captures.push({ slot: expected, background: label, displayPx: 512, ...await screen(`${dir}-${String(n).padStart(2,'0')}-${label}-512`) });
        }
        await page.locator('#size').selectOption('1024');
        for (const n of [15,16,1,2]) {
          await page.locator('#timeline button').nth(n-1).click();
          result.captures.push({ slot: `walk/${dir}/${String(n).padStart(2,'0')}.png`, background: label, displayPx: 1024, ...await screen(`${dir}-${String(n).padStart(2,'0')}-${label}-1024`) });
        }
        await page.locator('#action').selectOption('idle');
        result.idle.push({ slot: `idle/${dir}.png`, background: label, displayPx: 1024, ...await screen(`${dir}-idle-${label}-1024`) });
        await page.locator('#action').selectOption('walk');
      }
      evidence.directions.push(result);
      fs.writeFileSync(path.join(out, 'browser-observation.partial.json'), JSON.stringify(evidence,null,2));
      console.log(`${dir}: observed all 16 frames at 30/120 ms; captured both backgrounds and seam`);
    }
    for (const b of prior.bindings) requireOk(sha(fs.readFileSync(path.join(source, b.slot))) === b.sha256, 'Source changed during review: ' + b.slot);
    requireOk(evidence.errors.length === 0, 'Browser console errors');
    requireOk(evidence.responses.length === 136 && evidence.responses.every(x => x.status === 200), 'PNG load error');
    evidence.technicalPlaybackPassed = true;
  } finally {
    await browser.close();
    evidence.finishedAt = new Date().toISOString();
    fs.writeFileSync(path.join(out, 'browser-observation.json'), JSON.stringify(evidence,null,2));
  }
})().catch(error => {
  evidence.errors.push(error.stack || String(error));
  evidence.technicalPlaybackPassed = false;
  fs.writeFileSync(path.join(out, 'browser-observation.json'), JSON.stringify(evidence,null,2));
  console.error(error.message);
  process.exitCode = 1;
});
