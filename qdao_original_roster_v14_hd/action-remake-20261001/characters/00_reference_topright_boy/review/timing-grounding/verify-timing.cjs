"use strict";
const fs = require("fs"), path = require("path"), assert = require("assert/strict");
const logic = require("./timing-player.js");
const data = JSON.parse(fs.readFileSync(path.join(__dirname,"review-data.json"),"utf8"));
let checks = 0;
assert.deepEqual(data.modes.map(mode => mode.id), ["adopted-960"]); checks++;
assert.equal(data.adoptedMode, "adopted-960"); checks++;
assert.deepEqual(data.playback.map(item => item.rate), [1, 0.25]); checks++;
const mode = data.modes[0];
assert.deepEqual(mode.durationsMs, Array(16).fill(60)); checks++;
assert.equal(mode.cycleMs, 960); checks++;
for (const playback of data.playback) {
  const durations = mode.durationsMs.map(ms => ms * playback.durationMultiplier);
  const cycle = mode.cycleMs * playback.durationMultiplier;
  assert.equal(logic.totalDuration(durations), cycle); checks++;
  let start = 0;
  for (let frame = 0; frame < 16; frame++) {
    assert.equal(logic.startForFrame(durations, frame), start);
    assert.equal(logic.frameAt(durations, start), frame);
    assert.equal(logic.frameAt(durations, start + durations[frame] - 0.001), frame);
    assert.equal(logic.frameAt(durations, start + cycle * 10), frame);
    assert.equal(logic.frameAt(mode.durationsMs, start * playback.rate), frame);
    start += durations[frame]; checks += 5;
  }
  assert.equal(logic.frameAt(durations, cycle), 0);
  assert.equal(logic.frameAt(durations, cycle - 0.001), 15);
  assert.equal(logic.frameAt(durations, -0.001), 15); checks += 3;
}
const html = fs.readFileSync(path.join(__dirname,"index.html"),"utf8");
const js = fs.readFileSync(path.join(__dirname,"timing-player.js"),"utf8");
const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);
assert.equal(ids.length,new Set(ids).size); checks++;
for (const match of js.matchAll(/getElementById\("([^"]+)"\)/g)) {
  assert.ok(ids.includes(match[1]), "Missing control: " + match[1]); checks++;
}
const speed = html.match(/<select id="speed">([\s\S]*?)<\/select>/)[1];
assert.deepEqual([...speed.matchAll(/value="([^"]+)"/g)].map(match => Number(match[1])), [1, 0.25]); checks++;
for (const source of data.sources) {
  assert.ok(fs.existsSync(path.resolve(__dirname, source.browserPath)));
  assert.equal(source.manifestFrameDurationMs, 60); checks += 2;
}
assert.equal(data.products.length, 4); checks++;
for (const product of data.products) {
  const multiplier = product.playbackId === "normal" ? 1 : 4;
  assert.equal(product.modeId, "adopted-960");
  assert.deepEqual(product.durationsMs, Array(16).fill(60 * multiplier));
  assert.equal(product.cycleMs, 960 * multiplier);
  assert.ok(html.includes(product.file)); checks += 4;
}
process.stdout.write(JSON.stringify({status:"passed",checks,scope:"syntax separately; uniform normal/slow timing, loop boundaries, frame stepping, controls and local sources; no browser visual playback"}));
