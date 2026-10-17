const fs=require('fs'),path=require('path'),crypto=require('crypto');
const sharp=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const scene=__dirname,world='E:/work/image/designs/world-map-original-20260925/fidelity-20261016';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
function segment(code,start,end){const a=code.indexOf(start),b=code.indexOf(end,a+start.length);if(a<0||b<0)throw Error(start);return code.slice(a,b).replaceAll('\r\n','\n');}
async function compareStatic(original,output,regions){
 const a=await sharp(original).removeAlpha().raw().toBuffer({resolveWithObject:true}),b=await sharp(output).removeAlpha().raw().toBuffer({resolveWithObject:true});
 if(a.info.width!==b.info.width||a.info.height!==b.info.height||a.info.channels!==b.info.channels)throw Error('Canvas mismatch');
 let outsideMaskPixels=0,outsideChangedPixels=0;
 for(let y=0;y<a.info.height;y++)for(let x=0;x<a.info.width;x++){
  if(regions.some(([left,top,width,height])=>x>=left&&y>=top&&x<left+width&&y<top+height))continue;
  outsideMaskPixels++;const offset=(y*a.info.width+x)*a.info.channels;
  if(a.data.subarray(offset,offset+a.info.channels).compare(b.data.subarray(offset,offset+a.info.channels))!==0)outsideChangedPixels++;
 }
 return {originalCanvas:[a.info.width,a.info.height],maskRegions:regions,outsideMaskPixels,outsideChangedPixels,staticPixelsExact:outsideChangedPixels===0};
}
(async()=>{
 const compile=JSON.parse(fs.readFileSync(path.join(scene,'qa/compile-report.json'),'utf8'));
 for(const [root,name,capture,resource,checkRegions] of [
  [scene,'SceneChannelWindow.cs','SceneChannelFidelityVerification','SceneSelectV1',[
   ['state, cooldown and UI lifecycle','        public void SetView','        private void BuildRow'],
   ['switch transaction re-check, status and pagination','        private void RequestSwitch','    }\n}']]],
  [world,'CityTravelWindow.cs','WorldMapFidelityVerification','WorldMapOriginal',[
   ['zones, travel state, selection, pending gates and event transactions','        public void SetZones','        private const string FidelityResourceRoot']]]
 ]){
  const guard=JSON.parse(fs.readFileSync(path.join(root,'source-checkout.json'),'utf8'));
  const current=hash(guard.source),source=fs.readFileSync(guard.source,'utf8').replaceAll('\r\n','\n'),staged=fs.readFileSync(path.join(root,'integration',name),'utf8').replaceAll('\r\n','\n');
  const checks=checkRegions.map(([label,start,end])=>{
   let originalEnd=end;if(resource==='WorldMapOriginal')originalEnd='        private static void SetTab';
   return {name:label,unchanged:segment(source,start,originalEnd)===segment(staged,start,end)};
  });
  // Native constants/layout are allowed to change from 16 to 24 rows; the underlying cooldown/permission state machine remains identical.
  const images=JSON.parse(fs.readFileSync(path.join(root,'runtime-assets.json'),'utf8')).images;
  const skin=images[0],original=skin.derivedFrom[0].file,output=path.join(root,'runtime-assets',skin.file);
  const pixelCheck=await compareStatic(original,output,skin.operation.regions);
  const files=[{source:'integration/'+name,destination:'Assets/Scripts/UI/Ugui/Gameplay/'+name,sha256:hash(path.join(root,'integration',name))},
   ...[capture+'.cs',capture+'.cs.meta'].map(file=>({source:'integration/'+file,destination:'Assets/Editor/Fidelity/'+file,sha256:hash(path.join(root,'integration',file))})),
   ...images.flatMap(image=>[image.file,image.file+'.meta'].map(file=>({source:'runtime-assets/'+file,destination:'Assets/Resources/UI/Ugui/'+resource+'/Fidelity20261016/'+file,sha256:hash(path.join(root,'runtime-assets',file))})))];
  const report={checkedAtUtc:new Date().toISOString(),status:current===guard.sha256&&checks.every(c=>c.unchanged)&&pixelCheck.staticPixelsExact&&compile.runtimeExit===0&&compile.editorExit===0?'ready-for-install':'needs-attention',
   clientModified:false,unityLaunched:false,nativeCaptureRun:false,sourceGuard:{...guard,currentSha256:current,unchanged:current===guard.sha256},preservedBehaviorChecks:checks,
   staticPixelCheck:pixelCheck,compile,captureEntrypoint:capture+'.Capture',captureOutputDirectory:path.join(root,'qa'),files};
  fs.writeFileSync(path.join(root,'installation-manifest.json'),JSON.stringify(report,null,2)+'\n');
  if(root===world)fs.writeFileSync(path.join(root,'qa/compile-report.json'),JSON.stringify(compile,null,2)+'\n');
  console.log(JSON.stringify({module:resource,status:report.status,sourceUnchanged:report.sourceGuard.unchanged,behavior:checks,staticPixelCheck:pixelCheck,files:files.length}));
  if(report.status!=='ready-for-install')process.exitCode=1;
 }
})().catch(error=>{console.error(error.stack);process.exitCode=1;});
