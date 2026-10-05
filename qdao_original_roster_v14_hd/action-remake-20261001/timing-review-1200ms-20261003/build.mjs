import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import crypto from 'node:crypto';
import vm from 'node:vm';

const out = path.dirname(fileURLToPath(import.meta.url));
const batch = path.dirname(out);
const dispatchPath = path.join(batch, 'grounding-dispatch-20261003.json');
const dispatch = JSON.parse(fs.readFileSync(dispatchPath, 'utf8').replace(/^\uFEFF/, ''));
const dirs = ['N','NE','E','SE','S','SW','W','NW'];
const slash = value => value.replaceAll('\\', '/');
const relative = value => slash(path.relative(out, value));
const characters = [];
const evidence = { schemaVersion: 1, generatedAt: new Date().toISOString(), taskDateLocal: new Date().toLocaleDateString('en-CA', { timeZone: 'America/New_York' }), timezone: 'America/New_York', dispatch: relative(dispatchPath), parameters: { frameCount: 16, normalCycleMs: 1200, normalFrameMs: 75, timing: 'uniform_75ms_per_frame', optionalSlowMotion: [0.5,0.25], historicalSmallerDurationOptionsRemoved: true, hiddenTabBehavior: 'pause', sourcePngsModified: false, imageGeneration: false }, scope: 'Independent normal-speed playback from current manifest selections. User selected 1200ms per complete 16-frame run cycle and removal of smaller-ms options. Artwork and client acceptance are not implied.', browserVisualAcceptance: 'not_performed', characters: [] };

for (const c of dispatch.threads) {
  const root = c.output;
  const sources = [];
  const rows = [];
  const read = name => {
    const full = path.join(root, name);
    const stat = fs.statSync(full);
    const bytes = fs.readFileSync(full);
    sources.push({ path: relative(full), modifiedAt: stat.mtime.toISOString(), sha256: crypto.createHash('sha256').update(bytes).digest('hex') });
    return JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/, ''));
  };
  const add = (frame, rel, dir, order, context = '') => {
    if (!dirs.includes(dir)) return;
    rows.push({ path: rel ? path.resolve(root, rel) : null, direction: dir, order, status: frame.status || frame.visualReview || frame.visualStatus || context || 'manifest_selected', sourceLabel: frame.frame ?? frame.number ?? order, expectedSha256: frame.sha256 || null });
  };
  const standard = (frames, context = '') => {
    for (const f of frames) {
      const rel = f.output || f.candidate || f.file || f.path;
      const match = (rel || '').replaceAll('\\','/').match(/(?:^|\/)run\/(N|NE|E|SE|S|SW|W|NW)\/(?:frame_)?(\d+)\.png$/);
      if (f.action && f.action !== 'run') continue;
      if (!match && f.action !== 'run') continue;
      const d = f.direction || match?.[1];
      const order = Number(match?.[2] ?? f.frame ?? (f.index + 1));
      add(f, rel, d, order, context);
    }
  };
  const id = c.character_id.slice(0,2);
  let status = '当前导出／候选；此页不代表动作验收';
  if (id === '01') {
    const m = read('manifest.json');
    for (const s of m.sequences.filter(s => s.action === 'run')) for (const f of s.frames) add(f, f.path, s.direction, Number(f.frame));
    status = '当前 manifest 选中帧；此页不代表本次姿态复核通过';
  } else if (id === '02') {
    standard(read('inventory.json').frames);
  } else if (id === '03') {
    const main = read('manifest.json');
    const selections = read(main.allActionsSelection);
    for (const g of selections.groups.filter(g => g.action === 'run')) for (const f of g.frames) add(f, f.file, g.direction, Number(f.frame), g.status);
    status = '当前候选；未导出的方向按缺帧标记';
  } else if (id === '04') {
    standard(read('manifest.delivery.json').files);
  } else if (id === '05') {
    standard(read('final/manifest.json').frames);
  } else if (id === '06') {
    const m = read('preview/manifest.json');
    for (const s of m.sequences.filter(s => s.action === 'run')) for (const f of s.frames) add(f, f.path, s.direction, Number(f.number) + 1);
    status = '当前 runtime；原文件编号 00–15，对比按第 1–16 帧显示';
  } else if (id === '09') {
    for (const s of read('manifest.json').sequences.filter(s => s.action === 'run')) for (const f of s.frames) add(f, f.file, s.direction, Number(f.frame));
    status = '用户认可的竹弓少女版本；仅对比播放时长';
  } else if (id === '10') {
    standard(read('manifest.json').slots);
    status = '当前 runtime 正式帧；此页不代表本次姿态复核通过';
  } else if (id === '17') {
    const m = read('manifest.json');
    for (const s of m.sequences.filter(s => s.action === 'run')) for (const f of s.frames) add(f, f.file, s.direction, Number(f.frame));
    status = '当前 runtime 正式帧；此页不代表本次姿态复核通过';
  } else if (id === '20') {
    const m = read('merge-manifest.json');
    for (const g of m.groups.filter(g => g.action === 'run')) for (const f of g.frames.filter(Boolean)) add(f, f.source || f.candidate, g.direction, Number(f.frame));
  } else {
    standard(read('manifest.json').frames);
  }
  const item = { id: c.character_id, name: c.name, status, directions: {} };
  const audit = { id: c.character_id, name: c.name, sourceMetadata: sources, directions: {} };
  for (const d of dirs) {
    const frames = [], errors = [];
    for (let n = 1; n <= 16; n++) {
      const matches = rows.filter(r => r.direction === d && r.order === n);
      if (matches.length !== 1) {
        frames.push(null); errors.push(`${String(n).padStart(2,'0')}: ${matches.length ? '重复选择' : '无当前选择'}`); continue;
      }
      const row = matches[0];
      if (!row.path || !fs.existsSync(row.path)) {
        frames.push(null); errors.push(`${String(n).padStart(2,'0')}: 引用文件缺失${row.path ? ' ' + relative(row.path) : ''}`); continue;
      }
      const stat = fs.statSync(row.path), bytes = fs.readFileSync(row.path);
      if (bytes.subarray(0,8).toString('hex') !== '89504e470d0a1a0a') { frames.push(null); errors.push(`${n}: PNG 文件头错误`); continue; }
      const frame = { index: n, sourceLabel: row.sourceLabel, url: relative(row.path), width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20), modifiedAt: stat.mtime.toISOString(), bytes: stat.size, sha256: crypto.createHash('sha256').update(bytes).digest('hex') };
      frame.expectedSha256 = row.expectedSha256;
      frame.manifestShaMatches = row.expectedSha256 ? row.expectedSha256 === frame.sha256 : null;
      frames.push(frame);
    }
    const complete = frames.every(Boolean);
    item.directions[d] = { complete, available: frames.filter(Boolean).length, frames, errors };
    audit.directions[d] = { complete, available: frames.filter(Boolean).length, missingOrInvalid: errors, frames: frames.filter(Boolean) };
  }
  characters.push(item); evidence.characters.push(audit);
}

