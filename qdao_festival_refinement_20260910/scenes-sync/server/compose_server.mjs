import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const sharp=require(process.argv[2]);
const run=path.dirname(fileURLToPath(import.meta.url));
const repo=path.resolve(run,'../../..');
const plan=JSON.parse(await fs.readFile(path.join(run,'plan.json'),'utf8'));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const input=k=>path.join(run,plan.inputs[k].path);
const read=k=>fs.readFile(input(k));
const safe=(base,rel)=>{const p=path.resolve(base,rel);if(!p.startsWith(base+path.sep))throw Error('Unsafe path');return p;};
const checks=[];const check=(name,passed)=>{checks.push({check:name,passed});if(!passed)throw Error(name);};
const geometry={};
for(const k of ['base_svg','controls_svg','labels_svg'])geometry[k]=await fs.readFile(input(k),'utf8');
for(const [k,v] of Object.entries(plan.inputs))check('Input hash '+k,hash(await read(k))===v.sha256);
const sourceAlphaOld=await sharp(input('hero_old')).extractChannel(3).raw().toBuffer();
const sourceAlphaNew=await sharp(input('hero_new')).extractChannel(3).raw().toBuffer();
check('Source hero alpha exactly preserved',sourceAlphaOld.equals(sourceAlphaNew));
const render=(svg,w,h)=>sharp(Buffer.from(svg.replace(/<svg\b[^>]*>/,root=>root.replace(/\bwidth="[^"]*"/,`width="${w}"`).replace(/\bheight="[^"]*"/,`height="${h}"`)))).png({compressionLevel:9}).toBuffer();
const rect=plan.hero_placement_2560;
async function parts(w,h,heroKey){
 const scale=w/2560;
 const base=await render(geometry.base_svg,w,h);
 const hero=await sharp(input(heroKey)).resize(Math.round(rect[2]*scale),Math.round(rect[3]*scale)).png().toBuffer();
 const withHero=await sharp(base).composite([{input:hero,left:Math.round(rect[0]*scale),top:Math.round(rect[1]*scale)}]).png({compressionLevel:9}).toBuffer();
 const controls=await render(geometry.controls_svg,w,h);
 const combined=await sharp(withHero).composite([{input:controls}]).png({compressionLevel:9}).toBuffer();
 return {base:withHero,controls,combined};
}
async function baseline(actual,expected,name){
 if(hash(actual)===hash(expected))return 'byte_identical';
 const a=await sharp(actual).ensureAlpha().raw().toBuffer();
 const b=await sharp(expected).ensureAlpha().raw().toBuffer();
 check('Current output reproducible with old accepted inputs: '+name,a.equals(b));
 return 'rgba_identical';
}
async function compareChange(old,newer,w,h,mode,name){
 const a=await sharp(old).ensureAlpha().raw().toBuffer();
 const b=await sharp(newer).ensureAlpha().raw().toBuffer();
 check('RGBA buffer length '+name,a.length===b.length && a.length===w*h*4);
 let alphaSame=true,outsideSame=true,changed=0;let xmin=w,ymin=h,xmax=-1,ymax=-1;
 const s=w/2560,l=Math.round(rect[0]*s),t=Math.round(rect[1]*s),r=l+Math.round(rect[2]*s),bt=t+Math.round(rect[3]*s);
 for(let q=0;q<a.length;q+=4){
  if(a[q+3]!==b[q+3])alphaSame=false;
  if(a[q]!==b[q]||a[q+1]!==b[q+1]||a[q+2]!==b[q+2]||a[q+3]!==b[q+3]){
   const p=q/4,x=p%w,y=Math.floor(p/w);changed++;xmin=Math.min(xmin,x);xmax=Math.max(xmax,x);ymin=Math.min(ymin,y);ymax=Math.max(ymax,y);
   if(x<l||x>=r||y<t||y>=bt)outsideSame=false;
  }
 }
 check('Full alpha unchanged '+name,alphaSame);check('Pixels outside fixed hero rectangle unchanged '+name,outsideSame);
 return {alpha_exact:alphaSame,outside_hero_rectangle_exact:outsideSame,changed_pixels:changed,changed_bbox:changed?[xmin,ymin,xmax+1,ymax+1]:null};
}
const records=[];
async function save(target,newBytes,oldExpected,proof){
 const old=await fs.readFile(safe(path.join(run,'before'),target.path));
 const stale=target.path===plan.stale_prepared_alias;
 const reproducible=stale?'known_legacy_prepared_alias_replaced_with_current_composite':await baseline(old,oldExpected,target.path);
 const meta=await sharp(newBytes).metadata();
 check('Pixel contract '+target.path,meta.width===target.size[0]&&meta.height===target.size[1]&&(meta.hasAlpha?'RGBA':'RGB')===target.mode);
 const dst=safe(path.join(run,'staged'),target.path);await fs.mkdir(path.dirname(dst),{recursive:true});
 const changed=hash(newBytes)!==target.before_sha256;
 await fs.writeFile(dst,changed?newBytes:old);
 records.push({...target,sha256:hash(changed?newBytes:old),bytes:(changed?newBytes:old).length,staged:path.relative(run,dst).replaceAll('\\','/'),decision:changed?'recompose_from_same_scene_and_current_hero':'retain_unchanged_control_layer',baseline_reproduction:reproducible,...proof,client_written:false});
}
for(const [w,h]of [[5120,2160],[10240,4320]]){
 const old=await parts(w,h,'hero_old'),next=await parts(w,h,'hero_new');
 for(const role of ['base','controls','combined']){
  const targets=plan.outputs.filter(x=>x.mode==='RGBA'&&x.size[0]===w&&(x.role==='transparent_ui_alias'?'combined':x.role)===role);
  if(!targets.length)continue;
  const proof=await compareChange(old[role],next[role],w,h,'RGBA',role+' '+w);
  for(const target of targets)await save(target,next[role],old[role],proof);
 }
 console.log(JSON.stringify({staged_width:w,completed_files:records.length}));
}
const oldPage=await parts(2560,1080,'hero_old'),newPage=await parts(2560,1080,'hero_new');
const labels=await render(geometry.labels_svg,2560,1080);
const veil=Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1080"><rect width="2560" height="1080" fill="#EFF5DA" opacity=".25"/></svg>');
const screen=p=>sharp(input('retained_server_city')).composite([{input:veil},{input:p.combined},{input:labels}]).removeAlpha().png({compressionLevel:9}).toBuffer();
const oldScreen=await screen(oldPage),newScreen=await screen(newPage);
const proof=await compareChange(oldScreen,newScreen,2560,1080,'RGB','server screen');
for(const target of plan.outputs.filter(x=>x.mode==='RGB'))await save(target,newScreen,oldScreen,proof);
const qa=path.join(run,'qa');await fs.mkdir(qa,{recursive:true});
const pair=await Promise.all([oldScreen,newScreen].map(b=>sharp(b).resize(1280,540).toBuffer()));
await sharp({create:{width:1280,height:1080,channels:3,background:'#dae1d5'}}).composite([{input:pair[0],top:0,left:0},{input:pair[1],top:540,left:0}]).jpeg({quality:88}).toFile(path.join(qa,'server-before-after.jpg'));
await sharp(newScreen).extract({left:2000,top:0,width:420,height:385}).png().toFile(path.join(qa,'hero-native-detail.png'));
await fs.writeFile(path.join(run,'staged-validation.json'),JSON.stringify({status:'ready_for_visual_review',checked_at_utc:new Date().toISOString(),files:records,checks,errors:[],images_published:0,preserved_background:plan.inputs.retained_server_city,hero_source:plan.inputs.hero_new,recipe:'Same v10 serverParts with current unchanged SVGs, old approved scene snapshot and new alpha-identical hero',frozen_contracts_modified:false,client_written:false},null,2)+'\n');
console.log(JSON.stringify({status:'ready_for_visual_review',files:records.length,changed:records.filter(r=>r.decision!=='retain_unchanged_control_layer').length,checks:checks.length}));
