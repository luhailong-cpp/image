const { chromium } = require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = 'E:/work/image/qdao_chibi_roster_v13';
const out = path.join(root, 'review/browser-scaffold');
fs.mkdirSync(out, { recursive: true });
const report = { status: 'running', scope: 'scaffold-only browser QA; V13 artwork incomplete; not animation-art acceptance or game integration validation', checkedUtc: new Date().toISOString(), url: 'http://127.0.0.1:8873/', service: { pid: 24520, reused: true, host: '127.0.0.1', root }, assertions: [], errors: [], requests: [], screenshots: [] };
let browser;
function assert(name, ok, detail) { report.assertions.push({ name, passed: !!ok, detail }); if (!ok) report.errors.push(name); }
function sha(file) { return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'); }
(async () => {
 browser = await chromium.launch({ channel: 'msedge', headless: true });
 report.browserVersion = browser.version();
 report.inputs = ['index.html','tools/preview-template.html','tools/serve_preview.py','tools/qa_browser_scaffold.cjs'].map(name => ({file:path.join(root,name),sha256:sha(path.join(root,name))}));
 const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 });
 const page = await context.newPage();
 const responses = [], consoleErrors = [], pageErrors = [];
 page.on('response', r => { responses.push({ url: r.url(), status: r.status() }); });
 page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
 page.on('pageerror', e => pageErrors.push(String(e)));
 await page.addInitScript(() => {
   const clear = CanvasRenderingContext2D.prototype.clearRect;
   CanvasRenderingContext2D.prototype.clearRect = function (...a) { this.canvas.dataset.qaImage = ''; this.canvas.dataset.qaText = ''; return clear.apply(this, a); };
   const draw = CanvasRenderingContext2D.prototype.drawImage;
   CanvasRenderingContext2D.prototype.drawImage = function (...a) { this.canvas.dataset.qaImage = a[0].src || ''; return draw.apply(this, a); };
   const text = CanvasRenderingContext2D.prototype.fillText;
   CanvasRenderingContext2D.prototype.fillText = function (...a) { this.canvas.dataset.qaText = a[0]; return text.apply(this, a); };
 });
 const navigation = await page.goto(report.url, { waitUntil: 'networkidle', timeout: 30000 });
 assert('preview document serves HTTP 200', navigation.status() === 200, { status: navigation.status() });
 await page.waitForFunction(() => window.previewDebug && Object.values(window.previewDebug.getState().loaded).every(n => n === 8));
 await page.evaluate(() => window.previewDebug.setPhase(0));
 const directions = ['S','E','N','NE','SE','SW','W','NW'];
 const initial = await page.evaluate(() => ({ debug: window.previewDebug.getState(), labels: [...document.querySelectorAll('.card')].map(el => ({ direction:el.dataset.direction, readiness:el.querySelector('h2 .state').textContent, pending:el.querySelector('h2 .state').classList.contains('pending') })) }));
 assert('eight direction cards each show exactly 8/16 ready and pending', initial.labels.length === 8 && initial.labels.every(x => x.readiness === '8/16 张已就绪' && x.pending), initial);
 assert('page explicitly says missing poses will not be filled by old images', (await page.locator('.guide').innerText()).includes('页面不会复制旧图填满空位'));
 const phaseRows=[];
 for(let index=0;index<16;index++){
   await page.evaluate(ms => window.previewDebug.setPhase(ms), index*30);
   const row=await page.evaluate(() => ({ debug:window.previewDebug.getState(), cards:[...document.querySelectorAll('.card')].map(c=>({ direction:c.dataset.direction,oldLabel:c.querySelector('.old-frame').textContent,newLabel:c.querySelector('.new-frame').textContent,canvases:[...c.querySelectorAll('canvas')].map(v=>({image:v.dataset.qaImage,text:v.dataset.qaText})) })) }));
   const oldPos=Math.floor(index/2)*2+1, newPos=index+1;
   const expectedOld=String(oldPos).padStart(2,'0')+'.png', expectedNew=String(newPos).padStart(2,'0')+'.png';
   const ok=row.debug.frame8===Math.floor(index/2)+1 && row.debug.frame16===newPos && row.cards.every(c=>c.canvases[0].image.endsWith('/'+c.direction+'/'+expectedOld) && (newPos%2 ? c.canvases[1].image.endsWith('/'+c.direction+'/'+expectedNew) && !c.canvases[1].text : !c.canvases[1].image && c.canvases[1].text==='该过渡帧待完成'));
   assert('phase '+String(newPos).padStart(2,'0')+' has correct old/new mapping and honest missing-pose canvas',ok,row);
   phaseRows.push(row);
 }
 report.phaseMapping=phaseRows;
 await page.evaluate(() => window.previewDebug.setPhase(480));
 let state=await page.evaluate(()=>window.previewDebug.getState());
 assert('480ms wraps both sequences to first frame',state.elapsed===0 && state.frame8===1 && state.frame16===1,state);
 await page.locator('#next').click(); state=await page.evaluate(()=>window.previewDebug.getState());
 assert('next pauses and advances 30ms while old 8-frame holds',!state.playing&&state.elapsed===30&&state.frame8===1&&state.frame16===2,state);
 await page.locator('#previous').click(); state=await page.evaluate(()=>window.previewDebug.getState());
 assert('previous reverses one 30ms step',state.elapsed===0&&state.frame8===1&&state.frame16===1,state);
 await page.locator('#previous').click(); state=await page.evaluate(()=>window.previewDebug.getState());
 assert('previous wraps to 450ms / old08 / new16',state.elapsed===450&&state.frame8===8&&state.frame16===16,state);
 await page.locator('#next').click(); state=await page.evaluate(()=>window.previewDebug.getState());
 assert('next wraps 450ms to0',state.elapsed===0&&state.frame8===1&&state.frame16===1,state);
 const pausedBefore=state.elapsed; await page.waitForTimeout(180);
 state=await page.evaluate(()=>window.previewDebug.getState());
 assert('paused clock stays fixed',state.elapsed===pausedBefore&&!state.playing,state);
 for(const direction of directions){
   await page.selectOption('#direction',direction);
   const visible=await page.locator('.card:visible').evaluateAll(els=>els.map(x=>x.dataset.direction));
   assert('direction filter '+direction,visible.length===1&&visible[0]===direction,{visible});
 }
 await page.selectOption('#direction','all');
 assert('all-direction filter restores eight cards',(await page.locator('.card:visible').count())===8);
 await page.evaluate(()=>window.previewDebug.setPhase(210));
 await page.locator('#idle').check();
 const idleState=await page.evaluate(()=>({debug:window.previewDebug.getState(),clock:document.getElementById('clock').textContent,cards:[...document.querySelectorAll('.card')].map(c=>({direction:c.dataset.direction,canvases:[...c.querySelectorAll('canvas')].map(v=>v.dataset.qaImage)}))}));
 assert('idle uses same dedicated direction PNG on both sides',idleState.debug.idle&&idleState.clock==='站立'&&idleState.cards.every(c=>c.canvases.every(url=>url.endsWith('/idle/'+c.direction+'.png'))),idleState);
 await page.locator('#idle').uncheck();
 assert('unchecking idle restores frozen walk phase',(await page.evaluate(()=>window.previewDebug.getState())).elapsed===210);
 report.rateSamples=[];
 for(const rate of ['1','0.5','0.25']){
   await page.selectOption('#speed',rate);
   await page.evaluate(()=>window.previewDebug.setPhase(0));
   await page.locator('#play').click();
   const before=await page.evaluate(()=>({...window.previewDebug.getState(),time:performance.now()}));
   await page.waitForTimeout(220);
   const after=await page.evaluate(()=>({...window.previewDebug.getState(),time:performance.now()}));
   await page.locator('#play').click();
   const real=after.time-before.time,advanced=(after.elapsed-before.elapsed+480)%480,expected=real*Number(rate);
   const sample={rate:Number(rate),realMs:real,advancedMs:advanced,expectedMs:expected,toleranceMs:28};report.rateSamples.push(sample);
   assert('playback speed '+rate+' follows shared elapsed clock',Math.abs(advanced-expected)<28,sample);
 }
 await page.selectOption('#speed','1');
 await page.selectOption('#direction','S');
 await page.evaluate(()=>window.previewDebug.setPhase(30));
 await page.locator('#large').check();
 assert('large review option sets large class',await page.locator('body').evaluate(el=>el.classList.contains('large')));
 const capture=async name=>{const file=path.join(out,name);await page.screenshot({path:file,fullPage:true});report.screenshots.push({file,sha256:sha(file)});};
 await capture('desktop-S-missing-transition.png');
 await page.locator('#idle').check(); await capture('desktop-S-dedicated-idle.png'); await page.locator('#idle').uncheck();
 await page.locator('#large').uncheck();await page.selectOption('#direction','all');
 await page.setViewportSize({width:390,height:844});
 const mobile=await page.evaluate(()=>({viewport:innerWidth,html:document.documentElement.scrollWidth,body:document.body.scrollWidth,cards:[...document.querySelectorAll('.card')].map(c=>({d:c.dataset.direction,x:c.getBoundingClientRect().x,right:c.getBoundingClientRect().right,width:c.getBoundingClientRect().width}))}));
 assert('390px layout has no horizontal overflow',mobile.html<=390&&mobile.body<=390&&mobile.cards.every(c=>c.x>=0&&c.right<=390),mobile);
 const mobilePlaceholderText=await page.locator('.card canvas:nth-of-type(1)').evaluateAll(() => [...document.querySelectorAll('.card .slot:nth-child(2) canvas')].map(c=>({direction:c.closest('.card').dataset.direction,font:c.getContext('2d').font,displayPx:parseFloat(c.getContext('2d').font)*c.clientWidth/c.width,text:c.dataset.qaText})));
 assert('390px missing-pose text remains readable at12px or more',mobilePlaceholderText.every(c=>c.displayPx>=12 && c.text==='该过渡帧待完成'),mobilePlaceholderText);
 await capture('mobile-390-all-directions.png');
 await page.selectOption('#direction','E');await page.locator('#large').check();
 const mobileLarge=await page.evaluate(()=>({html:document.documentElement.scrollWidth,body:document.body.scrollWidth,visible:[...document.querySelectorAll('.card')].filter(c=>!c.hidden).map(c=>c.dataset.direction)}));
 assert('390px large single-direction view fits viewport',mobileLarge.html<=390&&mobileLarge.body<=390&&mobileLarge.visible.join()==='E',mobileLarge);
 await capture('mobile-390-E-large.png');
 const statuses=new Map(responses.map(x=>[x.url,x.status]));
 const expectedMissing=[];const expectedPresent=[];
 for(const d of directions){for(let f=1;f<=16;f++)(f%2?expectedPresent:expectedMissing).push(report.url+'candidate/24_lu_dongbin/walk/'+d+'/'+String(f).padStart(2,'0')+'.png');expectedPresent.push(report.url+'candidate/24_lu_dongbin/idle/'+d+'.png');}
 assert('all64 original odd PNGs and8 idle images loaded200',expectedPresent.every(url=>statuses.get(url)===200),{expected:72,present:expectedPresent.filter(url=>statuses.get(url)===200).length});
 assert('all64 pending real transitions returned404',expectedMissing.every(url=>statuses.get(url)===404),{expected:64,missing:expectedMissing.filter(url=>statuses.get(url)===404).length});
 const expectedSet=new Set(expectedMissing);const unexpected=responses.filter(x=>x.status>=400&&!expectedSet.has(x.url));
 assert('no unexpected failed resource responses',unexpected.length===0,{unexpected});
 assert('no JavaScript exceptions',pageErrors.length===0,pageErrors);
 report.requests=responses;report.consoleErrors=consoleErrors;report.pageErrors=pageErrors;report.expected404s=expectedMissing;report.note='Expected 64 missing-transition HTTP404 responses are scaffold state, not delivered art. This run does not accept anatomy, motion smoothness, loop continuity, generated-pose provenance, or Unity behavior.';
 report.status=report.errors.length?'failed':'passed-scaffold-only';
 await browser.close();browser=null;
})().catch(async err=>{report.status='failed';report.errors.push(String(err.stack||err));if(browser)await browser.close();}).finally(()=>{
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));
 const failed=report.assertions.filter(x=>!x.passed);
 fs.writeFileSync(path.join(out,'README.md'),'# V13 preview scaffold-only browser QA\n\nStatus: **'+report.status+'**. '+report.checkedUtc+'\n\nThis verifies preview controls and honest pending-art state. It is not V13 animation-art acceptance or game integration validation.\n\n- '+report.assertions.filter(x=>x.passed).length+' assertions passed; '+failed.length+' failed.\n- Expected assets: 64 original odd frames and 8 dedicated idle PNGs.\n- All 64 new even transition poses remain absent; their HTTP404s must be visible as pending poses, never filled by old art.\n- Browser: Microsoft Edge '+(report.browserVersion||'unavailable')+' in headless mode.\n- Service reused at 127.0.0.1:8873, PID24520, serving only V13 root.\n\nSee [report.json](report.json) for requests, phase checks, timing samples, screenshots, and errors.\n\n'+report.screenshots.map(x=>'- ['+path.basename(x.file)+']('+path.basename(x.file)+')').join('\n')+'\n\n'+(failed.length?'Failures:\n'+failed.map(x=>'- '+x.name).join('\n'):'')+'\n');
 console.log(JSON.stringify({status:report.status,passed:report.assertions.filter(x=>x.passed).length,failed:failed.map(x=>x.name),errors:report.errors,report:path.join(out,'report.json')},null,2));
 process.exitCode=report.status==='passed-scaffold-only'?0:1;
});
