// Deterministic extraction only. AI cleaning is performed by the built-in image tool.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const sharp = require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root = __dirname;
const out = path.join(root, 'runtime-assets');
fs.mkdirSync(out, { recursive: true });
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const records = [];
async function save(name, pipeline, sources, operation, border = [0,0,0,0]) {
  const destination = path.join(out, name + '.png');
  await pipeline.png().toFile(destination);
  const metadata = await sharp(destination).metadata();
  records.push({ file: name + '.png', sha256: hash(destination), width: metadata.width,
    height: metadata.height, spriteBorderLeftBottomRightTop: border, operation,
    derivedFrom: sources.map(p => ({ file: path.relative(root, p).replaceAll('\\','/'), sha256: hash(p) })) });
}
async function crop(name, source, rectangle, border) {
  await save(name, sharp(source).extract({left:rectangle[0],top:rectangle[1],width:rectangle[2],height:rectangle[3]}),
    [source], {type:'crop', rectangle}, border);
}
(async () => {
  const original = path.resolve(root, '../02-world.png');
  const cleaned = path.join(root, 'assets/world-clean-skin.png');
  const normalized = await sharp(cleaned).resize(1931,814,{fit:'fill'}).png().toBuffer();
  // Keep every original pixel outside the exact dynamic-content rectangles.
  const rectangles = [[870,34,225,44],[711,98,111,33],[929,98,80,33],[1116,98,106,33],
    [492,144,1060,44],[218,137,198,48],[270,205,117,49],[273,292,112,44],
    [270,377,124,47],[272,459,125,47],[184,705,247,48],[487,195,1258,493],
    [684,711,816,46],[1584,715,123,40],[1661,99,59,30],[1580,153,112,31]];
  const patches = await Promise.all(rectangles.map(async r => ({input:await sharp(normalized).extract({left:r[0],top:r[1],width:r[2],height:r[3]}).png().toBuffer(),left:r[0],top:r[1]})));
  await save('world_skin', sharp(original).composite(patches), [original,cleaned],
    {type:'preserve-original-static-art-and-insert-cleaned-dynamic-zones', normalizedCleanSize:[1931,814], rectangles});
  const blank = path.join(out,'world_skin.png');
  await crop('button_normal',cleaned,[677,90,181,48],[20,10,20,10]);
  await crop('button_selected',cleaned,[873,90,149,48],[20,10,20,10]);
  await crop('send_button',cleaned,[1534,700,220,70],[30,20,30,20]);
  await crop('input_field',cleaned,[664,704,854,62],[32,20,32,20]);
  const portraitRects=[[1624,574,108,106],[505,198,104,97],[505,294,104,104],[505,399,104,101],[505,519,104,103]];
  for(let p=0;p<portraitRects.length;p++){
    const [left,top,width,height]=portraitRects[p];
    const rgba=await sharp(original).extract({left,top,width,height}).ensureAlpha().raw().toBuffer();
    for(let y=0;y<height;y++)for(let x=0;x<width;x++){
      const radius=Math.hypot((x-(width-1)/2)/((width-1)/2),(y-(height-1)/2)/((height-1)/2));
      if(radius>1)rgba[(y*width+x)*4+3]=0;
    }
    await save('portrait_'+(p+1),sharp(rgba,{raw:{width,height,channels:4}}),[original],
      {type:'crop-and-elliptical-alpha-at-original-portrait-frame',rectangle:portraitRects[p]});
  }
  const portraitFrame=await sharp(original).extract({left:505,top:198,width:104,height:97}).ensureAlpha().raw().toBuffer();
  for(let y=0;y<97;y++)for(let x=0;x<104;x++){
    const radius=Math.hypot((x-51.5)/51.5,(y-48)/48);
    if(radius<.90||radius>1)portraitFrame[(y*104+x)*4+3]=0;
  }
  await save('portrait_frame',sharp(portraitFrame,{raw:{width:104,height:97,channels:4}}),[original],
    {type:'crop-elliptical-frame-only',rectangle:[505,198,104,97],innerNormalizedRadius:.90,outerNormalizedRadius:1});
  // Speech-bubble contour is original art. Its blank middle is a clean paper
  // strip already inside the same bubble; no generated or recolored contour.
  const bubble = {left:614,top:234,width:420,height:50};
  const cut = await sharp(original).extract(bubble).png().toBuffer();
  const paper = await sharp(original).extract({left:650,top:237,width:335,height:6}).resize(391,33).png().toBuffer();
  await save('message_bubble',sharp(cut).composite([{input:paper,left:17,top:9}]),[original],
    {type:'nine-slice-speech-contour-and-clean-interior-paper',rectangle:[614,234,420,50],paperStrip:[650,237,335,6]},[17,9,17,9]);
  for (const page of ['groups','rumor']) {
    const p=path.join(root,'assets',page+'-clean-skin.png');
    if (!fs.existsSync(p)) continue;
    const planPath = path.join(root, page + '-static-art-rectangles.json');
    const plan = JSON.parse(fs.readFileSync(planPath, 'utf8'));
    const pageOriginal = path.resolve(root, plan.sourceDesign);
    if (hash(pageOriginal) !== plan.sourceSha256) throw new Error(page + ' original artwork hash changed');
    let normalizedPage = await sharp(p).resize(1931,814,{fit:'fill'}).png().toBuffer();
    // Repair model artifacts only with clean paper copied from the same image.
    if (plan.cleanArtifactRepairs.length) {
      const repairs = await Promise.all(plan.cleanArtifactRepairs.map(async repair => {
        const r = repair.sourceRectangle;
        return { input: await sharp(normalizedPage).extract({left:r[0],top:r[1],width:r[2],height:r[3]}).png().toBuffer(),
          left:repair.destination[0], top:repair.destination[1] };
      }));
      normalizedPage = await sharp(normalizedPage).composite(repairs).png().toBuffer();
    }
    const pagePatches = await Promise.all(plan.dynamicRectangles.map(async r => ({
      input:await sharp(normalizedPage).extract({left:r[0],top:r[1],width:r[2],height:r[3]}).png().toBuffer(),left:r[0],top:r[1]
    })));
    await save(page+'_skin',sharp(pageOriginal).composite(pagePatches),[pageOriginal,p],
      {type:'preserve-original-static-art-and-insert-cleaned-dynamic-zones',normalizedCleanSize:[1931,814],
        rectangles:plan.dynamicRectangles,cleanArtifactRepairs:plan.cleanArtifactRepairs,
        staticArtworkPlan:{file:path.basename(planPath),sha256:hash(planPath)}});
  }
  // Crop from the restored skins so generated badge/chevron drift is excluded.
  const groupsSkin = path.join(out,'groups_skin.png');
  const rumorSkin = path.join(out,'rumor_skin.png');
  if (fs.existsSync(groupsSkin)) {
    await crop('group_row_selected',groupsSkin,[166,274,400,111],[12,12,12,12]);
    await crop('group_row_normal',groupsSkin,[166,396,400,112],[12,12,12,12]);
    await crop('group_row_lotus',groupsSkin,[166,519,400,111],[12,12,12,12]);
  }
  if (fs.existsSync(rumorSkin)) {
    await crop('rumor_row',rumorSkin,[484,246,1277,129],[12,12,12,12]);
    await crop('rumor_row_ended',rumorSkin,[484,645,1277,86],[12,12,12,12]);
  }
  const rumorOriginal = path.resolve(root,'../03-rumor.png');
  await crop('rumor_beast',rumorOriginal,[620,249,151,124]);
  await crop('rumor_treasure',rumorOriginal,[619,385,153,120]);
  await crop('rumor_victory',rumorOriginal,[591,517,213,117]);
  await crop('rumor_ended',rumorOriginal,[620,649,151,78]);
  await crop('list_paper',cleaned,[500,200,300,150],[12,12,12,12]);
  fs.writeFileSync(path.join(root,'runtime-assets.json'),JSON.stringify({createdAt:new Date().toISOString(),sourceDesignSize:[1931,814],uniformDisplayScale:2560/1931,images:records},null,2)+'\n');
  console.log('FIDELITY_ASSETS_OK '+records.length);
})();
