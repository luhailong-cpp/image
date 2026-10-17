const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=__dirname,skill='E:/work/image/designs/class-skills-20260928/fidelity-20261016',client='E:/work/mmorpg-client';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const definitions=[
 ['Attribute/AttributeFidelityLayout.cs',path.join(root,'AttributeFidelityLayout.cs')],
 ['Attribute/AttributePanel.Fidelity.cs',path.join(root,'AttributePanel.Fidelity.cs')],
 ['Skills/SkillPanel.Fidelity.cs',path.join(skill,'SkillPanel.Fidelity.cs')],
 ['Skills/SkillPanel.cs',null]
];
const files=[],guards=[];
for(const [relative,canonical] of definitions){
 const source=client+'/Assets/Scripts/UI/Ugui/'+relative,name=path.basename(relative),destination=path.join(root,'integration',name);
 guards.push({source,sha256:hash(source)});
 if(canonical)fs.copyFileSync(canonical,destination);
 else {let code=fs.readFileSync(source,'utf8');if(!code.includes('_fidelityCanPreviewClasses = previewClass != null;'))code=code.replace('_upgradeAction = upgrade;','_upgradeAction = upgrade;\n            _fidelityCanPreviewClasses = previewClass != null;');fs.writeFileSync(destination,code);}
 files.push({source:'integration/'+name,destination:'Assets/Scripts/UI/Ugui/'+relative,sha256:hash(destination)});
}
fs.writeFileSync(path.join(root,'layout-selector-patch-install-manifest.json'),JSON.stringify({status:'ready-for-install',checkedAtUtc:new Date().toISOString(),clientModified:false,unityLaunched:false,
 guards,files,scope:'Resolve actual *Plate control roots so horizontal navigation/Equipment placement applies; visible read-only class sidebar retains original preview callback and permission; actual60x60 slider hit area retained.'},null,2)+'\n');
console.log('Four-file selector/sidebar patch staged from current installed sources.');
