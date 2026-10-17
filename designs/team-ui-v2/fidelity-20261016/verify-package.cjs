const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=__dirname,client='E:/work/mmorpg-client';
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const baseline=JSON.parse(fs.readFileSync(path.join(root,'source-checkout.json'),'utf8'));
const sourceChecks=baseline.inputs.map(input=>({...input,currentSha256:hash(input.source),unchangedSinceCheckout:hash(input.source)===input.sha256}));
const old=fs.readFileSync(sourceChecks[0].source,'utf8'),staged=fs.readFileSync(path.join(root,'integration/TeamWindow.cs'),'utf8');
function segment(code,start,end){const a=code.indexOf(start),b=code.indexOf(end,a+start.length);if(a<0||b<0)throw Error(start);return code.slice(a,b).replaceAll('\r\n','\n');}
const checks=[
 ['public API and event surface','        public const int RowsPerPage','        private static readonly Color'],
 ['state/show/hide/reset and selection lifecycle','        public void SetState','        private bool CanAct'],
 ['permission gates','        private bool CanAct','        private void MovePage'],
 ['footer, pagination and real match status','        private string StatusText','        private void RenderNoTeam'],
 ['all action intents, dialogs and match/backfill transaction','        private void Decide','        private static void Portrait']
].map(([name,start,end])=>({name,unchanged:segment(old,start,end)===segment(staged,start,end)}));
const assets=JSON.parse(fs.readFileSync(path.join(root,'runtime-assets.json'),'utf8')).images;
const assetChecks=assets.map(asset=>{
 const file=path.join(root,'runtime-assets',asset.file),meta=fs.readFileSync(file+'.meta','utf8');
 return {file:asset.file,sha256:hash(file),matchesRecord:hash(file)===asset.sha256,
  cleanSingleSprite:meta.includes('spriteMode: 1')&&meta.includes('sprites: []')&&!meta.includes('application_card_0'),
  guid:asset.guid,guidMatches:meta.includes('guid: '+asset.guid),noMipmaps:meta.includes('enableMipMap: 0'),uncompressed:meta.includes('textureCompression: 0')};
});
const compile=JSON.parse(fs.readFileSync(path.join(root,'qa/compile-report.json'),'utf8'));
const files=[
 ...['TeamWindow.cs','TeamUiArt.cs'].map(name=>({source:'integration/'+name,destination:'Assets/Scripts/UI/Ugui/Team/'+name,sha256:hash(path.join(root,'integration',name)),operation:'replace only if baseline SHA still matches'})),
 ...['TeamFidelityVerification.cs','TeamFidelityVerification.cs.meta'].map(name=>({source:'integration/'+name,destination:'Assets/Editor/Team/'+name,sha256:hash(path.join(root,'integration',name)),operation:'add native capture utility'})),
 ...assets.flatMap(asset=>[asset.file,asset.file+'.meta'].map(name=>({source:'runtime-assets/'+name,destination:'Assets/Resources/UI/Ugui/TeamV2/Fidelity20261016/'+name,sha256:hash(path.join(root,'runtime-assets',name)),operation:'add final runtime sprite'})))
];
const report={checkedAtUtc:new Date().toISOString(),status:sourceChecks.every(c=>c.unchangedSinceCheckout)&&checks.every(c=>c.unchanged)&&assetChecks.every(c=>c.matchesRecord&&c.cleanSingleSprite&&c.guidMatches&&c.noMipmaps&&c.uncompressed)&&compile.runtimeExit===0&&compile.editorExit===0?'ready-for-install':'needs-attention',
 clientModified:false,unityLaunched:false,nativeCaptureRun:false,sourceChecks,preservedBehaviorChecks:checks,assetChecks,
 compile,captureEntrypoint:'TeamFidelityVerification.Capture',captureOutputDirectory:'E:/work/image/designs/team-ui-v2/fidelity-20261016/qa',
 captureStates:['explicit approved-art preview','authoritative identity portrait fixture','member permissions fixture','received invitations fixture','unavailable production without fake identities'],
 captureResolutions:[[2560,1080],[1920,1080]],files};
fs.writeFileSync(path.join(root,'installation-manifest.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:report.status,sourceConflicts:sourceChecks.filter(c=>!c.unchangedSinceCheckout),preservedBehaviorChecks:checks,assetCount:assets.length,files:files.length}));
if(report.status!=='ready-for-install')process.exitCode=1;
