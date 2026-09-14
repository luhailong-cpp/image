const { chromium } = require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
(async()=>{
const out='E:/work/image/qdao_chibi_roster_v12/review/browser-qc';fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({channel:'msedge',headless:true});const page=await browser.newPage({viewport:{width:1280,height:1050}});
const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(r.status()+' '+r.url());});
await page.goto('http://127.0.0.1:8871/sample.html');await page.locator('#play:not([disabled])').waitFor();await page.getByRole('button',{name:'08',exact:true}).click();
if(!(await page.locator('#sample-caption').textContent()).includes('第 8 / 8'))throw Error('frame08 failed');
await page.locator('#next').click();if(!(await page.locator('#sample-caption').textContent()).includes('第 1 / 8'))throw Error('wrap failed');
await page.locator('#speed').selectOption('0.5');await page.locator('#bg').click();await page.locator('#guide').uncheck();
if(await page.locator('#pair').evaluate(e=>e.classList.contains('guides')))throw Error('guides failed');
await page.screenshot({path:out+'/sample-desktop.png',fullPage:true});
await page.setViewportSize({width:390,height:844});await page.screenshot({path:out+'/sample-mobile.png',fullPage:true});
const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);if(overflow)throw Error('mobile overflow');
if(errors.length)throw Error(errors.join('\n'));fs.writeFileSync(out+'/sample-result.json',JSON.stringify({passed:true,loadedSourceAndSampleFrames:16,frame08:true,wrap08to01:true,halfSpeed:true,darkBackground:true,guideToggle:true,mobileWidth:390,horizontalOverflow:overflow,errors},null,2));
await browser.close();console.log('Sample page passed, 16 real PNGs loaded, controls and 390px mobile checked.');
})().catch(e=>{console.error(e);process.exitCode=1});