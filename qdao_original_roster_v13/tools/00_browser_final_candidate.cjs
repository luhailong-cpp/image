const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const out='E:/work/image/qdao_original_roster_v13/review/00_reference_topright_boy/browser-final-candidate';
fs.mkdirSync(out,{recursive:true});
const results={scope:'00 actual candidate preview, not Unity or final visual approval',started_utc:new Date().toISOString(),base:'http://127.0.0.1:8874/',errors:[],network:[],directions:[],checks:[]};
function check(name,ok,detail){results.checks.push({name,passed:!!ok,detail});if(!ok)throw Error(name+': '+JSON.stringify(detail));}
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
const browser=await chromium.launch({channel:'msedge',headless:true});const page=await browser.newPage({viewport:{width:1180,height:1050},deviceScaleFactor:1});
page.on('pageerror',e=>results.errors.push(String(e)));page.on('response',r=>{if(r.url().includes('/candidate/00_reference_topright_boy/'))results.network.push({url:r.url(),status:r.status()});});
await page.goto(results.base,{waitUntil:'networkidle'});
await page.selectOption('#character','00_reference_topright_boy');
for(const d of ['S','E','SE','NE','N','NW','W','SW']){
 await page.selectOption('#direction',d);await page.waitForFunction(d=>window.previewDebug.getState().direction===d&&window.previewDebug.getState().loaded===16&&!document.querySelector('#status').textContent.includes('正在'),d);
 const info=await page.evaluate(()=>({state:previewDebug.getState(),status:document.querySelector('#status').textContent,images:images.map(im=>({src:im.src,w:im.naturalWidth,h:im.naturalHeight})),idle:{src:idle?.src,w:idle?.naturalWidth,h:idle?.naturalHeight}}));
 check(d+' full actual inventory',info.images.length===16&&info.images.every((x,i)=>x.w===512&&x.h===512&&x.src.endsWith('/'+String(i+1).padStart(2,'0')+'.png'))&&info.idle.w===512&&info.idle.src.endsWith('/idle/'+d+'.png'),info);
 check(d+' pending visual label',info.status.includes('pending_visual'),info.status);
 const pixels=[];
 for(const ms of [0,240,450]){await page.evaluate(ms=>previewDebug.setPhase(ms),ms);const x=await page.locator('#walk').screenshot();pixels.push({phase:ms,sha256:sha(x)});await page.screenshot({path:path.join(out,d+'-'+String(ms/30+1).padStart(2,'0')+'-normal.png')});}
 check(d+' 01 09 16 differ',new Set(pixels.map(p=>p.sha256)).size===3,pixels);results.directions.push({direction:d,inventory:info,pixels});
}
await page.selectOption('#direction','S');await page.waitForFunction(()=>previewDebug.getState().direction==='S'&&previewDebug.getState().loaded===16);
for(const [phase,frame] of [[0,1],[29.999,1],[30,2],[239.9,8],[240,9],[450,16],[479.9,16],[480,1]]){await page.evaluate(p=>previewDebug.setPhase(p),phase);const state=await page.evaluate(()=>previewDebug.getState());check('phase '+phase,state.frame===frame,state);}
await page.evaluate(()=>previewDebug.setPhase(450));await page.click('#next');check('next wraps16 to1',(await page.evaluate(()=>previewDebug.getState())).frame===1);
await page.click('#prev');check('previous wraps1 to16',(await page.evaluate(()=>previewDebug.getState())).frame===16);
const before=await page.evaluate(()=>previewDebug.getState());await page.waitForTimeout(160);const after=await page.evaluate(()=>previewDebug.getState());check('paused stays exact',before.phase===after.phase&&!after.playing,{before,after});
for(const speed of ['1','.5']){
 await page.selectOption('#speed',speed);await page.evaluate(()=>previewDebug.setPhase(0));await page.click('#play');
 const a=await page.evaluate(()=>({time:performance.now(),state:previewDebug.getState()}));await page.waitForTimeout(270);const b=await page.evaluate(()=>({time:performance.now(),state:previewDebug.getState()}));
 const elapsed=b.time-a.time,advanced=(b.state.phase-a.state.phase+480)%480;
 check('real clock speed '+speed,Math.abs(advanced-elapsed*Number(speed))<40,{a,b,elapsed,advanced,expected:elapsed*Number(speed)});
 await page.click('#play');
}
await page.check('#large');await page.evaluate(()=>previewDebug.setPhase(240));await page.screenshot({path:path.join(out,'S-09-enlarged.png')});
const large=await page.locator('#walk').boundingBox();await page.uncheck('#large');const normal=await page.locator('#walk').boundingBox();check('enlarged actual canvas',large.width>normal.width,{large,normal});
await page.setViewportSize({width:390,height:900});await page.screenshot({path:path.join(out,'mobile-390.png')});
const widths=await page.evaluate(()=>({window:innerWidth,document:document.documentElement.scrollWidth,body:document.body.scrollWidth}));check('390 no horizontal overflow',widths.document<=widths.window&&widths.body<=widths.window,widths);
check('zero JS errors',results.errors.length===0,results.errors);check('all candidate PNG requests200',results.network.length>=136&&results.network.every(r=>r.status===200),{requests:results.network.length,bad:results.network.filter(r=>r.status!==200)});
results.finished_utc=new Date().toISOString();results.status='passed_preview_behavior_pending_art_review';fs.writeFileSync(path.join(out,'browser-report.json'),JSON.stringify(results,null,2));await browser.close();console.log(JSON.stringify({status:results.status,directions:results.directions.length,checks:results.checks.length,requests:results.network.length,out}));
})().catch(e=>{results.status='failed';results.failure=String(e);fs.writeFileSync(path.join(out,'browser-report.json'),JSON.stringify(results,null,2));console.error(e);process.exit(1)});
