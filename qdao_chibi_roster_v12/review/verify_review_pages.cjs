const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');const assert=require('assert');
const previewSources=JSON.parse(fs.readFileSync('E:/work/image/qdao_chibi_roster_v12/review/site/preview-source-verification.json','utf8'));
const expectedPublished=new Set(previewSources.characters.map(c=>c.character_id));
const expectedPending=new Set(previewSources.pending);
const expectedExported=Number(process.env.QDAO_EXPECTED_EXPORTED||expectedPublished.size);
assert.equal(expectedPublished.size,expectedExported,'Published preview count does not match requested QA scope');
(async()=>{
const out='E:/work/image/qdao_chibi_roster_v12/review/browser-qc';fs.mkdirSync(out,{recursive:true});let browser;
const report={status:'running',pages:{},errors:[]};
try{
browser=await chromium.launch({channel:'msedge',headless:true});
const page=await browser.newPage({viewport:{width:1280,height:1050}});
page.setDefaultTimeout(20000);
page.on('pageerror',e=>report.errors.push(e.message));
page.on('response',r=>{if(r.status()>=400&&!r.url().endsWith('/favicon.ico'))report.errors.push(r.status()+' '+r.url());});
await page.goto('http://127.0.0.1:8871/index.html');
await page.locator('#play:not([disabled])').waitFor();
const names=await page.locator('#character option').evaluateAll(es=>es.map(e=>e.value));assert.equal(names.length,8);
let directions=0,disabled=0;
for(const name of names){
 await page.locator('#character').selectOption(name);
 if(expectedPending.has(name)){await page.locator('#candidate').waitFor({state:'visible'});assert(await page.locator('#play').isDisabled());disabled++;continue;}
 assert(expectedPublished.has(name),'Role missing from verified preview source list: '+name);
 for(const dr of ['S','SW','W','NW','N','NE','E','SE']){
  await page.locator('[data-direction="'+dr+'"]').click();
  await page.locator('#play:not([disabled])').waitFor();
  assert.equal(await page.locator('#load-error').isVisible(),false);
  directions++;
 }
}
assert.equal(directions,expectedExported*8);assert.equal(disabled,8-expectedExported);
await page.locator('#character').selectOption('24_lu_dongbin');await page.locator('#play:not([disabled])').waitFor();
await page.locator('#timeline button').nth(7).click();await page.locator('#next').click();assert((await page.locator('#new-caption').textContent()).includes('第 1 / 8'));
await page.locator('#play').click();const seen=new Set();
for(let i=0;i<6;i++){await page.waitForTimeout(90);seen.add(await page.locator('#new-caption').textContent());}
assert(seen.size>1,'index animation stalled');
await page.evaluate(()=>{epoch=performance.now()+80;playing=true;});await page.waitForTimeout(180);assert(report.errors.length===0,'index future epoch boundary failed');
await page.screenshot({path:out+'/index-fixed-desktop.png',fullPage:true});
report.pages.index={roles:names.length,exportedDirectionPairs:directions,candidatesDisabled:disabled,realAnimationAdvances:seen.size>1,futureEpochBoundary:true};

await page.goto('http://127.0.0.1:8871/sample.html');
const expectedDirections=['S','SW','W','NW','N','NE','E','SE'];
const sampleDirections=await page.locator('#direction option').evaluateAll(es=>es.map(e=>e.value));
assert.deepEqual(sampleDirections,expectedDirections,'sample must expose all8 directions');
assert.deepEqual(await page.locator('#action option').evaluateAll(es=>es.map(e=>e.value)),['walk','idle']);
assert((await page.locator('#delivery-status').textContent()).includes('已接入游戏项目'),'published status must match actual imported resource state');
const waitState=async(dr,mode)=>page.waitForFunction(({dr,mode})=>document.body.dataset.ready==='true'&&document.body.dataset.direction===dr&&document.body.dataset.action===mode,{dr,mode});
const sourceChecks=[];
for(const dr of sampleDirections){
 await page.locator('#direction').selectOption(dr);await page.locator('#action').selectOption('walk');await waitState(dr,'walk');
 assert.equal(await page.locator('#error').isVisible(),false);
 await page.locator('#timeline button').nth(7).click();
 assert((await page.locator('#sample-caption').textContent()).includes('第 8 / 8'));
 const paused=await page.locator('#sample-caption').textContent();await page.waitForTimeout(150);assert.equal(await page.locator('#sample-caption').textContent(),paused,'seeking must freeze a walk frame');
 assert.equal(await page.locator('#action').inputValue(),'walk','pause must not select idle');
 await page.locator('#next').click();assert((await page.locator('#sample-caption').textContent()).includes('第 1 / 8'));
 await page.locator('#prev').click();assert((await page.locator('#sample-caption').textContent()).includes('第 8 / 8'));
 const walkCanvas=await page.locator('#sample').evaluate(c=>c.toDataURL());
 const walkSources=await page.evaluate(()=>({old:oldFrames.map(im=>im.src),candidate:sampleFrames.map(im=>im.src)}));
 assert.equal(walkSources.old.length,8);assert.equal(walkSources.candidate.length,8);
 assert(walkSources.candidate.every(s=>s.includes('/sample/walk/'+dr+'/')));
 await page.locator('#action').selectOption('idle');await waitState(dr,'idle');
 assert.equal(await page.locator('#error').isVisible(),false);
 assert(await page.locator('#timeline').isHidden(),'idle should not present walk-frame controls');
 for(const control of ['play','prev','next','speed'])assert(await page.locator('#'+control).isDisabled(),'idle control must be disabled: '+control);
 assert((await page.locator('#old-caption').textContent()).includes('独立站立'));
 assert((await page.locator('#sample-caption').textContent()).includes('独立站立'));
 assert(!(await page.locator('#sample-caption').textContent()).includes('/ 8'),'idle must not masquerade as paused walk');
 const idleCanvas=await page.locator('#sample').evaluate(c=>c.toDataURL());assert.notEqual(idleCanvas,walkCanvas,'idle should use an independent authored picture');
 const idleSources=await page.evaluate(()=>({old:oldFrames.map(im=>im.src),candidate:sampleFrames.map(im=>im.src)}));
 assert.equal(idleSources.old.length,1);assert.equal(idleSources.candidate.length,1);
 assert(idleSources.old[0].endsWith('/assets/pre-natural/24_lu_dongbin/idle/'+dr+'.png'));
 assert(idleSources.candidate[0].endsWith('/sample/idle/'+dr+'.png'));
 const staticCaption=await page.locator('#sample-caption').textContent();await page.waitForTimeout(100);assert.equal(await page.locator('#sample-caption').textContent(),staticCaption);
 sourceChecks.push({direction:dr,walkFramesPerSide:8,independentIdlePerSide:1,oldIdle:idleSources.old[0],candidateIdle:idleSources.candidate[0]});
 await page.locator('#action').selectOption('walk');await waitState(dr,'walk');assert(await page.locator('#timeline').isVisible());assert(!(await page.locator('#play').isDisabled()));
}
await page.locator('#direction').selectOption('S');await waitState('S','walk');
await page.locator('#timeline button').nth(0).click();await page.locator('#play').click();
const sampleSeen=new Set();for(let i=0;i<6;i++){await page.waitForTimeout(90);sampleSeen.add(await page.locator('#sample-caption').textContent());}assert(sampleSeen.size>1,'sample animation stalled');
await page.evaluate(()=>{epoch=performance.now()+80;playing=true;});await page.waitForTimeout(180);assert(report.errors.length===0,'sample future epoch boundary failed');
await page.locator('#speed').selectOption('0.5');assert.equal(await page.evaluate(()=>rate),0.5);
await page.locator('#bg').click();assert.equal(await page.locator('body').getAttribute('data-bg'),'dark');
await page.locator('#guide').uncheck();assert(!(await page.locator('#pair').getAttribute('class')).includes('guides'));
await page.locator('#direction').selectOption('NW');await waitState('NW','walk');await page.locator('#timeline button').nth(6).click();
await page.screenshot({path:out+'/sample-eight-directions-walk-desktop.png',fullPage:true});
await page.locator('#action').selectOption('idle');await waitState('NW','idle');
await page.screenshot({path:out+'/sample-eight-directions-idle-desktop.png',fullPage:true});
await page.setViewportSize({width:390,height:844});await page.locator('#direction').selectOption('SE');await waitState('SE','idle');
await page.screenshot({path:out+'/sample-eight-directions-idle-mobile.png',fullPage:true});
assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)),'sample idle mobile overflow');
await page.locator('#action').selectOption('walk');await waitState('SE','walk');await page.locator('#timeline button').nth(7).click();
await page.screenshot({path:out+'/sample-eight-directions-walk-mobile.png',fullPage:true});
assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)),'sample walk mobile overflow');

