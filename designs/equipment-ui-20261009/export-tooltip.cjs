const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const sharp = require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root = __dirname;
const original = 'C:/Users/luyua/.codex/generated_images/01a120d0-6ad5-76c3-ba1a-9d08e57e3575/exec-a2636740-5a2b-4c84-b7df-79463d8751ae.png';
const sha = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const json = (file,value) => fs.writeFileSync(file,JSON.stringify(value,null,2)+'\n');
async function main() {
  const source = path.join(root,'tooltip-paper-source.png');
  if (!fs.existsSync(source)) fs.copyFileSync(original,source);
  const config = JSON.parse(fs.readFileSync('E:/work/image/config/image-generation.json','utf8'));
  const metadata = await sharp(source).metadata();
  const record = {file:'tooltip-paper-source.png',sha256:sha(source),generatedAt:fs.statSync(original).mtime.toISOString(),width:metadata.width,height:metadata.height,format:'png',tool:'image_gen.imagegen',route:'builtin',configSnapshot:config,submittedParameters:{model:null,quality:null,transparent_background:true},actualModel:null,actualQuality:null,evidence:{outputFile:original,resultID:'exec-a2636740-5a2b-4c84-b7df-79463d8751ae',verifiedNativeAlpha:true},unverifiedReason:'宿主管理；工具未开放 model/quality 选择器，也未披露可核实的实际型号与画质。',prompt:'prompts/tooltip-paper.txt',references:[{file:'E:/work/image/designs/gameplay-ui/02-inventory.png',purpose:'primary approved art style'},{file:'E:/work/image/designs/equipment-ui-20261008/skin-atlas.png',purpose:'existing frame language; new ivory body requested'}]};
  json(source+'.generation.json',record);
  // Crop transparent margin, reduce uniformly, then extend only the stretchable center.
  const base = await sharp(source).extract({left:64,top:0,width:896,height:1492}).resize(448,746).png().toBuffer();
  const top = await sharp(base).extract({left:0,top:0,width:448,height:160}).png().toBuffer();
  const center = await sharp(base).extract({left:0,top:160,width:448,height:506}).resize(448,690,{fit:'fill'}).png().toBuffer();
  const bottom = await sharp(base).extract({left:0,top:666,width:448,height:80}).png().toBuffer();
  const dest = path.join(root,'sprites','tooltip_panel.png');
  await sharp({create:{width:448,height:930,channels:4,background:{r:0,g:0,b:0,alpha:0}}}).composite([{input:top,top:0,left:0},{input:center,top:160,left:0},{input:bottom,top:850,left:0}]).png().toFile(dest);
  const stats = await sharp(dest).stats();
  const derived = {file:'tooltip_panel.png',sha256:sha(dest),width:448,height:930,format:'png',derivedFrom:{file:'../tooltip-paper-source.png',sha256:record.sha256,generationRecord:'../tooltip-paper-source.png.generation.json'},operation:{crop:[64,0,896,1492],uniformResize:[448,746],verticalCenterStretch:{top:160,bottom:80,finalHeight:930}},unityBorder:[48,80,48,160],alphaRange:[stats.channels[3].min,stats.channels[3].max]};
  json(dest+'.generation.json',derived);
  const targets = ['E:/work/mmorpg-client','E:/work/mmorpg-client-equip'];
  const integrations = [];
  for(const target of targets){
    const file = path.join(target,'Assets/Resources/UI/Ugui/EquipmentV1/tooltip_panel.png');
    fs.copyFileSync(dest,file);
    const metaFile=file+'.meta';
    let meta=fs.readFileSync(metaFile,'utf8');
    const guid=meta.match(/^guid: (.+)$/m)[1];
    meta=meta.replace(/spriteBorder: \{[^}]+\}/,'spriteBorder: {x: 48, y: 80, z: 48, w: 160}').replace(/userData: .*/,'userData: GPT Image equipment UI paper card; source E:/work/image/designs/equipment-ui-20261009');
    fs.writeFileSync(metaFile,meta);
    integrations.push({file,sha256:sha(file),preservedGuid:guid});
  }
  json(path.join(root,'sprite-manifest.json'),{source:record.file,items:[derived],integrations,reusedResources:'../equipment-ui-20261008/sprite-manifest.json'});
  console.log(JSON.stringify({native:[metadata.width,metadata.height],export:[448,930],alphaRange:derived.alphaRange,border:derived.unityBorder,integrations},null,2));
}
main().catch(e=>{console.error(e);process.exit(1)});
