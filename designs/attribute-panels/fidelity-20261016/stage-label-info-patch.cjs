const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=__dirname,skill='E:/work/image/designs/class-skills-20260928/fidelity-20261016',client='E:/work/mmorpg-client';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const specs=[
 {dir:root,name:'AttributePanel.Fidelity.cs',dest:'Assets/Scripts/UI/Ugui/Attribute/AttributePanel.Fidelity.cs',edit:s=>s.replace('t.text="技能";AttributeFidelityLayout.Font(t,29);','t.text="技能";AttributeFidelityLayout.Place(t.rectTransform,0,0,145,68.8f);AttributeFidelityLayout.Font(t,29);')},
 {dir:skill,name:'SkillPanel.Fidelity.cs',dest:'Assets/Scripts/UI/Ugui/Skills/SkillPanel.Fidelity.cs',edit:s=>s.replace('AttributeFidelityLayout.Place(_classInfo.rectTransform,430,155,1200,26);AttributeFidelityLayout.Font(_classInfo,18,AttributeFidelityLayout.Muted,true);_classInfo.textWrappingMode=TextWrappingModes.NoWrap;','AttributeFidelityLayout.Place(_classInfo.rectTransform,81.6f,_state?.Context?.IsPet==true?210:700,270,100);AttributeFidelityLayout.Font(_classInfo,22,AttributeFidelityLayout.Muted,true);_classInfo.textWrappingMode=TextWrappingModes.Normal;')}
];
if(!process.argv.includes('--compile-only')){
const files=[],guards=[];
for(const spec of specs){const from=client+'/'+spec.dest;let s=fs.readFileSync(from,'utf8');const out=spec.edit(s);if(s===out)throw Error('Expected exact edit missing: '+spec.name);const staged=root+'/integration/label-info-patch/'+spec.name;fs.mkdirSync(path.dirname(staged),{recursive:true});fs.writeFileSync(staged,out);fs.writeFileSync(spec.dir+'/'+spec.name,out);fs.writeFileSync(spec.dir+'/integration/'+spec.name,out);guards.push({source:from,sha256:hash(from)});files.push({source:path.relative(root,staged).replaceAll('\\','/'),destination:spec.dest,sha256:hash(staged)});}
const manifest={status:'ready-for-install',checkedAtUtc:new Date().toISOString(),clientModified:false,unityLaunched:false,guards,files,scope:'Presentation only: ClassInfo below the four-class sidebar (pet context uses the free upper sidebar); attribute SkillTabPlate label exactly matches its145x68.8 button. Pet tab labels already match140x68.8 and need no edit.'};
fs.writeFileSync(root+'/label-info-patch-install-manifest.json',JSON.stringify(manifest,null,2)+'\n');console.log(JSON.stringify(manifest,null,2));
}
let compile=fs.readFileSync('E:/work/image/qdao_ui_redesign_v5/fidelity-battle-20261016/compile-staged.ps1','utf8');
const begin=compile.indexOf('$stagedNames='),end=compile.indexOf('$runtime=',begin);
compile=compile.slice(0,begin)+`$stagedNames=@('AttributePanel.Fidelity.cs','SkillPanel.Fidelity.cs')
$sources=@(Get-ChildItem (Join-Path $Client 'Assets/Scripts') -Recurse -Filter *.cs | ForEach-Object {
 if($_.Name -in $stagedNames){'"'+(Join-Path $package ('integration/label-info-patch/'+$_.Name))+'"'}else{'"'+$_.FullName+'"'}
})
`+compile.slice(end);
compile=compile.replace("$qa=Join-Path $package 'qa'","$qa=Join-Path $package 'qa/label-info-patch'").replaceAll('BattleFidelity.Runtime','LabelInfoFidelity.Runtime');
fs.writeFileSync(root+'/compile-label-info-patch.ps1',compile);
