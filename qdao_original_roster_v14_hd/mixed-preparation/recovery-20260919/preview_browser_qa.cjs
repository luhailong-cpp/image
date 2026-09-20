const fs=require('fs');
const assert=require('assert');
const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out=__dirname;
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
  const page=await browser.newPage({viewport:{width:1920,height:1080},reducedMotion:'reduce'});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8877/');
  await page.waitForFunction(()=>window.mixedPreviewDebug?.getState().reviewStatus==='pending');
  await page.evaluate(()=>mixedPreviewDebug.selectDirection('SW'));
  let state=await page.evaluate(()=>mixedPreviewDebug.getState());
  assert.equal(state.loaded.length,3);assert.equal(state.complete,false);assert.equal(state.playing,false);
  assert.equal(state.sourceSizes.find(r=>r[0]==='walk/SW/01.png')[1],512);
  assert.equal(state.sourceSizes.find(r=>r[0]==='walk/SW/02.png')[1],1024);
  assert.deepEqual(state.renderDestination,[1024,1024]);
  const drawAudit=await page.evaluate(()=>{const calls=[];const proto=CanvasRenderingContext2D.prototype,old=proto.drawImage;proto.drawImage=function(...args){calls.push([args[0].naturalWidth,...args.slice(1)]);return old.apply(this,args)};mixedPreviewDebug.setFrame(1);mixedPreviewDebug.setFrame(2);proto.drawImage=old;return calls});
  assert(drawAudit.some(r=>r[0]===512&&r.slice(1).join(',')==='0,0,1024,1024'));
  assert(drawAudit.some(r=>r[0]===1024&&r.slice(1).join(',')==='0,0,1024,1024'));
  await page.screenshot({path:out+'/mixed-preview-desktop-qa.png',fullPage:true});
  await page.locator('#next').click();assert.equal((await page.evaluate(()=>mixedPreviewDebug.getState())).frame,3);
  await page.evaluate(()=>mixedPreviewDebug.setFrame(1));await page.locator('#next').focus();await page.keyboard.press('Space');assert.equal((await page.evaluate(()=>mixedPreviewDebug.getState())).frame,2);assert.equal((await page.evaluate(()=>mixedPreviewDebug.getState())).playing,false);
  await page.evaluate(()=>mixedPreviewDebug.setFrame(16));await page.locator('#next').click();assert.equal((await page.evaluate(()=>mixedPreviewDebug.getState())).frame,1);
  await page.evaluate(()=>mixedPreviewDebug.setFrame(1));await page.keyboard.press('ArrowLeft');assert.equal((await page.evaluate(()=>mixedPreviewDebug.getState())).frame,16);
  await page.locator('#play').click();await page.waitForTimeout(100);assert.equal((await page.evaluate(()=>mixedPreviewDebug.getState())).playing,true);await page.locator('#play').click();
  await page.locator('#large').check();assert(await page.locator('body').evaluate(el=>el.classList.contains('large')));
  const downloadPromise=page.waitForEvent('download');await page.locator('#draft').click();const download=await downloadPromise;await download.saveAs(out+'/mixed-preview-PENDING-qa.json');
  const draft=JSON.parse(fs.readFileSync(out+'/mixed-preview-PENDING-qa.json','utf8'));assert.equal(draft.status,'pending');assert.deepEqual(draft.evidence,[]);assert.equal(draft.reviewed_at_utc,null);
  await page.setViewportSize({width:375,height:812});await page.locator('#large').uncheck();
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
  await page.screenshot({path:out+'/mixed-preview-mobile-qa.png',fullPage:true});
  await page.setViewportSize({width:812,height:375});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
  assert.deepEqual(errors,[]);
  fs.writeFileSync(out+'/preview-browser-qa.json',JSON.stringify({scope:'Preview fixture only; no artwork approval',status:'passed',checks:['actual PNG decode and browser SHA','512 and 1024 both drawn to same 1024 world canvas','missing slots remain empty','16 to 1 wrap','keyboard stepping','deliberate playback','large view','pending-only review download','375px and landscape no overflow','reduced-motion starts paused'],state,errors},null,2));
 } finally {await browser.close();await fetch('http://127.0.0.1:8877/qa-stop').catch(()=>{});}
})().catch(e=>{console.error(e);process.exitCode=1});
