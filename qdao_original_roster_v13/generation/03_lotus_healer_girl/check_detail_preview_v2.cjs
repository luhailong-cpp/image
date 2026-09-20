const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
(async()=>{
const root='E:/work/image/qdao_original_roster_v13/candidate/03_lotus_healer_girl',out=path.join(root,'review/browser-final-candidate-v2/detail');fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({channel:'msedge',headless:true});
try { const page=await browser.newPage({viewport:{width:1400,height:960}});
await page.goto('http://127.0.0.1:8874/');await page.selectOption('#character','03_lotus_healer_girl');
const records=[];
for(const d of ['N','NE','E','SE','S','SW','W','NW']){
await page.selectOption('#direction',d);await page.waitForFunction(d=>window.previewDebug?.getState().direction===d&&window.previewDebug.getState().loaded===16,d);
await page.uncheck('#large');await page.evaluate(()=>window.previewDebug.setPhase(0));
await page.locator('.panes').screenshot({path:path.join(out,d+'-normal-idle-and-walk.png')});
await page.check('#large');
for(const f of (d === "SW" ? [1,5,6,7,8,9,10,11,12,13,15,16] : [1,5,9,13,15,16])){
await page.evaluate(p=>window.previewDebug.setPhase(p),(f-1)*30);
const filename=d+'-large-'+String(f).padStart(2,'0')+'.png';
await page.locator('#walk').screenshot({path:path.join(out,filename)});
records.push({direction:d,frame:f,file:filename,...await page.evaluate(()=>window.previewDebug.getState())});
}
}
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
fs.writeFileSync(path.join(out,'capture.json'),JSON.stringify({recordedAtUtc:new Date().toISOString(),manifestSha256:sha(path.join(root,'manifest.json')),records,scope:'Actual browser element screenshots for human/model visual inspection; not a visual approval or Unity validation.'},null,2));
console.log(JSON.stringify({captured:records.length,normal:8}));
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});

