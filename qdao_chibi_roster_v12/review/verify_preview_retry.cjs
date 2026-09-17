const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),assert=require('assert');
(async()=>{
 const output='E:/work/image/qdao_chibi_roster_v12/review/browser-qc/image-retry-result.json';
 const report={status:'running',intentionalFailure:'27/E/04 browser request aborted once',verifiedUtc:new Date().toISOString()};
 let browser;
 try{
  browser=await chromium.launch({channel:'msedge',headless:true});const page=await browser.newPage();page.setDefaultTimeout(20000);
  let requests=0;
  await page.route('**/assets/v12/27_ink_kite_ranger/walk/E/04.png',route=>{requests++;return requests===1?route.abort('failed'):route.continue();});
  await page.goto('http://127.0.0.1:8871/index.html');await page.locator('#play:not([disabled])').waitFor();
  await page.locator('#character').selectOption('27_ink_kite_ranger');await page.locator('#play:not([disabled])').waitFor();
  await page.locator('[data-direction="E"]').click();await page.locator('#load-error').waitFor({state:'visible'});
  assert(await page.locator('#play').isDisabled());
  assert.equal(await page.evaluate(()=>imageCache.has('assets/v12/27_ink_kite_ranger/walk/E/04.png')),false);
  await page.locator('[data-direction="E"]').click();await page.locator('#play:not([disabled])').waitFor();
  assert.equal(await page.locator('#load-error').isVisible(),false);assert.equal(requests,2);
  report.status='passed';report.failedPromiseEvicted=true;report.sameDirectionReloadsActualMissingFrame=true;report.requestCount=requests;
 }catch(e){report.status='failed';report.failure=String(e);throw e;}
 finally{fs.writeFileSync(output,JSON.stringify(report,null,2));if(browser)await browser.close();}
 console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exitCode=1;});
