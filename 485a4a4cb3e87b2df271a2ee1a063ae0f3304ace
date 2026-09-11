// Historical builder is retained for provenance; current UI publication is owned by v10.
if (!process.argv.includes('--check')) {
  console.error('Historical UI writes are disabled. From the repository root, follow qdao_ui_style_recut_v10/README.md: extract_art.py, build_common_legacy.py, build_attributes.py, build_composites.mjs, validate_staged.py, then publish_staged.py --apply.');
  process.exit(process.argv.includes('--help') ? 0 : 1);
}

/** Rebuild legacy Q UI assets in place. Node >=22 and the existing Sharp runtime. */
import fs from 'node:fs/promises';
// Windows viewers can briefly hold a generated asset while it is refreshed.
const rawWriteFile = fs.writeFile.bind(fs);
fs.writeFile = async (...params) => {
  for (let attempt=0;;attempt++) {
    try { return await rawWriteFile(...params); }
    catch (error) {
      if (attempt>=12 || !['UNKNOWN','EBUSY','EPERM'].includes(error.code)) throw error;
      await new Promise(resolve=>setTimeout(resolve,250));
    }
  }
};

import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
const exact = path.dirname(fileURLToPath(import.meta.url));
const repo = path.dirname(exact);
const atomic = path.join(repo, 'q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic');
const components = path.join(repo, 'qdao_ui_redesign_v5/components');
const require = createRequire(import.meta.url);
const args = process.argv.slice(2);
const sharpAt = args.indexOf('--sharp');
const sharp = require(sharpAt >= 0 ? args[sharpAt + 1] : path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp'));
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
const relative = file => path.relative(repo, file).replaceAll('\\', '/');
const specPath = path.join(exact, 'manifest_native_q5.json');
let prior = { assets: [] };
try { prior = JSON.parse(await fs.readFile(specPath, 'utf8')); } catch (e) { if (e.code !== 'ENOENT') throw e; }
if (args.includes('--check')) {
  if (!prior.assets.length) throw new Error('Build manifest does not exist.');
  for (const a of prior.assets) {
    const file = path.join(repo, a.png), data = await fs.readFile(file), meta = await sharp(data).metadata();
    if (hash(data) !== a.png_sha256 || meta.width !== a.width || meta.height !== a.height || !meta.hasAlpha) throw new Error(`Asset mismatch: ${a.png}`);
    if (hash(await fs.readFile(path.join(repo, a.svg))) !== a.svg_sha256) throw new Error(`SVG mismatch: ${a.svg}`);
  }
  console.log(JSON.stringify({ passed: true, files: prior.assets.length, dimensions_alpha_hashes: true }));
  process.exit(0);
}
const defs = `<defs><linearGradient id="legacy_jade" x2="0" y2="1"><stop stop-color="#438E78"/><stop offset=".52" stop-color="#287660"/><stop offset="1" stop-color="#176C5F"/></linearGradient><linearGradient id="legacy_ivory" x2="0" y2="1"><stop stop-color="#FFFBEF"/><stop offset="1" stop-color="#F3E7CB"/></linearGradient><linearGradient id="legacy_gold" x2="0" y2="1"><stop stop-color="#F3DE9C"/><stop offset=".45" stop-color="#C59645"/><stop offset="1" stop-color="#9E7037"/></linearGradient><linearGradient id="legacy_wood" x2="0" y2="1"><stop stop-color="#9A7350"/><stop offset="1" stop-color="#68462E"/></linearGradient><linearGradient id="legacy_red" x2="0" y2="1"><stop stop-color="#E96D51"/><stop offset="1" stop-color="#A43831"/></linearGradient></defs>`;
const xml = (w, h, body, title, vw = w, vh = h) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${vw} ${vh}" preserveAspectRatio="none" role="img"><title>五行奇谈 ${title}</title>${defs}${body}</svg>`;
const rect = (x,y,w,h,r,fill,stroke='none',sw=0,extra='') => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" ${extra}/>`;
function skin(w, h, active, grid, search = false) {
  const [left, top, cw, ch] = grid, right = w-left-cw, bottom=h-top-ch;
  // Curved geometry is contained by the existing four fixed grid corners.
  const r = Math.max(6,Math.min(22,left-10,right-10,top-8,bottom-8));
  let body = rect(4,7,w-8,h-10,r,'#503C2B','none',0,'opacity=".15"');
  body += rect(3,4,w-6,h-10,r,'url(#legacy_wood)');
  body += rect(3,3,w-6,h-11,r,'url(#legacy_gold)');
  body += rect(6,6,w-12,h-17,Math.max(3,r-3),active?'url(#legacy_jade)':'url(#legacy_ivory)','#8D672F',1);
  body += rect(10,10,w-20,h-25,Math.max(2,r-7),'none',active?'#D9C790':'#CFB57F',1.2);
  body += `<path d="M${r+5} 7H${w-r-5}" fill="none" stroke="#FFFADE" stroke-width="1.6" opacity=".75" stroke-linecap="round"/>`;
  if (search) body += `<g fill="none" stroke="#795638" stroke-width="3" stroke-linecap="round"><circle cx="${Math.min(32,left/2)}" cy="${h/2-4}" r="8"/><path d="m${Math.min(32,left/2)+6} ${h/2+2} 7 7"/></g>`;
  return body;
}
const redStatus = `<circle cx="16" cy="18" r="13" fill="#503C2B" opacity=".15"/><circle cx="16" cy="16" r="13" fill="url(#legacy_gold)"/><circle cx="16" cy="16" r="10" fill="url(#legacy_red)" stroke="#873930" stroke-width=".7"/><path d="M16 10v7m0 4v.1" stroke="#FFF7DE" stroke-width="2.5" stroke-linecap="round"/>`;
const coreBody = source => source.replace(/^<svg[^>]*>/,'').replace(/<\/svg>\s*$/,'');
const badgeBodies = {};
for (const symbol of ['taiji','pagoda','furnace','mountain','lotus','sword','water','compass','peach_spirit','flame']) badgeBodies[symbol] = coreBody(await fs.readFile(path.join(components,`svg/round_badge_${symbol}.svg`),'utf8'));
const flowerBody = coreBody(await fs.readFile(path.join(components,'svg/gold_flower.svg'),'utf8'));
const place = (body, x, y, w, h, vb = '0 0 120 120') => `<svg x="${x}" y="${y}" width="${w}" height="${h}" viewBox="${vb}">${body}</svg>`;
const assets = [];
async function emit(dir, file, w, h, body, info = {}, vw = w, vh = h) {
  const dest = path.join(dir,file), key=relative(dest), priorAsset=prior.assets.find(a=>a.png===key);
  let original = priorAsset?.original;
  if (!original) {
    try { const bytes=await fs.readFile(dest),m=await sharp(bytes).metadata(); original={ existed:true, dimensions:[m.width,m.height], mode:m.hasAlpha?'RGBA':'RGB', sha256:hash(bytes) }; }
    catch(e) { if(e.code!=='ENOENT')throw e; original={existed:false,dimensions:[w,h],reason:'Previously referenced in the legacy manifest but missing from disk.'}; }
  }
  if(original.existed&&(original.dimensions[0]!==w||original.dimensions[1]!==h)) throw new Error(`Original dimensions changed: ${file}`);
  // New v7 AI painting; logical SVG viewBox and physical canvas remain intact.
  const painted=await fs.readFile(path.join(repo,'qdao_gpt_image2_refresh_v7/ui/derived/legacy',file));
  body=`<image x="0" y="0" width="${vw}" height="${vh}" href="data:image/png;base64,${painted.toString('base64')}"/>`;
  const source=xml(w,h,body,file,vw,vh), svgFile=path.join(dir,'svg_q5',file.replace(/\.png$/,'.svg'));
  await fs.mkdir(path.dirname(svgFile),{recursive:true});
  await fs.writeFile(svgFile,source,'utf8');
  await fs.writeFile(dest, await sharp(Buffer.from(source)).png({compressionLevel:9}).toBuffer());
  const rendered=await fs.readFile(dest), meta=await sharp(rendered).metadata(), stats=await sharp(rendered).stats();
  if(meta.width!==w||meta.height!==h||!meta.hasAlpha||stats.channels[3].min!==0||stats.channels[3].max!==255) throw new Error(`RGBA validation failed: ${file}`);
  assets.push({png:key,svg:relative(svgFile),width:w,height:h,original,authoring:'New built-in image_gen v7 artwork; alpha cleanup and fixed-border resampling; embedded portable PNG in SVG.',v7_source_map:'qdao_gpt_image2_refresh_v7/ui/source-map.json',dynamic_text_baked:false,alpha_range:[0,255],...info,png_sha256:hash(rendered),svg_sha256:hash(Buffer.from(source))});
}
const exactSkin = async (name,w,h,active,grid,role,search=false) => emit(exact,name,w,h,skin(w,h,active,grid,search),{role,state:active?'selected':'normal',round_badge_baked:false,status_baked:false,nine_slice:{basis:'New safe grid; no prior numeric grid exists in this asset repository.',center_xywh:grid},resize_axes:search?'horizontal':'both',fixed_height:search?h:null});
await exactSkin('fx_top_tab_active.png',260,76,true,[48,22,164,32],'tab');
await exactSkin('fx_top_tab_idle_mid.png',300,66,false,[48,20,204,26],'tab');
await exactSkin('fx_top_tab_idle_right.png',344,66,false,[48,20,248,26],'tab');
await exactSkin('fx_left_row_active.png',240,65,true,[38,19,164,27],'list_row');
for(let i=1;i<=4;i++)await exactSkin(`fx_left_row_idle_${i}.png`,240,65,false,[38,19,164,27],'list_row');
await exactSkin('fx_search_box.png',250,61,false,[48,18,152,25],'search',true);
await exactSkin('fx_bottom_bar.png',1250,180,false,[65,32,1120,116],'summary_bar');
const exactSymbols=['pagoda','taiji','furnace','mountain','sword','peach_spirit','water','compass'];
for(let i=0;i<8;i++) {
  for(const suffix of ['', '_base'])await exactSkin(`fx_server_card_${i}${suffix}.png`,473,100,false,[48,25,377,50],'server_card_base');
  await emit(exact,`fx_server_card_${i}_badge.png`,116,100,place(badgeBodies[exactSymbols[i]],8,0,100,100),{role:'round_badge',symbol:exactSymbols[i],nine_slice:null,resize_axes:'uniform',card_baked:false});
  await emit(exact,`fx_server_card_${i}_dot.png`,47,46,place(redStatus,3.5,3,40,40,'0 0 32 32'),{role:'status_dot',status_color:'red',nine_slice:null,resize_axes:'uniform',semantics:'Legacy red marker preserved; client supplies actual state meaning and label.'});
  await emit(exact,`fx_server_card_${i}_stroke.png`,142,35,`<path d="M8 17.5h48m30 0h48" fill="none" stroke="#C59645" stroke-width="2.4" stroke-linecap="round"/><path d="m60 17.5 11-5 11 5-11 5z" fill="#E8D197" stroke="#C59645" stroke-width="1"/>`,{role:'decorative_divider',nine_slice:null,resize_axes:'uniform',replaces:'Old gray paint-over mark; new clean gold divider is decorative, not text.'});
}
// Existing import metadata is copied exactly; logical coordinates match the legacy UI_PIECES target.
const atomicSpecs=[
['top_button_green_selected.png',1391,441,360,114,[44,28,272,58],true,false,'tab_button_green_active_v3.png'],
['list_bg_unselected.png',1419,380,360,96,[40,22,280,52],false,false,'list_row_idle_v3.png'],
['list_bg_selected_green.png',1419,380,360,96,[40,22,280,52],true,false,'list_row_active_v3.png'],
['server_card_bg_wide.png',2606,574,640,141,[60,30,520,80],false,false,'server_card_wide_idle_v3.png'],
['server_card_bg_wide_selected_green.png',2606,574,640,141,[60,30,520,80],true,false,'server_card_wide_active_v3.png'],
['server_card_bg_medium.png',2364,574,520,126,[60,30,400,66],false,false,'server_card_med_idle_v3.png'],
['server_card_bg_medium_selected_green.png',2364,574,520,126,[60,30,400,66],true,false,'server_card_med_active_v3.png'],
['bottom_bar_bg_green_white.png',6679,413,1280,79,[60,16,1160,48],false,false,'bottom_bar_v3.png'],
['search_box_with_icon.png',1428,285,420,84,[60,20,280,44],false,true,'search_box_with_icon_v3.png']
];
for(const [name,w,h,tw,th,grid,active,search,target] of atomicSpecs)await emit(atomic,name,w,h,skin(tw,th,active,grid,search),{role:search?'search':'control_base',state:active?'selected':'normal',round_badge_baked:false,status_baked:false,legacy_import:{target_name:target,target_size:[tw,th],scale:'9grid',scale9grid_center_xywh:grid,source:'wire_qdao_v3_assets.py:UI_PIECES'},source_grid_center_xywh:[grid[0]*w/tw,grid[1]*h/th,grid[2]*w/tw,grid[3]*h/th],resize_axes:search?'horizontal':'both',fixed_target_height:search?th:null},tw,th);
await emit(atomic,'status_red_dot.png',128,128,redStatus,{role:'status_dot',status_color:'red',nine_slice:null,resize_axes:'uniform',legacy_import:{target_name:'status_red_dot_v3.png',target_size:[32,32],scale9grid_center_xywh:null}},32,32);
await emit(atomic,'ornament_gold_flower.png',360,360,flowerBody,{role:'ornament',nine_slice:null,resize_axes:'uniform',legacy_import:{target_name:'ornament_gold_flower_v3.png',target_size:[120,120],scale9grid_center_xywh:null}},120,120);
const iconNames={taiji:'icon_yin_yang.png',pagoda:'icon_pagoda.png',furnace:'icon_cauldron.png',mountain:'icon_mountain.png',lotus:'icon_lotus.png',sword:'icon_sword.png',water:'icon_water.png',compass:'icon_compass.png',peach_spirit:'icon_peach_spirit.png',flame:'icon_fire.png'};
for(const [symbol,file] of Object.entries(iconNames))await emit(atomic,file,420,420,badgeBodies[symbol],{role:'round_badge',symbol,nine_slice:null,resize_axes:'uniform',v5_source:`qdao_ui_redesign_v5/components/svg/round_badge_${symbol}.svg`},120,120);
await emit(atomic,'icon_leaf.png',420,420,badgeBodies.peach_spirit,{role:'legacy_alias',symbol:'peach_spirit',alias_of:'icon_peach_spirit.png',nine_slice:null,resize_axes:'uniform'},120,120);
const cells=JSON.parse(await fs.readFile(path.join(atomic,'manifest_ai_qstyle_badges.json'),'utf8')).outputs;
let sheet='';
for(const [i,symbol] of Object.keys(iconNames).entries()) { const [x,y,w,h]=cells[i].source_cell; sheet+=place(badgeBodies[symbol],x+(w-328)/2,y+(h-328)/2,328,328); }
await emit(atomic,'ai_qstyle_badges_sheet_chroma.png',1774,887,sheet,{role:'badge_sheet',symbols:Object.keys(iconNames),nine_slice:null,legacy_filename_note:'Kept for compatibility; background now has real Alpha rather than chroma green.',source_cells_preserved:true,legacy_import:{target_name:'badges_chroma_sheet_v3.png',target_size:[1024,512],scale9grid_center_xywh:null,disableTrim:true}});
const manifest={product:'五行奇谈',version:'gpt-image2-q7',date:'2026-09-07',asset_count:assets.length,exact_slice_count:50,atomic_control_count:11,round_symbol_count:10,round_symbol_alias_count:1,badge_sheet_count:1,renderer:{sharp:sharp.versions.sharp,vips:sharp.versions.vips},source_builder:relative(fileURLToPath(import.meta.url)),scope:'Replaces all 50 exact slices and all 11 atomic UI controls in place, fills 10 missing 420px symbols and one legacy alias, replaces the badge sheet at its original dimensions.',nine_slice_note:'Existing atomic UI_PIECES target dimensions and center xywh values are preserved exactly. Exact slices had no numeric grid metadata; new safe grids are explicitly marked. Search magnifiers keep fixed target height. Round icons, statuses, ornaments and dividers scale uniformly.',client_note:'Artwork and metadata only. No unknown client directory was read or modified. Server state meanings and dynamic text belong to the client.',assets};
await fs.writeFile(specPath,JSON.stringify(manifest,null,2)+'\n','utf8');
await fs.writeFile(path.join(atomic,'manifest_native_q5.json'),JSON.stringify({...manifest,assets:assets.filter(a=>a.png.startsWith(relative(atomic)+'/')),asset_count:23,exact_slice_count:0,full_manifest:'../../exact_qdao_slices/manifest_native_q5.json'},null,2)+'\n','utf8');
await fs.writeFile(path.join(atomic,'manifest_redrawn.json'),JSON.stringify({product:'五行奇谈',version:'gpt-image2-q7',backgrounds:atomicSpecs.map(s=>s[0]),status:['status_red_dot.png'],ornaments:['ornament_gold_flower.png'],round_icons:Object.values(iconNames),aliases:{'icon_leaf.png':'icon_peach_spirit.png'},notes:'All PNGs have real Alpha. Backgrounds contain no text, status dot or round badge. The search magnifier remains part of the fixed-height search asset.',native_manifest:'manifest_native_q5.json'},null,2)+'\n','utf8');
await fs.writeFile(path.join(atomic,'manifest_ai_qstyle_badges.json'),JSON.stringify({source_sheet:'ai_qstyle_badges_sheet_chroma.png',authoring:'New built-in image_gen v7 emblems; true-alpha atlas at legacy coordinates.',native_dimensions:[1774,887],transparent:true,outputs:cells.map((cell,i)=>({...cell,file:Object.values(iconNames)[i],normalized_size:[420,420],symbol:Object.keys(iconNames)[i]})),aliases:{'icon_leaf.png':'icon_peach_spirit.png'}},null,2)+'\n','utf8');
console.log(JSON.stringify({assets:assets.length,exact:50,atomic_controls:11,round_symbols:10,alias:1,badge_sheet:1,validation:'RGBA, exact dimensions, SHA-256'}));