const totals = { characters: characters.length, completeDirections: characters.reduce((n,c) => n + Object.values(c.directions).filter(d => d.complete).length, 0), expectedDirections: characters.length * 8, referencedFrames: characters.reduce((n,c) => n + Object.values(c.directions).reduce((v,d) => v + d.available, 0), 0) };
totals.manifestShaMismatches = characters.reduce((n,c) => n + Object.values(c.directions).reduce((v,d) => v + d.frames.filter(f => f && f.manifestShaMatches === false).length, 0), 0);
evidence.totals = totals;
let html = fs.readFileSync(path.join(out, 'template.html'), 'utf8');
html = html.replace('/*__DATA__*/', JSON.stringify({ generatedAt: evidence.generatedAt, characters, totals }).replaceAll('<', '\\u003c'));
const script = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
new vm.Script(script);
const functionText = script.match(/function frameAt\(elapsed, cycle\) \{[^}]+\}/)?.[0];
if (!functionText) throw new Error('frameAt missing');
const frameAt = vm.runInNewContext(functionText + '; frameAt');
for (const cycle of [1200]) {
  if (frameAt(0,cycle)!==0 || frameAt(cycle,cycle)!==0 || frameAt(cycle-0.01,cycle)!==15) throw new Error('Cycle boundary failed');
  for (let i=0;i<16;i++) if (frameAt(i*cycle/16+0.01,cycle)!==i) throw new Error('Frame boundary failed');
}
if (1200 / 16 !== 75) throw new Error('Frame duration division failed');
evidence.validation = { javascriptSyntax: 'passed_node_vm', allNonNullReferencesExist: true, pngHeadersAndDimensionsRead: true, cycleBoundaries: 'passed_1200', exactFrameDuration: '1200_divided_by_16_equals_75', graphicalBrowserQA: 'not_performed', clientRuntimeQA: 'not_performed', incompleteDirectionsPlayback: 'blocked_until_all_16_frames_available', snapshotWarning: 'Other role chats may update PNGs after this snapshot; regenerate with node build.mjs to refresh inventory. No source PNG is copied or modified.' };
fs.writeFileSync(path.join(out, 'index.html'), html);
fs.writeFileSync(path.join(out, 'evidence.json'), JSON.stringify(evidence,null,2)+'\n');
console.log(JSON.stringify({ ...totals, output: path.join(out,'index.html'), missing: characters.filter(c=>Object.values(c.directions).some(d=>!d.complete)).map(c=>({id:c.id,directions:Object.fromEntries(Object.entries(c.directions).filter(([k,d])=>!d.complete).map(([k,d])=>[k,d.available]))})) },null,2));
