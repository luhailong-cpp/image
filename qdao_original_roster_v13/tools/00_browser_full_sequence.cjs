const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root='E:/work/image/qdao_original_roster_v13',id='00_reference_topright_boy',dir=root+'/review/'+id+'/browser-final-candidate';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const mpath=root+'/candidate/'+id+'/manifest.json',mp=fs.readFileSync(mpath),manifest=JSON.parse(mp);
const results={status:'running',scope:'actual browser canvas normal/enlarged sequential capture and resource SHA check, no video claim',manifest_sha256:sha(mp),start_utc:new Date().toISOString(),directions:[],response_hashes:{},errors:[]},pending=[];
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});const page=await browser.newPage({viewport:{width:1180,height:1050},deviceScaleFactor:1});
page.on('pageerror',e=>results.errors.push(String(e)));page.on('response',r=>{const marker='/candidate/'+id+'/';if(r.url().includes(marker)&&r.status()===200)pending.push(r.body().then(b=>{results.response_hashes[r.url().split(marker)[1]]=sha(b);}));});
await page.goto('http://127.0.0.1:8874/',{waitUntil:'networkidle'});await page.selectOption('#character',id);
for(const d of ['N','NE','E','SE','S','SW','W','NW']){
 await page.selectOption('#direction',d);await page.waitForFunction(d=>previewDebug.getState().direction===d&&previewDebug.getState().loaded===16&&!document.querySelector('#status').textContent.includes('正在'),d);
 const captures=[];
 for(const large of [false,true]){
  await page.locator('#large').setChecked(large);
  for(let n=1;n<=16;n++){await page.evaluate(ms=>previewDebug.setPhase(ms),(n-1)*30);const name=d+'-'+(large?'large':'normal')+'-canvas-'+String(n).padStart(2,'0')+'.png';const buf=await page.locator('#walk').screenshot({path:path.join(dir,name)});captures.push({frame:n,large,path:name,sha256:sha(buf)});}
 }
 results.directions.push({direction:d,captures,state:await page.evaluate(()=>previewDebug.getState())});
}
await Promise.all(pending);
for(const f of manifest.files.filter(f=>f.path.startsWith('idle/')||/^walk\/[^/]+\/\d\d.png$/.test(f.path))){
 if(results.response_hashes[f.path]!==f.sha256)throw Error('Actual resource SHA mismatch '+f.path);
}
if(sha(fs.readFileSync(mpath))!==results.manifest_sha256)throw Error('Candidate changed while captured');
if(results.errors.length)throw Error('JS errors');
results.status='passed_actual_136_resources_and_256_canvas_captures';results.finished_utc=new Date().toISOString();fs.writeFileSync(path.join(dir,'browser-sequence-report.json'),JSON.stringify(results,null,2));await browser.close();console.log(JSON.stringify({status:results.status,manifest_sha256:results.manifest_sha256,captures:256,resources:Object.keys(results.response_hashes).length}));})().catch(e=>{results.status='failed';results.failure=String(e);fs.writeFileSync(path.join(dir,'browser-sequence-report.json'),JSON.stringify(results,null,2));console.error(e);process.exit(1);});
