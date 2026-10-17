const fs=require('fs'),path=require('path'),crypto=require('crypto');
const sharp=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=__dirname;
const original='C:/Users/luyua/.codex/generated_images/01a11b28-5cb7-7961-b9c3-e205ee7ea915/exec-f57072b6-0156-4e5b-85e9-bde577af3d22.png';
const source=path.join(root,'equipment-icons.png');fs.copyFileSync(original,source);
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
async function main(){
const m=await sharp(source).metadata();
const record={file:'equipment-icons.png',sha256:sha(source),generatedAt:fs.statSync(original).mtime.toISOString(),width:m.width,height:m.height,format:'png',tool:'image_gen.imagegen',route:'builtin',configSnapshot:JSON.parse(fs.readFileSync('E:/work/image/config/image-generation.json','utf8')),submittedParameters:{model:null,quality:null,transparent_background:true},actualModel:null,actualQuality:null,evidence:{outputFile:original},unverifiedReason:'宿主管理，工具未披露可核实型号及质量。',prompt:'equipment-icons.prompt.txt',references:[{file:'E:/work/image/designs/gameplay-ui/02-inventory.png',purpose:'primary style'}]};
fs.writeFileSync(source+'.generation.json',JSON.stringify(record,null,2));
for(const [name,left,width] of [['icon_sword',0,800],['icon_boots',800,736]]){
const dest=path.join(root,'sprites',name+'.png');
await sharp(source).extract({left,top:64,width,height:896}).resize(600,600,{fit:'contain',background:{r:0,g:0,b:0,alpha:0}}).png().toFile(dest);
const provenance={file:name+'.png',sha256:sha(dest),width:600,height:600,derivedFrom:{file:'../equipment-icons.png',sha256:record.sha256,generationRecord:'../equipment-icons.png.generation.json'},operation:{type:'crop and aspect-preserving resize/transparent pad',crop:{left,top:64,width,height:896},nativeResolution:false}};
fs.writeFileSync(dest+'.generation.json',JSON.stringify(provenance,null,2));
const guid=crypto.createHash('md5').update('equipment-ui-20261008/'+name).digest('hex');
let meta=fs.readFileSync('E:/work/mmorpg-client/Assets/Resources/UI/Ugui/EquipmentV1/checkbox_off.png.meta','utf8').replace(/[a-f0-9]{32}/g,guid);
for(const t of ['E:/work/mmorpg-client','E:/work/mmorpg-client-equip']){const d=path.join(t,'Assets/Resources/UI/Ugui/EquipmentV1',name+'.png');fs.copyFileSync(dest,d);fs.writeFileSync(d+'.meta',meta);}
console.log(name,provenance.sha256);
}
}
main().catch(e=>{console.error(e);process.exit(1)});
