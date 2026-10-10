/** Rebuild legacy server layers and HUD from staged v10 PNGs; never writes original assets. */
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const toolRoot = path.dirname(fileURLToPath(import.meta.url));
const pack = path.dirname(toolRoot), repo = path.dirname(pack), staged = path.join(pack, 'staged');
const args = process.argv.slice(2), require = createRequire(import.meta.url);
if (args.includes('--help')) {
  console.log('node build_composites.mjs [--sharp <installed sharp package>] [--check-inputs]\n'
    + 'Requires 39 new component PNGs in staged/qdao_ui_redesign_v5/components/png or derived/components.\n'
    + 'Writes only v10/staged: 12 server PNGs, 3 HUD PNGs, their SVGs and metadata, plus HUD preview.');
  process.exit(0);
}
const sharpIndex = args.indexOf('--sharp');
if (sharpIndex >= 0 && !args[sharpIndex + 1]) throw new Error('--sharp needs a package path');
let sharp;
for (const candidate of [sharpIndex >= 0 ? args[sharpIndex + 1] : null, 'sharp',
  path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp')].filter(Boolean)) {
  try { sharp = require(candidate); break; } catch {}
}
if (!sharp) throw new Error('Installed Sharp is required; no packages are downloaded.');
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const rel = p => path.relative(repo, p).replaceAll('\\', '/');
const readJson = async p => JSON.parse((await fs.readFile(p, 'utf8')).replace(/^\uFEFF/, ''));
const insideStage = relative => {
  const full = path.resolve(staged, relative);
  if (!full.startsWith(staged + path.sep)) throw new Error(`Unsafe staging path ${relative}`);
  return full;
};
async function writeStage(relative, data) {
  const full = insideStage(relative);
  await fs.mkdir(path.dirname(full), { recursive: true });
  await fs.writeFile(full, data);
  return full;
}
const writeJson = (relative, object) => writeStage(relative, JSON.stringify(object, null, 2) + '\n');
const componentContract = await readJson(path.join(pack, 'contracts/components.json'));
const layerContract = await readJson(path.join(pack, 'contracts/layers.json'));
const inventory = await readJson(path.join(pack, 'contracts/current_files.json'));
const baseline = new Map(inventory.files.map(item => [item.path, item]));
const layerDir = 'q_daoist_login_ui_uncropped_highres_final_layers';
const hudDir = 'qdao_ui_redesign_v5/hud';
const inputRoot = path.join(pack, 'contracts/composite-inputs');
const hudContract = await readJson(path.join(inputRoot, hudDir, 'placement.json'));
const embedded = /data:image\/png;base64,[A-Za-z0-9+/=]+/g;
const replacements = new Map(), componentSources = [], missing = [];

// Existing SVG geometry supplies exact pixel cuts and positions. Only its PNG paint changes.
for (const asset of componentContract.assets) {
  const candidates = [path.join(staged, 'qdao_ui_redesign_v5/components', asset.png),
    path.join(pack, 'derived/components', asset.id + '.png')];
  let candidate;
  for (const p of candidates) { try { await fs.access(p); candidate = p; break; } catch {} }
  if (!candidate) { missing.push(asset.id); continue; }
  const png = await fs.readFile(candidate), meta = await sharp(png).metadata();
  if (meta.width !== asset.width || meta.height !== asset.height || !meta.hasAlpha)
    throw new Error(`Wrong staged component contract: ${asset.id}`);
  const original = await fs.readFile(path.join(inputRoot, 'qdao_ui_redesign_v5/components', asset.svg), 'utf8');
  const oldUris = [...new Set(original.match(embedded) || [])];
  if (oldUris.length !== 1) throw new Error(`Expected one old PNG in ${asset.svg}; found ${oldUris.length}`);
  const newUri = 'data:image/png;base64,' + png.toString('base64');
  const prior = replacements.get(oldUris[0]);
  if (prior && prior.uri !== newUri) throw new Error(`Ambiguous embedded component mapping: ${prior.id}/${asset.id}`);
  replacements.set(oldUris[0], { id: asset.id, uri: newUri });
  componentSources.push({ id: asset.id, path: rel(candidate), sha256: sha(png), size: [meta.width, meta.height] });
}
if (missing.length) throw new Error('New component PNGs are not ready: ' + missing.join(', '));

function replacePaint(original, name) {
  const ids = new Set();
  let count = 0;
  const result = original.replace(embedded, oldUri => {
    const match = replacements.get(oldUri);
    if (!match) throw new Error(`Unknown old embedded PNG in ${name}; refusing to leave old paint`);
    count++; ids.add(match.id); return match.uri;
  });
  if (!count) throw new Error(`No replaceable component images in ${name}`);
  return { source: result, replacements: count, component_ids: [...ids] };
}
const transformed = {};
for (const name of ['base', 'controls']) {
  const original = await fs.readFile(path.join(inputRoot, layerDir, 'native_q5', name + '.svg'), 'utf8');
  transformed[name] = replacePaint(original, 'server/' + name);
  if (/<text\b/.test(transformed[name].source)) throw new Error(`Dynamic text in server ${name}`);
}
const labelsSource = await fs.readFile(path.join(inputRoot, layerDir, 'native_q5/labels.svg'), 'utf8');
for (const name of ['hud_skin', 'hud_overlay']) {
  const original = await fs.readFile(path.join(inputRoot, hudDir, name + '.svg'), 'utf8');
  transformed[name] = replacePaint(original, name);
}
if (/<text\b/.test(transformed.hud_skin.source)) throw new Error('Text in HUD skin');
const heroPath = path.join(inputRoot, 'qdao_chibi_game_pack_v4/hero-transparent_1024.png');
const cityPath = path.join(inputRoot, 'qdao_chibi_game_pack_v4/main-city_2560x1080.png');
const hudBackgroundPath = path.join(inputRoot, 'qdao_chibi_game_pack_v4/preview-main-city_2560x1080.png');
const sceneInputs = [];
for (const [p, role] of [[heroPath, 'existing_transparent_hero'], [cityPath, 'existing_server_city'],
  [hudBackgroundPath, 'existing_hud_city']]) {
  const bytes = await fs.readFile(p), metadata = await sharp(bytes).metadata();
  sceneInputs.push({ path: rel(p), sha256: sha(bytes), size: [metadata.width, metadata.height], role });
}
if (args.includes('--check-inputs')) {
  console.log(JSON.stringify({ status: 'inputs_ready', components: componentSources.length,
    embedded_replacements: Object.fromEntries(Object.entries(transformed).map(([k,v])=>[k,v.replacements])),
    expected_pngs: 15, stage: staged }));
  process.exit(0);
}

const render = (svg, width, height) => {
  const scaled = svg.replace(/<svg\b[^>]*>/, root => root
    .replace(/\bwidth="[^"]*"/, `width="${width}"`)
    .replace(/\bheight="[^"]*"/, `height="${height}"`));
  return sharp(Buffer.from(scaled)).png({ compressionLevel: 9 }).toBuffer();
};
const outputRecords = [];
async function savePng(relative, bytes, role, extra = {}) {
  const original = baseline.get(relative);
  if (!original) throw new Error(`PNG absent from frozen 158-file contract: ${relative}`);
  const metadata = await sharp(bytes).metadata(), stats = await sharp(bytes).stats();
  const mode = metadata.hasAlpha ? 'RGBA' : 'RGB';
  const alpha = metadata.hasAlpha ? [stats.channels[3].min, stats.channels[3].max] : null;
  if (metadata.width !== original.size[0] || metadata.height !== original.size[1]
      || mode !== original.mode || JSON.stringify(alpha) !== JSON.stringify(original.alpha_range))
    throw new Error(`Output pixel contract mismatch: ${relative}`);
  await writeStage(relative, bytes);
  outputRecords.push({ path: relative, role, size: original.size, mode, alpha_range: alpha,
    original_sha256: original.sha256, sha256: sha(bytes), ...extra });
}
for (const name of ['base', 'controls'])
  await writeStage(`${layerDir}/native_q5/${name}.svg`, transformed[name].source);
await writeStage(`${layerDir}/native_q5/labels.svg`, labelsSource);
const heroRect = layerContract.hero_placement_2560;
async function serverParts(width, height) {
  const scale = width / 2560;
  const base = await render(transformed.base.source, width, height);
  const hero = await sharp(heroPath).resize(Math.round(heroRect[2]*scale), Math.round(heroRect[3]*scale)).png().toBuffer();
  const baseWithHero = await sharp(base).composite([{ input: hero,
    left: Math.round(heroRect[0]*scale), top: Math.round(heroRect[1]*scale) }]).png({compressionLevel:9}).toBuffer();
  const controls = await render(transformed.controls.source, width, height);
  const combined = await sharp(baseWithHero).composite([{ input: controls }]).png({compressionLevel:9}).toBuffer();
  return { base: baseWithHero, controls, combined };
}
for (const [width, height] of [[5120,2160], [10240,4320]]) {
  const parts = await serverParts(width, height);
  for (const target of layerContract.outputs.filter(t => t.mode === 'RGBA' && t.size[0] === width)) {
    const role = target.role === 'transparent_ui_alias' ? 'combined' : target.role;
    await savePng(target.path, parts[role], target.role, { dynamic_text_baked: false });
  }
}
const page = await serverParts(2560, 1080);
const labels = await render(labelsSource, 2560, 1080);
const veil = Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1080"><rect width="2560" height="1080" fill="#EFF5DA" opacity=".25"/></svg>');
const screen = await sharp(cityPath).composite([{ input: veil }, { input: page.combined }, { input: labels }])
  .removeAlpha().png({ compressionLevel: 9 }).toBuffer();
for (const target of layerContract.outputs.filter(t => t.mode === 'RGB'))
  await savePng(target.path, screen, target.role, { dynamic_text_baked: true, production_data: false });
await writeJson(`${layerDir}/manifest_native_q5.json`, {
  ...layerContract, version: 'canonical-style-v10', date: new Date().toISOString().slice(0,10),
  source_builder: rel(fileURLToPath(import.meta.url)), staged_only: true,
  paint_source: 'New v10 common component PNGs; existing SVG positions/cuts retained',
  component_sources: componentSources, sources: sceneInputs,
  outputs: outputRecords.filter(r => baseline.get(r.path).family === 'layers'),
});

for (const name of ['hud_skin', 'hud_overlay']) {
  await writeStage(`${hudDir}/${name}.svg`, transformed[name].source);
  await savePng(`${hudDir}/${name}.png`, await render(transformed[name].source,2560,1080), name,
    { dynamic_text_baked: name === 'hud_overlay' });
}
await writeStage(`${hudDir}/hud_labels.svg`, await fs.readFile(path.join(inputRoot,hudDir,'hud_labels.svg')));
await savePng(`${hudDir}/hud_labels.png`, await fs.readFile(path.join(inputRoot,hudDir,'hud_labels.png')),
  'hud_labels', { unchanged_reason: 'Independent approved text layer is intentionally preserved' });
const overlay = await fs.readFile(insideStage(`${hudDir}/hud_overlay.png`));
const full = await sharp(hudBackgroundPath).composite([{input:overlay,left:0,top:0}])
  .removeAlpha().png({compressionLevel:9}).toBuffer();
await writeStage('qdao_ui_redesign_v5/source/04_main_city_hud.png', full);
const [beforeRaw, afterRaw, overlayRaw] = await Promise.all([
  sharp(hudBackgroundPath).removeAlpha().raw().toBuffer(), sharp(full).removeAlpha().raw().toBuffer(),
  sharp(overlay).ensureAlpha().raw().toBuffer()]);
let unchangedOutside = true;
for (let pixel=0; pixel<2560*1080; pixel++) {
  if (overlayRaw[pixel*4+3] === 0 && [0,1,2].some(channel => beforeRaw[pixel*3+channel] !== afterRaw[pixel*3+channel])) {
    unchangedOutside = false; break;
  }
}
if (!unchangedOutside) throw new Error('HUD preview changed scene pixels outside HUD');
await writeJson(`${hudDir}/placement.json`, {
  ...hudContract, version: 10, staged_only: true, source_builder: rel(fileURLToPath(import.meta.url)),
  source_component: componentSources.find(c=>c.id==='primary_button_normal'),
  source_background: sceneInputs.find(s=>s.role==='existing_hud_city'),
  validation: { exact_original_pixels_outside_overlay: unchangedOutside,
    layers: outputRecords.filter(r=>baseline.get(r.path).family==='hud') },
});
for (const source of [...sceneInputs, ...componentSources]) {
  if (sha(await fs.readFile(path.join(repo,source.path))) !== source.sha256)
    throw new Error(`Source input changed during build: ${source.path}`);
}
if (outputRecords.length !== 15) throw new Error(`Expected 15 PNG contracts; got ${outputRecords.length}`);
await writeJson('composite_build_report.json', {
  status: 'built', staged_only: true, built_at_utc: new Date().toISOString(), asset_count: outputRecords.length,
  source_builder: rel(fileURLToPath(import.meta.url)), component_sources: componentSources, scene_sources: sceneInputs,
  replacements: Object.fromEntries(Object.entries(transformed).map(([k,v])=>[k,{count:v.replacements,component_ids:v.component_ids}])),
  unchanged_scene_sources: true, unchanged_component_sources: true, exact_hud_pixels_outside_overlay: unchangedOutside, files: outputRecords,
  note: 'PNG dimensions/Alpha and HUD composition were verified; visual QA and engine integration are separate.'
});
const reviewSvg = Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1250">'
  + '<defs><pattern id="checker" width="24" height="24" patternUnits="userSpaceOnUse"><rect width="24" height="24" fill="#e2e0d1"/><path d="M0 0H12V12H0ZM12 12H24V24H12Z" fill="#ced4ca"/></pattern></defs>'
  + '<rect width="2560" height="1250" fill="#243c33"/>'
  + '<rect x="0" y="695" width="2560" height="540" fill="url(#checker)"/>'
  + '<g font-family="Arial,sans-serif" font-size="29" fill="#f2e2be">'
  + '<text x="20" y="40">v10 RECOMPOSED UI | new painted components, preserved native labels and scene art | Sharp QA</text>'
  + '<text x="20" y="88">SERVER SELECTION — demonstrative native text</text>'
  + '<text x="1300" y="88">MAIN CITY HUD — original scene pixels outside overlay</text>'
  + '<text x="20" y="677">SERVER BASE — no dynamic text</text>'
  + '<text x="1300" y="677">SERVER CONTROLS — no dynamic text</text>'
  + '</g></svg>');
const reviewImages = await Promise.all([screen, full, page.base, page.controls]
  .map(input => sharp(input).resize(1280,540).png().toBuffer()));
const review = await sharp(reviewSvg).composite(reviewImages.map((input,index)=>({input,
  left:(index%2)*1280,top:index<2?105:695}))).png({compressionLevel:9}).toBuffer();
await writeStage('composite-review.png',review);
console.log(JSON.stringify({ status:'built',stage:staged,png_contracts:outputRecords.length,
  unchanged_text_layer:'hud_labels.png', extra_hud_preview:true, scene_sources_unchanged:true }));
