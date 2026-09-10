/** Render approved SVG-derived PNG candidates into staging; never overwrite inputs.
 * Usage: node render_svg_pairs.mjs --mapping mapping.json [--check]
 *        [--report report.json] [--ids comma,separated] [--sharp installed-directory]
 * Mapping: {root?:path, pairs:[{id,svg,png,output,width?,height?,overlays?:[
 *   {png|svg,left?,top?,width?,height?}
 * ]}]}. Paths resolve against root (default: this repository). SVG viewBox stays
 * fixed while its root width/height is set to the target PNG's actual dimensions.
 * Overlays are composited sequentially, matching the existing layer builder.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const args = process.argv.slice(2);
const arg = (name, fallback = null) => {
  const at = args.indexOf(name);
  if (at < 0) return fallback;
  if (!args[at + 1] || args[at + 1].startsWith('--')) throw new Error(`${name} needs a value`);
  return args[at + 1];
};
if (args.includes('--help')) {
  console.log('node render_svg_pairs.mjs --mapping mapping.json [--check] [--report report.json] [--ids id,id] [--sharp package-directory]\n--check renders and compares in memory only; regular mode writes only each staging output. Original alpha and RGB under alpha=0 are retained.');
  process.exit(0);
}
const defaultRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const mappingPath = path.resolve(arg('--mapping', path.join(defaultRoot, 'qdao_exposure_refinement_v8/svg_raster_pairs.json')));
const mapping = JSON.parse(await fs.readFile(mappingPath, 'utf8'));
const root = path.resolve(mapping.root ?? defaultRoot);
const stagingRoot = path.join(root, 'qdao_exposure_refinement_v8');
const absolute = value => path.isAbsolute(value) ? path.resolve(value) : path.resolve(root, value);
const normalized = value => path.resolve(value).toLowerCase();
const within = (target, parent) => {
  const relative = path.relative(parent, target);
  return relative !== '' && relative !== '..' && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative);
};
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
let sharp;
for (const candidate of [arg('--sharp'), 'sharp', path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp')].filter(Boolean)) {
  try { sharp = require(candidate); break; } catch {}
}
if (!sharp) throw new Error('Installed sharp not found; pass --sharp. No packages are installed by this script.');
sharp.cache(false);
const checkOnly = args.includes('--check');
const ids = arg('--ids')?.split(',');
const pairs = mapping.pairs.filter(pair => !ids || ids.includes(pair.id));
if (!pairs.length) throw new Error('No mapping pairs selected');
const protectedInputs = new Set(mapping.pairs.flatMap(pair => [pair.svg, pair.png, ...(pair.overlays ?? []).map(layer => layer.svg ?? layer.png)]).filter(Boolean).map(value => normalized(absolute(value))));
const outputPaths = new Set();
for (const pair of pairs) {
  if (!pair.svg || !pair.png || !pair.output) throw new Error('Each pair requires svg, png, output');
  const output = absolute(pair.output);
  if (!within(output, stagingRoot) || protectedInputs.has(normalized(output))) throw new Error(`Output must be in refinement staging and cannot overwrite an input: ${output}`);
  if (outputPaths.has(normalized(output))) throw new Error(`Duplicate output: ${output}`);
  outputPaths.add(normalized(output));
}

function sizeSvg(source, width, height) {
  let found = false;
  const result = source.replace(/<svg\b[^>]*>/, tag => {
    found = true;
    for (const [name, value] of [['width', width], ['height', height]]) {
      const attribute = new RegExp(`\\b${name}\\s*=\\s*(["'])[^"']*\\1`);
      if (!attribute.test(tag)) throw new Error(`SVG root missing ${name}`);
      tag = tag.replace(attribute, `${name}="${value}"`);
    }
    return tag;
  });
  if (!found) throw new Error('SVG root not found');
  return result;
}

async function svgPng(filename, width, height) {
  const source = await fs.readFile(absolute(filename), 'utf8');
  return sharp(Buffer.from(sizeSvg(source, width, height))).png({ compressionLevel: 9 }).toBuffer();
}

async function render(pair, width, height) {
  let output = await svgPng(pair.svg, width, height);
  for (const layer of pair.overlays ?? []) {
    let overlay;
    if (layer.svg) {
      overlay = await svgPng(layer.svg, layer.width ?? width, layer.height ?? height);
    } else if (layer.png) {
      let raster = sharp(await fs.readFile(absolute(layer.png)));
      if (layer.width || layer.height) raster = raster.resize(layer.width, layer.height);
      overlay = await raster.png().toBuffer();
    } else throw new Error('Overlay requires svg or png');
    output = await sharp(output).composite([{ input: overlay, left: layer.left ?? 0, top: layer.top ?? 0 }]).png({ compressionLevel: 9 }).toBuffer();
  }
  return output;
}

const results = [];
for (const pair of pairs) {
  const originalBytes = await fs.readFile(absolute(pair.png));
  const originalMeta = await sharp(originalBytes).metadata();
  const width = pair.width ?? originalMeta.width, height = pair.height ?? originalMeta.height;
  if (width !== originalMeta.width || height !== originalMeta.height) throw new Error(`Mapping dimensions disagree with target PNG: ${pair.png}`);
  const renderedBytes = await render(pair, width, height);
  const { data: original, info: originalInfo } = await sharp(originalBytes).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  const { data: rendered, info: renderedInfo } = await sharp(renderedBytes).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  if (renderedInfo.width !== width || renderedInfo.height !== height || originalInfo.channels !== 4 || renderedInfo.channels !== 4) throw new Error(`Render size/channels mismatch: ${pair.id}`);
  let alphaDifferent = 0, rgbDifferent = 0, visibleRgbDifferent = 0, hiddenRgbDifferent = 0, rgbAbsDiff = 0, maxChannelDifference = 0;
  for (let offset = 0; offset < original.length; offset += 4) {
    const alpha = original[offset + 3];
    if (alpha !== rendered[offset + 3]) alphaDifferent++;
    let changed = false;
    for (let channel = 0; channel < 3; channel++) {
      const difference = Math.abs(original[offset + channel] - rendered[offset + channel]);
      rgbAbsDiff += difference;
      maxChannelDifference = Math.max(maxChannelDifference, difference);
      changed ||= difference !== 0;
    }
    if (changed) {
      rgbDifferent++;
      if (alpha === 0) hiddenRgbDifferent++; else visibleRgbDifferent++;
    }
    // The original target is the transparency contract, including invisible RGB.
    rendered[offset + 3] = alpha;
    if (alpha === 0) original.copy(rendered, offset, offset, offset + 3);
  }
  let savedBytes = null;
  if (!checkOnly) {
    let output = sharp(rendered, { raw: { width, height, channels: 4 } });
    if (!originalMeta.hasAlpha) output = output.removeAlpha();
    savedBytes = await output.png({ compressionLevel: 9 }).toBuffer();
    const outputPath = absolute(pair.output);
    await fs.mkdir(path.dirname(outputPath), { recursive: true });
    await fs.writeFile(outputPath, savedBytes);
  }
  const result = {
    id: pair.id, svg: pair.svg, png: pair.png, output: pair.output,
    dimensions: [width, height], original_has_alpha: originalMeta.hasAlpha,
    original_sha256: hash(originalBytes), raw_render_sha256: hash(renderedBytes),
    raw_render_alpha_different_pixels: alphaDifferent,
    raw_render_rgb_different_pixels: rgbDifferent,
    raw_render_visible_rgb_different_pixels: visibleRgbDifferent,
    raw_render_hidden_rgb_different_pixels: hiddenRgbDifferent,
    raw_render_mean_abs_rgb_difference: rgbAbsDiff / (width * height * 3),
    raw_render_max_channel_difference: maxChannelDifference,
    raw_render_exact_pixels: alphaDifferent === 0 && rgbDifferent === 0,
    original_alpha_and_hidden_rgb_preserved_in_output: !checkOnly,
    output_sha256: savedBytes ? hash(savedBytes) : null,
    output_written: !checkOnly,
  };
  results.push(result);
  console.log(JSON.stringify(result));
}
const report = { schema: 'qdao.svg.render_comparison.v1', check_only: checkOnly, renderer: sharp.versions, pair_count: results.length, results };
const reportArg = arg('--report');
if (reportArg) {
  const reportPath = absolute(reportArg);
  if (!within(reportPath, stagingRoot) || protectedInputs.has(normalized(reportPath))) throw new Error('Report must be inside refinement staging and cannot overwrite an input');
  await fs.mkdir(path.dirname(reportPath), { recursive: true });
  await fs.writeFile(reportPath, JSON.stringify(report, null, 2) + '\n');
}
