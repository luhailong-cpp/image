const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=__dirname,skill='E:/work/image/designs/class-skills-20260928/fidelity-20261016',client='E:/work/mmorpg-client';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
function normalize(code){return code.replaceAll('\r\n','\n').replaceAll('public sealed partial class','public sealed class').replace(/^            ApplyFidelityLayout\(\);\n/gm,'');}
function excludeMethod(code,start,end){const a=code.indexOf(start),b=code.indexOf(end,a+start.length);return code.slice(0,a)+'/* point stepper presentation */\n'+code.slice(b);}
const sources=['AttributePanel.cs','PetPanel.cs','SkillPanel.cs'].map(name=>{
 const folder=name==='SkillPanel.cs'?skill:root,guard=JSON.parse(fs.readFileSync(path.join(folder,name+'.source.json'),'utf8'));
 let a=normalize(fs.readFileSync(guard.source,'utf8')),b=normalize(fs.readFileSync(path.join(folder,'integration',name),'utf8'));
 if(name==='PetPanel.cs'){
  b=b.replaceAll('FidelityPetGeometry.','PetUiStyle.').replace('var anchored = (Vector2)_root.InverseTransformPoint(row.Rect.TransformPoint(UnityEngine.Vector3.zero));','var anchored = row.Rect.anchoredPosition;');
  for(const marker of ['a','b']){if(marker==='a')a=excludeMethod(a,'        private UiPointRow CreatePointStepper(','        private static UiTextButton CreateStep(');else b=excludeMethod(b,'        private UiPointRow CreatePointStepper(','        private static UiTextButton CreateStep(');}
 }
 if(name==='SkillPanel.cs')b=b.replace('private const float ListHeight = 500f','private const float ListHeight = 430f');
 return {name,...guard,currentSha256:hash(guard.source),sourceUnchanged:hash(guard.source)===guard.sha256,
  authoritativeCodePreserved:a===b,presentationExceptions:name==='PetPanel.cs'?['local geometry constants','visible slider creation using unchanged UiPointRow model','tooltip coordinate transformation']:name==='SkillPanel.cs'?['viewport height 430 to 500']:[]};
});
const sprites=fs.readdirSync(client+'/Assets/Resources/UI/Ugui/AttributesPaintedV2').filter(name=>name.endsWith('.png')).map(name=>{
 const target=client+'/Assets/Resources/UI/Ugui/AttributesPaintedV2/'+name,source='E:/work/image/designs/attribute-panels/v2-painted/unity-slices/png/'+name;
 return {name,clientSha256:hash(target),sourceExists:fs.existsSync(source),sourceSha256:fs.existsSync(source)?hash(source):null,sameSourcePixels:fs.existsSync(source)&&hash(source)===hash(target)};
});
const compile=JSON.parse(fs.readFileSync(path.join(root,'qa/compile-report.json'),'utf8'));
for(const folder of [root,skill]){
 const files=fs.readdirSync(path.join(folder,'integration')).map(name=>{
  const base=name.replace('.meta',''),module=base.startsWith('PetPanel')?'Pet':base.startsWith('SkillPanel')?'Skills':'Attribute';
  return {source:'integration/'+name,destination:'Assets/Scripts/UI/Ugui/'+module+'/'+name,sha256:hash(path.join(folder,'integration',name))};
 });
 const report={checkedAtUtc:new Date().toISOString(),status:sources.every(s=>s.sourceUnchanged&&s.authoritativeCodePreserved)&&compile.runtimeExit===0?'ready-for-install':'needs-attention',
  clientModified:false,unityLaunched:false,nativeCaptureRun:false,sources,compile,newRasterAssets:0,globalStyleFilesModified:[],
  designReferences:['designs/attribute-panels/v10-preview/index.html','designs/attribute-panels/v10-preview/panel.css','designs/class-skills-20260928/index.html','designs/class-skills-20260928/styles.css'],
  spriteAudit:sprites,files,dependencies:folder===skill?['attribute-panels/fidelity-20261016 AttributeFidelityLayout.cs']:[],
  acceptance:'Install both manifests together; preserve existing source .meta. Re-run native captures after installation before claiming visual completion.'};
 fs.writeFileSync(path.join(folder,'installation-manifest.json'),JSON.stringify(report,null,2)+'\n');
 if(folder===skill)fs.writeFileSync(path.join(folder,'qa/compile-report.json'),JSON.stringify(compile,null,2)+'\n');
 console.log(JSON.stringify({folder,status:report.status,files:files.length,sources:sources.map(s=>({name:s.name,guard:s.sourceUnchanged,behavior:s.authoritativeCodePreserved})),sprites:sprites.length,sameSource:sprites.filter(s=>s.sameSourcePixels).length}));
}
