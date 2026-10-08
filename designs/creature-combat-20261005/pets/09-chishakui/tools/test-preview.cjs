// State tests only; this does not open a browser or claim rendered visual playback.
const assert = require('node:assert/strict');
const Timeline = require('../preview/playback-state.js');
const results = [];
for (const [action, count, ms] of [['hit', 6, 40], ['attack', 12, 30], ['cast', 16, 45]]) {
  const t = new Timeline(count, ms);
  t.advance(ms * 4.5);
  assert.deepEqual(t.frames, [4, 1], 'normal and slow clocks diverge correctly');
  const held = [t.normalMs, t.slowMs];
  t.paused = true;
  t.advance(5000);
  assert.deepEqual([t.normalMs, t.slowMs], held, 'local pause preserves both subframe positions');
  t.paused = false;
  t.advance(5000, true);
  assert.deepEqual([t.normalMs, t.slowMs], held, 'global pause preserves both clocks');
  t.advance(ms * 0.5);
  assert.deepEqual(t.frames, [5, 1], 'resume continues without wall-clock jump');
  t.seek(count - 1);
  assert.deepEqual(t.frames, [count - 1, count - 1]);
  t.step(1);
  assert.deepEqual(t.frames, [0, 0], 'next wraps last to first');
  t.step(-1);
  assert.deepEqual(t.frames, [count - 1, count - 1], 'previous wraps first to last');
  t.paused = false;
  t.advance(ms);
  assert.deepEqual(t.frames, [0, count - 1], 'resumed scrub has independent normal/slow clocks');
  t.reset();
  assert.equal(t.paused, false);
  assert.deepEqual(t.frames, [0, 0]);
  t.advance(count * ms);
  assert.deepEqual(t.frames, [0, Math.floor(count / 4)], 'normal cycle is exact');
  t.reset();
  t.advance(count * ms * 4);
  assert.deepEqual(t.frames, [0, 0], 'both cycles align at exact 4x duration');
  results.push({action, count, durationMs: ms, passed: true});
}
console.log(JSON.stringify({kind: 'non-browser timeline state tests', results, visualPlaybackVerified: false}));
