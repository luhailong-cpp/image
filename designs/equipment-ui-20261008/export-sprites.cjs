const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const sharp = require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root = __dirname;
const source = path.join(root, 'skin-atlas.png');
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const config = JSON.parse(fs.readFileSync('E:/work/image/config/image-generation.json', 'utf8'));
const refs = [
  ['E:/work/image/designs/gameplay-ui/02-inventory.png','primary style'],
  ['E:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png','primary style'],
  ['C:/Users/luyua/AppData/Local/Temp/codex-clipboard-8fb5197b-bd85-4b31-bb01-af834c7ec336.png','function only'],
  ['C:/Users/luyua/AppData/Local/Temp/codex-clipboard-7f766e1b-cfaf-42f6-b617-831b2d9f0bac.png','function only'],
];
const targets = ['E:/work/mmorpg-client','E:/work/mmorpg-client-equip'];
const items = [
  ['wish_panel',24,24,1040,728,[65,60,45,120]],
  ['tooltip_panel',1064,24,448,930,[48,74,48,100]],
  ['button_primary',48,778,372,100,[58,38,58,38]],
  ['button_secondary',428,778,372,100,[58,38,58,38]],
  ['checkbox_off',814,780,98,98,[0,0,0,0]],
  ['checkbox_on',936,780,98,98,[0,0,0,0]],
  ['close',48,892,104,104,[0,0,0,0]],
];
function meta(guid,border) {
return `fileFormatVersion: 2\nguid: ${guid}\nTextureImporter:\n  externalObjects: {}\n  serializedVersion: 13\n  mipmaps:\n    enableMipMap: 0\n    sRGBTexture: 1\n  isReadable: 0\n  textureSettings:\n    serializedVersion: 2\n    filterMode: 1\n    aniso: 1\n    wrapU: 1\n    wrapV: 1\n    wrapW: 1\n  nPOTScale: 0\n  spriteMode: 1\n  spriteMeshType: 1\n  spritePixelsToUnits: 100\n  spritePivot: {x: 0.5, y: 0.5}\n  spriteBorder: {x: ${border[0]}, y: ${border[1]}, z: ${border[2]}, w: ${border[3]}}\n  alphaUsage: 1\n  alphaIsTransparency: 1\n  textureType: 8\n  textureShape: 1\n  maxTextureSize: 2048\n  platformSettings:\n  - serializedVersion: 4\n    buildTarget: DefaultTexturePlatform\n    maxTextureSize: 2048\n    textureFormat: -1\n    textureCompression: 0\n    compressionQuality: 100\n  spriteSheet:\n    serializedVersion: 2\n    sprites: []\n    outline: []\n    physicsShape: []\n    bones: []\n    spriteID: ${guid}\n    internalID: 0\n    nameFileIdTable: {}\n  userData: GPT Image equipment UI; see E:/work/image/designs/equipment-ui-20261008\n  assetBundleName: \n  assetBundleVariant: \n`;
}
async function main(){
  const sm=await sharp(source).metadata();
  const record={file:'skin-atlas.png',sha256:sha(source),generatedAt:fs.statSync(source).mtime.toISOString(),width:sm.width,height:sm.height,format:'png',tool:'image_gen.imagegen',route:'builtin',configSnapshot:config,submittedParameters:{model:null,quality:null,transparent_background:true},actualModel:null,actualQuality:null,evidence:{outputFile:'C:/Users/luyua/.codex/generated_images/01a11b28-5cb7-7961-b9c3-e205ee7ea915/exec-c400789a-1174-41f5-a6f4-0ee4d4807af3.png'},unverifiedReason:'宿主管理；工具未开放 model/quality 选择器，未披露可核实型号或质量元数据。',prompt:'skin-atlas.prompt.txt',references:refs.map(([file,purpose])=>({file,purpose})),alpha:'Native RGBA; actual alpha inspected and composited against dark background. Renderer may show RGB under alpha; no background removal needed.'};
  fs.writeFileSync(path.join(root,'skin-atlas.png.generation.json'),JSON.stringify(record,null,2));
  const retry='C:/Users/luyua/.codex/generated_images/01a11b28-5cb7-7961-b9c3-e205ee7ea915/exec-e7060326-2ddc-4126-a4ec-a2db42ae06ec.png';
  fs.writeFileSync(path.join(root,'alpha-retry.generation.json'),JSON.stringify({...record,file:retry,sha256:sha(retry),generatedAt:fs.statSync(retry).mtime.toISOString(),prompt:'alpha-retry.prompt.txt',references:[{file:source,purpose:'edit target'}],evidence:{outputFile:retry},used:false,reason:'Original already has usable alpha; initial tool preview did not visualize it correctly. Retry is not integrated.'},null,2));
  const out=[];
  for(const [name,left,top,width,height,border] of items){
    const dest=path.join(root,'sprites',name+'.png');
    await sharp(source).extract({left,top,width,height}).png().toFile(dest);
    const stats=await sharp(dest).stats();
    const provenance={file:name+'.png',sha256:sha(dest),width,height,format:'png',derivedFrom:{file:'../skin-atlas.png',sha256:record.sha256,generationRecord:'../skin-atlas.png.generation.json'},operation:{type:'lossless crop',left,top,width,height},unityBorder:border,alphaRange:[stats.channels[3].min,stats.channels[3].max]};
    fs.writeFileSync(dest+'.generation.json',JSON.stringify(provenance,null,2));
    let guid=crypto.createHash('md5').update('equipment-ui-20261008/'+name).digest('hex');
    for(const target of targets){
      // The 2026-10-09 paper card supersedes this historical dark card in the clients.
      // Keep this source's provenance and exports, but do not regress the current integration.
      if(name === 'tooltip_panel' && fs.existsSync(path.join(root, '../equipment-ui-20261009/sprite-manifest.json'))) continue;
      const dir=path.join(target,'Assets/Resources/UI/Ugui/EquipmentV1');fs.mkdirSync(dir,{recursive:true});
      fs.copyFileSync(dest,path.join(dir,name+'.png'));
      const mp=path.join(dir,name+'.png.meta');
      if(!fs.existsSync(mp))fs.writeFileSync(mp,meta(guid,border));
    }
    out.push(provenance);
  }
  fs.writeFileSync(path.join(root,'sprite-manifest.json'),JSON.stringify({source:record.file,sourceSHA256:record.sha256,targets,items:out},null,2));
  console.log(JSON.stringify(out.map(x=>({file:x.file,width:x.width,height:x.height,alphaRange:x.alphaRange})),null,2));
}
main().catch(e=>{console.error(e);process.exit(1)});
