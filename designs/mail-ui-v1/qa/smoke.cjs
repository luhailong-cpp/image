const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
let chromium;
try { ({chromium} = require('playwright')); }
catch { ({chromium} = require(path.join(process.env.USERPROFILE, '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'))); }
const output = path.resolve(__dirname, '../screenshots');
const writeArtifacts = process.env.MAIL_UI_QA_WRITE_ARTIFACTS !== '0';
const festivalAssets = {
  midautumn: 'event-midautumn.png',
  'spring-festival': 'event-spring-festival.png',
  'lantern-festival': 'event-lantern-festival.png',
  'spring-equinox': 'event-spring-equinox.png',
  qingming: 'event-qingming.png',
  'dragon-boat': 'event-dragon-boat.png',
  'summer-solstice': 'event-summer-solstice.png',
  qixi: 'event-qixi.png',
  'autumn-equinox': 'event-autumn-equinox.png',
  'double-ninth': 'event-double-ninth.png',
  'winter-solstice': 'event-winter-solstice.png',
  laba: 'event-laba.png'
};
const newSolarTerms = ['spring-equinox', 'summer-solstice', 'autumn-equinox'];
const results = [];
const errors = [];
const check = (name, condition) => { assert(condition, name); results.push(name); };
(async () => {
  const browser = await chromium.launch({headless:true,channel:'msedge'});
  try {
    const context = await browser.newContext({viewport:{width:2560,height:1080},deviceScaleFactor:1});
    const page = await context.newPage();
    page.on('pageerror', e => errors.push(e.message));
    page.on('response', r => {if(r.status() >= 400) errors.push(`${r.status()} ${r.url()}`);});
    await page.goto('http://127.0.0.1:4351/mail-ui-v1/index.html');
    await page.waitForFunction(() => [...document.images].every(i => i.complete));
    const stored = () => page.evaluate(() => JSON.parse(localStorage.getItem('wuxing-qitan-mail-ui-v1')));
    const reset = async () => {await page.locator('.demo-controls').evaluate(el => {el.open=true;}); await page.locator('#reset-demo').click();await page.locator('.demo-controls').evaluate(el=>{el.open=false;});};
    const screenshot = async name => {if(!writeArtifacts) return;await page.locator('#toast').evaluate(el=>{el.hidden=true;});await page.screenshot({path:path.join(output,name)});};
    const bounds = async label => {
      const items = await page.evaluate(()=>{const w=document.querySelector('.mail-window').getBoundingClientRect();return [...document.querySelectorAll('#claim-mail,#claim-all,#delete-mail')].map(el=>{const r=el.getBoundingClientRect();return {id:el.id,bottom:r.bottom,right:r.right,top:r.top,inside:r.bottom<=innerHeight&&r.top>=0&&r.bottom<=w.bottom&&r.top>=w.top&&r.left>=w.left&&r.right<=w.right};});});
      check(`${label}: all action buttons inside viewport and window`,items.every(item=>item.inside));
      check(`${label}: no horizontal page overflow`,await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
      return items;
    };
    if(writeArtifacts) fs.mkdirSync(output,{recursive:true});
    check('Initial current mail read independently of its pending reward', (await stored()).items.find(i=>i.id==='midautumn').read && !(await stored()).items.find(i=>i.id==='midautumn').claimed);
    const initialItems=(await stored()).items;
    check('Initial 17 letters include 12 festival examples', initialItems.length===17 && Object.keys(festivalAssets).every(id=>initialItems.some(i=>i.id===id)));
    check('Initial 14 claimable letters', await page.locator('#mail-summary').innerText().then(text=>/待领\s*14/.test(text)));
    const version2Items=(await stored()).items.filter(i=>!newSolarTerms.includes(i.id) && i.id!=='laba');
    await page.evaluate(items=>localStorage.setItem('wuxing-qitan-mail-ui-v1',JSON.stringify({version:2,category:'all',selectedId:'midautumn',items})),version2Items);
    await page.reload();
    const migrated=await stored();
    check('Version 2 storage adds three new solar terms',migrated.version===3 && newSolarTerms.every(id=>migrated.items.some(i=>i.id===id)));
    check('Version 2 storage preserves earlier deletions',!migrated.items.some(i=>i.id==='laba'));
    await reset();
    const desktopBounds=await bounds('2560 event');
    await screenshot('01-event-2560.png');
    await page.locator('#delete-mail').click();
    check('Pending attachment protects individual deletion', (await stored()).items.length===17 && /请先领取/.test(await page.locator('#toast').innerText()));
    await page.locator('#open-event').click();
    check('Event opens sample detail modal', await page.locator('#event-dialog').evaluate(el=>el.open));
    check('Sample activity is explicitly described as a preview',/非真实开放活动/.test(await page.locator('#event-dialog').innerText()));
    await screenshot('06-event-modal.png');
    await page.keyboard.press('Escape');
    check('Escape closes event modal',!(await page.locator('#event-dialog').evaluate(el=>el.open)));
    await page.locator('[data-mail-id="maintenance"]').click();
    check('Opening maintenance changes read without claiming', (await stored()).items.find(i=>i.id==='maintenance').read && !(await stored()).items.find(i=>i.id==='maintenance').claimed);
    await bounds('2560 text reward');
    await screenshot('02-text-reward-2560.png');
    await page.locator('#claim-mail').click();
    check('Single claim disables button and marks rewards', await page.locator('#claim-mail').isDisabled() && await page.locator('.reward.claimed').count()===2);
    await screenshot('03-claimed-2560.png');
    await page.reload();
    check('Claim persists across reload',await page.locator('#claim-mail').isDisabled() && (await stored()).items.find(i=>i.id==='maintenance').claimed);
    const unreadBeforeBulk=(await stored()).items.filter(i=>!i.read).length;
    await page.locator('#claim-all').click();
    check('Bulk claim counts exactly 13 eligible letters and 28 items',/13 封邮件，共 28 项附件/.test(await page.locator('#toast').innerText()));
    check('Bulk claim preserves unread state', (await stored()).items.filter(i=>!i.read).length===unreadBeforeBulk);
    check('Bulk claim skips expired and notification messages',!(await stored()).items.find(i=>i.id==='expired').claimed && !(await stored()).items.find(i=>i.id==='notice').claimed);
    check('No double claiming: bulk claim disabled after all valid claims',await page.locator('#claim-all').isDisabled());
    await reset();
    await page.locator('#clean-read').click();
    check('Clean read removes only two read messages with no valid pending attachment', (await stored()).items.length===15 && /2 封已读/.test(await page.locator('#toast').innerText()));
    check('Clean read protects read message with pending attachments', (await stored()).items.some(i=>i.id==='midautumn'));
    await page.locator('[data-mail-id="notice"]').click();
    await screenshot('05-notification-2560.png');
    check('Notification has no claim button',await page.locator('#claim-mail').count()===0);
    await page.locator('#delete-mail').click();
    check('Read notification can be deleted', !(await stored()).items.some(i=>i.id==='notice'));
    await reset();
    await page.locator('[data-category="event"]').click();
    check('Event filter contains 12 festival letters and one expired letter',await page.locator('.mail-row').count()===13);
    for(const [id,file] of Object.entries(festivalAssets)) {
      await page.locator(`[data-mail-id="${id}"]`).click();
      const art=page.locator('.event-banner > img');
      await art.evaluate(el=>new Promise(resolve=>{if(el.complete) resolve();else {el.addEventListener('load',resolve,{once:true});el.addEventListener('error',resolve,{once:true});}}));
      check(`${id} banner loads its 2098x749 image`,await art.evaluate((el,file)=>el.currentSrc.endsWith(`/assets/${file}`)&&el.naturalWidth===2098&&el.naturalHeight===749,file));
      if(newSolarTerms.includes(id)) {
        await page.locator('#open-event').click();
        const dialogArt=page.locator('#event-dialog .event-dialog-art');
        await dialogArt.evaluate(el=>new Promise(resolve=>{if(el.complete) resolve();else {el.addEventListener('load',resolve,{once:true});el.addEventListener('error',resolve,{once:true});}}));
        check(`${id} activity dialog uses the same image`,await dialogArt.evaluate((el,file)=>el.currentSrc.endsWith(`/assets/${file}`)&&el.naturalWidth===2098,file));
        await page.locator('[data-close-dialog]').last().click();
      }
    }
    await page.locator('[data-mail-id="expired"]').click();
    check('Expired mail cannot be claimed',await page.locator('#claim-mail').isDisabled() && /已过期/.test(await page.locator('#claim-mail').innerText()));
    await bounds('2560 expired');
    await screenshot('04-expired-2560.png');
    await reset();
    await page.setViewportSize({width:1920,height:1080});
    await bounds('1920 event');
    await screenshot('07-event-1920.png');
    await page.locator('#close-mail').click();
    check('Mail panel can close and reopen',await page.locator('#reopen-panel').isVisible());
    await page.locator('#reopen-mail').click();
    check('Reopened panel preserves selected mail',await page.locator('#mail-detail').getAttribute('data-current-mail')==='midautumn');
    const mobileContext=await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true});
    const mobile=await mobileContext.newPage();
    mobile.on('pageerror',e=>errors.push(e.message));
    await mobile.goto('http://127.0.0.1:4351/mail-ui-v1/index.html');
    await mobile.waitForFunction(()=>[...document.images].every(i=>i.complete));
    const mobileStored=()=>mobile.evaluate(()=>JSON.parse(localStorage.getItem('wuxing-qitan-mail-ui-v1')));
    check('Mobile opening inbox does not mark unseen event mail as read',!(await mobileStored()).items.find(i=>i.id==='midautumn').read);
    check('390px inbox has no horizontal overflow',await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    if(writeArtifacts) await mobile.screenshot({path:path.join(output,'08-mobile-inbox.png'),fullPage:true});
    await mobile.locator('[data-mail-id="midautumn"]').click();
    check('Mobile selected mail detail opens and marks read',await mobile.locator('#mail-detail').isVisible() && (await mobileStored()).items.find(i=>i.id==='midautumn').read);
    check('Mobile attachment names are visible',await mobile.locator('.reward-name').count()===4);
    check('390px detail has no horizontal overflow',await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    if(writeArtifacts) await mobile.screenshot({path:path.join(output,'09-mobile-event.png'),fullPage:true});
    const mobileLayout=await mobile.evaluate(()=>({window:document.querySelector('.mail-window').getBoundingClientRect().toJSON(),reader:document.querySelector('.mail-reader').getBoundingClientRect().toJSON(),footer:document.querySelector('.detail-footer').getBoundingClientRect().toJSON(),viewport:innerHeight}));
    check('390px claim control stays inside first viewport',await mobile.locator('#claim-mail').evaluate(el=>el.getBoundingClientRect().bottom<=innerHeight));
    await mobile.locator('#claim-mail').click();
    check('Mobile touch claim disables control',await mobile.locator('#claim-mail').isDisabled());
    await mobile.locator('#back-to-list').click();
    check('Mobile returns to inbox',await mobile.locator('.inbox').isVisible());
    check('No browser errors or failed assets',errors.length===0);
    const report={passed:results.length,checks:results,errors,desktopBounds,mobileLayout,screenshots:writeArtifacts?fs.readdirSync(output):[],preview:'http://localhost:4351/mail-ui-v1/index.html'};
    if(writeArtifacts) fs.writeFileSync(path.join(__dirname,'validation.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report));
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