await page.emulateMedia({reducedMotion:'reduce'});await page.reload();await waitState('S','walk');
assert.equal(await page.locator('#play').textContent(),'播放');const reducedCaption=await page.locator('#sample-caption').textContent();await page.waitForTimeout(180);assert.equal(await page.locator('#sample-caption').textContent(),reducedCaption,'reduced-motion mode should initially pause');
await page.locator('#action').selectOption('idle');await waitState('S','idle');await page.locator('#direction').selectOption('NE');await waitState('NE','idle');
assert.equal(await page.locator('#error').isVisible(),false);

report.pages.sample={directions:sampleDirections,actions:['walk','idle'],loadedPNGCount:144,sourceChecks,independentIdleIsDifferentFromPausedWalk:true,frame08AndBothWrapDirections:true,seekingPausesWalk:true,actualAnimationAdvances:sampleSeen.size>1,futureEpochBoundary:true,halfSpeed:true,backgroundToggle:true,guideToggle:true,reducedMotionStartsPaused:true,mobileWidth:390,noHorizontalOverflow:true};
assert.deepEqual(report.errors,[]);report.status='passed';
}catch(e){report.status='failed';report.failure=String(e);throw e;}
finally{fs.writeFileSync(out+'/review-pages-result.json',JSON.stringify(report,null,2));if(browser)await browser.close();}
console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exitCode=1;});

