const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
(async()=>{
 const root='E:/work/image/qdao_original_roster_v13/candidate/03_lotus_healer_girl';
 const out=path.join(root,'review/browser-final-candidate-v2');fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({channel:'msedge',headless:true});
 try {
 const page=await browser.newPage({viewport:{width:1400,height:960}});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://127.0.0.1:8874/');
 await page.waitForFunction(()=>document.querySelector('#character option[value="03_lotus_healer_girl"]'));
 await page.selectOption('#character','03_lotus_healer_girl');
 const observed=[];
 for(const d of ['S','SE','E','NE','N','NW','W','SW']){
  await page.selectOption('#direction',d);
  await page.waitForFunction(d=>window.previewDebug?.getState().direction===d&&window.previewDebug.getState().loaded===16,d);
  await page.selectOption('#speed','1');await page.uncheck('#large');
  await page.evaluate(()=>window.previewDebug.setPhase(0));
  await page.screenshot({path:path.join(out,d+'-normal-frame01.png')});
  const phases=[];for(let phase=0;phase<=480;phase+=30){
   await page.evaluate(p=>window.previewDebug.setPhase(p),phase);
   phases.push({requestedPhaseMs:phase,...await page.evaluate(()=>window.previewDebug.getState())});
  }
  await page.evaluate(()=>window.previewDebug.setPhase(0));await page.click('#play');
  const playback=await page.evaluate(()=>new Promise(resolve=>{
   const samples=[];const start=performance.now();
   function sample(now){samples.push({elapsedMs:now-start,...window.previewDebug.getState()});
    if(now-start>=1000)resolve(samples);else requestAnimationFrame(sample);}
   requestAnimationFrame(sample);
  }));
  await page.evaluate(()=>window.previewDebug.setPhase(0));await page.check('#large');
  for(const frame of [1,9,15,16]){
   await page.evaluate(p=>window.previewDebug.setPhase(p),(frame-1)*30);
   await page.screenshot({path:path.join(out,d+'-large-frame'+String(frame).padStart(2,'0')+'.png')});
  }
  observed.push({direction:d,phaseObservations:phases,actualNormalPlayback:playback,uniquePlayedFrames:[...new Set(playback.map(x=>x.frame))].sort((a,b)=>a-b)});
 }
 const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
 const result={recordedAtUtc:new Date().toISOString(),scope:'Actual complete 03 candidate PNG loading, exact phase control and normal-speed requestAnimationFrame playback observation. This is browser observation, not Unity validation or final visual approval.',manifestSha256:sha(path.join(root,'manifest.json')),qcSha256:sha(path.join(root,'qc.json')),observations:observed,jsErrors:errors,visualReview:'pending'};
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify({directions:observed.map(x=>({direction:x.direction,loaded:x.phaseObservations[0].loaded,uniquePlayedFrames:x.uniquePlayedFrames})),jsErrors:errors,visualReview:'pending'}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});



