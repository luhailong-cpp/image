// Historical builder is retained for provenance; current UI publication is owned by v10.
{
  console.error('Historical UI writes are disabled. From the repository root, follow qdao_ui_style_recut_v10/README.md: extract_art.py, build_common_legacy.py, build_attributes.py, build_composites.mjs, validate_staged.py, then publish_staged.py --apply.');
  process.exit(process.argv.includes('--help') ? 0 : 1);
}

/** Original-path high-resolution server-selection layers; uses approved v4/v5 art. */
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
const nativeRoot=path.dirname(fileURLToPath(import.meta.url)), layerRoot=path.dirname(nativeRoot), repo=path.dirname(layerRoot);
const require=createRequire(import.meta.url), args=process.argv.slice(2), at=args.indexOf('--sharp');
const sharp=require(at>=0?args[at+1]:path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex'), rel=p=>path.relative(repo,p).replaceAll('\\','/');
const copy=JSON.parse(await fs.readFile(path.join(repo,'qdao_ui_redesign_v5/copy.zh-CN.json'),'utf8'));
const cm=JSON.parse(await fs.readFile(path.join(repo,'qdao_ui_redesign_v5/components/manifest.json'),'utf8'));
const audit=JSON.parse(await fs.readFile(path.join(repo,'docs/ART_ASSET_AUDIT.json'),'utf8'));
const targets=audit.assets.filter(a=>['legacy_screen_7','login_layers_6'].includes(a.family));
if(targets.length!==12)throw new Error('Expected exactly 12 assigned baseline files.');
const map=new Map(cm.assets.map(a=>[a.id,a]));
const body=new Map();
for(const a of cm.assets)body.set(a.id,(await fs.readFile(path.join(repo,'qdao_ui_redesign_v5/components',a.svg),'utf8')).replace(/^<svg[^>]*>/,'').replace(/<\/svg>\s*$/,''));
const rootSvg=b=>`<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1080" viewBox="0 0 2560 1080" role="img">${b}</svg>`;
const simple=(id,x,y,w,h)=>`<svg x="${x}" y="${y}" width="${w}" height="${h}" viewBox="0 0 ${map.get(id).width} ${map.get(id).height}" overflow="hidden">${body.get(id)}</svg>`;
const placements=[];
function patch(id,x,y,w,h,role) {
 const a=map.get(id), n=a.nine_slice;
 placements.push({id,role,rect:[x,y,w,h],source_size:[a.width,a.height],source_nine_slice:n,resize_axes:a.resize_axes??'uniform'});
 if(!n)return simple(id,x,y,w,h);
 const scale=a.resize_axes==='horizontal'?h/a.height:1;
 const sx=[0,n.left,a.width-n.right,a.width],sy=[0,n.top,a.height-n.bottom,a.height];
 // Integer destination cuts prevent nested SVG clip antialias seams.
 const dx=[x,Math.round(x+n.left*scale),Math.round(x+w-n.right*scale),x+w],dy=[y,Math.round(y+n.top*scale),Math.round(y+h-n.bottom*scale),y+h];
 let out='';
 for(let r=0;r<3;r++)for(let c=0;c<3;c++)out+=`<svg x="${dx[c]}" y="${dy[r]}" width="${dx[c+1]-dx[c]}" height="${dy[r+1]-dy[r]}" viewBox="${sx[c]} ${sy[r]} ${sx[c+1]-sx[c]} ${sy[r+1]-sy[r]}" preserveAspectRatio="none" overflow="hidden">${body.get(id)}</svg>`;
 return out;
}
const textNodes=[];
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
function txt(x,y,value,size=28,color='#344D43',weight=400,anchor='start',source='') {
 textNodes.push({text:value,x,y,font_size:size,color,font_weight:weight,anchor,source});
 return `<text x="${x}" y="${y}" font-family="Microsoft YaHei,Noto Sans CJK SC,sans-serif" font-size="${size}" font-weight="${weight}" text-anchor="${anchor}" fill="${color}">${esc(value)}</text>`;
}
let base=patch('main_frame',300,176,1960,820,'decorative_frame');
base+=patch('primary_button_normal',360,218,1750,98,'header_plaque');
base+=simple('round_badge_taiji',286,109,120,120)+simple('round_badge_furnace',260,838,116,116)+simple('gold_flower',2190,909,118,118);
base+=simple('cloud_corner',276,176,90,90);
let controls='',labels='';
labels+=txt(430,139,copy.product.title,54,'#176C5F',700,'start','product.title');
labels+=txt(401,280,copy.pages.serverSelect.title,38,'#FFF7DE',700,'start','pages.serverSelect.title');
controls+=patch('search_normal',362,347,350,70,'search');
labels+=txt(426,392,copy.pages.serverSelect.searchPlaceholder,24,'#795638',400,'start','pages.serverSelect.searchPlaceholder');
for(const [i,c]of copy.pages.serverSelect.categories.entries()) {
 const y=444+i*104,selected=c.id==='all';
 controls+=patch(`list_row_${selected?'selected':'normal'}`,362,y,350,80,'category');
 labels+=txt(445,y+49,c.label,28,selected?'#FFF7DE':'#344D43',selected?700:400,'start',`pages.serverSelect.categories[${i}].label`);
}
const symbols=['pagoda','taiji','furnace','mountain','sword','peach_spirit','water','compass'];
for(const [i,s]of copy.demoData.servers.entries()) {
 const x=758+(i%2)*710,y=350+Math.floor(i/2)*130,selected=s.id===copy.demoData.selectedServerId,state=s.status==='maintenance'?'disabled':selected?'selected':'normal',color=selected?'#FFF7DE':state==='disabled'?'#536254':'#344D43';
 controls+=patch(`server_card_wide_${state}`,x,y,660,114,'server_card');
 controls+=simple(`round_badge_${symbols[i]}`,x+548,y+12,90,90);
 const dot=s.status==='smooth'?'green':s.status==='busy'?'orange':'gray';
 controls+=simple(`status_dot_${dot}`,x+80,y+73,22,22);
 labels+=txt(x+77,y+47,s.name,31,color,700,'start',`demoData.servers[${i}].name`);
 labels+=txt(x+112,y+91,copy.serverStatusLabels[s.status],22,color,400,'start',`serverStatusLabels.${s.status}`);
 if(selected)labels+=txt(x+420,y+91,copy.common.selected,20,color,400,'start','common.selected');
 if(s.recommended) { controls+=simple('recommend_badge',x+424,y+16,90,37.5); labels+=txt(x+468,y+42,copy.common.recommended,18,'#674B2F',700,'middle','common.recommended'); }
}
controls+=patch('summary_bar',360,894,1220,79,'selection_summary');
const selectedServer=copy.demoData.servers.find(s=>s.id===copy.demoData.selectedServerId);
labels+=txt(398,943,copy.pages.serverSelect.selectionTemplate.replace('{serverName}',selectedServer.name),28,'#344D43',400,'start','pages.serverSelect.selectionTemplate + demoData.selectedServerId');
controls+=patch('list_row_normal',1620,899,210,72,'back');
controls+=patch('primary_button_normal',1850,896,320,78,'continue');
labels+=txt(1725,945,copy.pages.serverSelect.actions.back,28,'#344D43',700,'middle','pages.serverSelect.actions.back');
labels+=txt(2010,946,copy.pages.serverSelect.actions.continue,30,'#FFF7DE',700,'middle','pages.serverSelect.actions.continue');
const sources={base:rootSvg(base),controls:rootSvg(controls),labels:rootSvg(labels)};
for(const [key,value]of Object.entries(sources))await fs.writeFile(path.join(nativeRoot,`${key}.svg`),value,'utf8');
const heroPath=path.join(repo,'qdao_chibi_game_pack_v4/hero-transparent_1024.png');
const cityPath=path.join(repo,'qdao_chibi_game_pack_v4/main-city_2560x1080.png');
const heroRect=[2042,30,310,310];
const render=(source,w,h)=>sharp(Buffer.from(source.replace('width="2560" height="1080"',`width="${w}" height="${h}"`))).png({compressionLevel:9}).toBuffer();
const cache=new Map();
async function layers(w,h) {
 const key=`${w}x${h}`;if(cache.has(key))return cache.get(key);
 const scale=w/2560,vector=await render(sources.base,w,h),hero=await sharp(heroPath).resize(Math.round(heroRect[2]*scale),Math.round(heroRect[3]*scale)).png().toBuffer();
 const basePng=await sharp(vector).composite([{input:hero,left:Math.round(heroRect[0]*scale),top:Math.round(heroRect[1]*scale)}]).png({compressionLevel:9}).toBuffer();
 const controlsPng=await render(sources.controls,w,h);
 const combined=await sharp(basePng).composite([{input:controlsPng}]).png({compressionLevel:9}).toBuffer();
 const result={base:basePng,controls:controlsPng,combined};cache.set(key,result);return result;
}
const outputRecords=[];
async function save(target,bytes,role,extra={}) {
 const dest=path.join(repo,target.path),meta=await sharp(bytes).metadata();
 if(meta.width!==target.size[0]||meta.height!==target.size[1])throw new Error(`Wrong dimensions ${target.path}`);
 const stats=await sharp(bytes).stats();
 if(target.mode==='RGBA'&&(!meta.hasAlpha||stats.channels[3].min!==0||stats.channels[3].max!==255))throw new Error(`Wrong Alpha ${target.path}`);
 for(let attempt=0;;attempt++){try{await fs.writeFile(dest,bytes);break;}catch(e){if(attempt>=8||!['UNKNOWN','EBUSY','EPERM'].includes(e.code))throw e;await new Promise(resolve=>setTimeout(resolve,250));}}
 outputRecords.push({path:target.path,role,size:target.size,mode:meta.hasAlpha?'RGBA':'RGB',alpha_range:meta.hasAlpha?[stats.channels[3].min,stats.channels[3].max]:null,original_sha256:target.baseline_sha256,sha256:sha(bytes),...extra});
}
for(const size of [[5120,2160],[10240,4320]]) {
 const [w,h]=size,parts=await layers(w,h);
 for(const t of targets.filter(t=>t.family==='login_layers_6'&&t.size[0]===w)) {
  const role=t.path.includes('background_ui')?'base':t.path.includes('buttons_uncropped')?'controls':'combined';
  await save(t,parts[role],role,{dynamic_text_baked:false,composition:role==='combined'?'Alpha-over of corresponding base and controls files.':null});
 }
 if(w===5120)for(const t of targets.filter(t=>t.family==='legacy_screen_7'&&t.mode==='RGBA'))await save(t,parts.combined,'transparent_ui_alias',{dynamic_text_baked:false});
 if(w===10240)cache.delete(`${w}x${h}`);
}
const p=await layers(2560,1080),labelImage=await render(sources.labels,2560,1080);
const fog=Buffer.from(rootSvg('<rect width="2560" height="1080" fill="#EFF5DA" opacity=".25"/>'));
const screen=await sharp(cityPath).composite([{input:fog},{input:p.combined},{input:labelImage}]).removeAlpha().png({compressionLevel:9}).toBuffer();
for(const t of targets.filter(t=>t.family==='legacy_screen_7'&&t.mode==='RGB'))await save(t,screen,'server_selection_visual_reference',{dynamic_text_baked:true,text_source:'qdao_ui_redesign_v5/copy.zh-CN.json',production_data:false});
const manifest={product:copy.product.title,version:'gpt-image2-q7',date:'2026-09-07',asset_count:outputRecords.length,original_dimensions_preserved:true,source_builder:rel(fileURLToPath(import.meta.url)),source_vectors:['native_q5/base.svg','native_q5/controls.svg','native_q5/labels.svg'],layer_contract:{base:'Transparent decorative frame/plaque + approved Q hero; no labels.',controls:'Transparent newly AI-painted fixed-contract control skins, badge icons, and demo state markers; no labels.',combined:'Exact alpha-over of matching base and controls; no labels.',root_rgba:'Compatibility alias of the 5120 transparent combined UI.',root_rgb:'Approved main-city scene + light veil + 2560 combined UI + separate labels SVG from existing copy JSON. Visual reference only.'},runtime_note:'This rebuild does not connect a game client. Use individual controls/state assets and render text from real data. Combined PNGs illustrate one default arrangement and do not implement input or selection.',sources:[{path:rel(heroPath),sha256:sha(await fs.readFile(heroPath)),role:'New v7 1024px true-alpha Q hero, resampled for corner decoration.'},{path:rel(cityPath),sha256:sha(await fs.readFile(cityPath)),role:'New v7 main-city background; root RGB visuals only.'},{path:'qdao_ui_redesign_v5/copy.zh-CN.json',sha256:sha(await fs.readFile(path.join(repo,'qdao_ui_redesign_v5/copy.zh-CN.json'))),role:'Existing approved product name and demo data.'}],hero_placement_2560:heroRect,control_placements_2560:placements,text_placements_2560:textNodes,outputs:outputRecords};
await fs.writeFile(path.join(layerRoot,'manifest_native_q5.json'),JSON.stringify(manifest,null,2)+'\n','utf8');
console.log(JSON.stringify({replaced:outputRecords.length,transparent_layers:8,opaque_screen_references:4,source_vectors:3,dimensions:[2560,5120,10240],dynamic_text_separate_for_rgba:true}));
