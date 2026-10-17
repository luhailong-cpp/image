// Requested deterministic source extraction and reuse of approved, already-clean TeamV2 slices.
// No AI generation or new visual design occurs here.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const sharp=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=__dirname,out=path.join(root,'runtime-assets');fs.mkdirSync(out,{recursive:true});
const original=path.resolve(root,'../team-ui-v2.png'),slices=path.resolve(root,'../unity-slices/png');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const records=[];
const generation=JSON.parse(fs.readFileSync(path.resolve(root,'../source/generation.json'),'utf8'));
const metaTemplate=fs.readFileSync('E:/work/mmorpg-client/Assets/Resources/UI/Ugui/TeamV2/application_card.png.meta','utf8');
async function save(key,pipeline,sources,operation,border=[0,0,0,0]){
  const file=path.join(out,key+'.png');await pipeline.png().toFile(file);const m=await sharp(file).metadata();
  const guid=crypto.randomBytes(16).toString('hex');
  const data={key,file:key+'.png',resourceKey:'UI/Ugui/TeamV2/Fidelity20261016/'+key,width:m.width,height:m.height,
    sha256:hash(file),guid,spriteBorderLeftBottomRightTop:border,operation,
    derivedFrom:sources.map(p=>({file:path.relative(root,p).replaceAll('\\','/'),sha256:hash(p)}))};
  records.push(data);
  const meta=metaTemplate.replace(/guid: [a-f0-9]+/,`guid: ${guid}`)
    .replace(/second: application_card_0/,'second: '+key+'_0').replace(/maxTextureSize: \d+/g,'maxTextureSize: 4096')
    .replace(/spriteBorder: \{[^}]+\}/,`spriteBorder: {x: ${border[0]}, y: ${border[1]}, z: ${border[2]}, w: ${border[3]}}`);
  fs.writeFileSync(file+'.meta',meta);
  fs.writeFileSync(file+'.sprite.json',JSON.stringify({textureType:'Sprite',spriteMode:'Single',spriteMeshType:'FullRect',
    mipmaps:false,compression:'Uncompressed',pixelsPerUnit:100,maxTextureSize:4096,filterMode:'Bilinear',wrapMode:'Clamp',...data},null,2)+'\n');
  fs.writeFileSync(file+'.generation.json',JSON.stringify({recordType:'derived-existing-approved-art',generatedAtUtc:new Date().toISOString(),
    aiGenerationPerformed:false,configurationTargetModel:'not applicable to crop/reconstruction',submittedModel:'not applicable',
    submittedQuality:'not applicable',returnedModel:'not disclosed by the original host tool',returnedQuality:'not disclosed by the original host tool',
    originalGenerationEvidence:'../source/generation.json',originalGenerationDate:generation.date,originalTool:generation.tool,...data},null,2)+'\n');
}
async function paper(source,w,h){const m=await sharp(source).metadata();return sharp(source).extract({left:40,top:25,width:m.width-80,height:m.height-50}).resize(w,h).png().toBuffer();}
(async()=>{
  const member=path.join(slices,'member_row.png'),app=path.join(slices,'application_card.png');
  const sections=path.join(slices,'section_plate.png'),badge=path.join(slices,'badge_self.png');
  const patches=[
    {input:await paper(member,855,519),left:193,top:199},
    {input:await paper(app,626,408),left:1105,top:235},
    {input:await sharp(original).extract({left:650,top:153,width:220,height:32}).resize(338,42).png().toBuffer(),left:1206,top:111},
    {input:await sharp(badge).resize(159,44).png().toBuffer(),left:1545,top:110},
    {input:await sharp(sections).resize(435,73).png().toBuffer(),left:1099,top:157},
    {input:await sharp(original).extract({left:680,top:163,width:170,height:31}).resize(139,35).png().toBuffer(),left:910,top:162},
    {input:await sharp(original).extract({left:610,top:730,width:220,height:20}).resize(263,45).png().toBuffer(),left:285,top:732},
    {input:await sharp(original).extract({left:610,top:730,width:220,height:20}).resize(1010,48).png().toBuffer(),left:540,top:730},
    {input:await sharp(original).extract({left:1115,top:648,width:610,height:15}).resize(618,45).png().toBuffer(),left:1107,top:665},
    {input:await sharp(path.join(slices,'button_secondary.png')).resize(181,54).png().toBuffer(),left:1538,top:725}
  ];
  await save('team_skin',sharp(original).composite(patches),[original,member,app,sections,badge,path.join(slices,'button_secondary.png')],
    {type:'preserve-original-static-frame-world-and-title; replace-dynamic-zones-with-approved-clean-paper-and-controls',sourceSize:[1931,814],
      regions:patches.map(p=>({left:p.left,top:p.top}))});
  const portraits=[[238,201,105,105],[239,309,103,103],[238,415,104,104],[1128,246,132,132],[1127,449,132,132]];
  for(let i=0;i<portraits.length;i++){
    const [left,top,width,height]=portraits[i];
    const circle=Buffer.from(`<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg"><ellipse cx="${width/2}" cy="${height/2}" rx="${width/2}" ry="${height/2}" fill="white"/></svg>`);
    await save('preview_portrait_'+(i+1),sharp(original).extract({left,top,width,height}).ensureAlpha().composite([{input:circle,blend:'dest-in'}]),[original],
      {type:'source-crop-and-circular-alpha-mask',rectangle:[left,top,width,height],usage:'explicit offline preview fixture only; never infer a live identity'});
  }
  fs.writeFileSync(path.join(root,'runtime-assets.json'),JSON.stringify({createdAtUtc:new Date().toISOString(),sourceDesignSize:[1931,814],uniformScale:2560/1931,
    existingTeamV2SliceCount:14,existingSliceManifest:'../unity-slices/manifest.json',images:records},null,2)+'\n');
  const files=['TeamWindow.cs','TeamUiArt.cs'];
  fs.mkdirSync(path.join(root,'integration'),{recursive:true});
  const inputs=files.map(name=>{const source='E:/work/mmorpg-client/Assets/Scripts/UI/Ugui/Team/'+name;const destination=path.join(root,'integration',name);
    if(!fs.existsSync(destination))fs.copyFileSync(source,destination);return {source,destination:path.relative(root,destination),sha256:hash(source)};});
  if(!fs.existsSync(path.join(root,'source-checkout.json')))fs.writeFileSync(path.join(root,'source-checkout.json'),JSON.stringify({copiedAtUtc:new Date().toISOString(),
    warning:'Client Team logic is being edited in another task. Compare these hashes before installing presentation files.',inputs},null,2)+'\n');
  process.stdout.write(JSON.stringify({assets:records.length,output:out,inputs},null,2)+'\n');
})().catch(error=>{process.stderr.write(error.stack+'\n');process.exitCode=1;});
