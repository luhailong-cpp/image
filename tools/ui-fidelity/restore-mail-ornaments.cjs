const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const sharp=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root='E:/work/image/docs/ui-fidelity-20261016/mail-original-ornaments',client='E:/work/mmorpg-client';
const rel='Assets/Resources/UI/Ugui/MailV1Fidelity/mail_empty_frame.png';
const original='E:/work/image/designs/mail-ui-v1/01-mail-event.png';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const before=fs.readFileSync(path.join(client,rel)),sourceBytes=fs.readFileSync(original),meta=await sharp(sourceBytes).metadata();
 const base=await sharp(before).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 const source=await sharp(sourceBytes).resize(base.info.width,base.info.height,{kernel:'linear'}).ensureAlpha().raw().toBuffer();
 let replaced=0;for(let y=0;y<base.info.height;y++)for(let x=0;x<base.info.width;x++){
  // These are only the static original scenery, outside frame, corners and tassels.
  // The title and every native content/control region retain the text-free skin.
  const nativeContent=x>=200&&x<1740&&y>=80&&y<775;
  const nativeTitle=x>=780&&x<1165&&y>=18&&y<115;
  if(nativeContent||nativeTitle)continue;
  const p=(y*base.info.width+x)*4;source.copy(base.data,p,p,p+4);replaced++;
 }
 const target=path.join(root,rel);fs.mkdirSync(path.dirname(target),{recursive:true});
 await sharp(base.data,{raw:{width:base.info.width,height:base.info.height,channels:4}}).png().toFile(target);
 const final=fs.readFileSync(target),record={derivedAtUtc:new Date().toISOString(),operation:'Deterministic same-source UI slicing/composition: restore static outer scenery, gold corners, frame and tassels from approved original; preserve text-free native content regions. No AI call.',sha256:sha(final),width:base.info.width,height:base.info.height,referenceResolution:[meta.width,meta.height],normalization:'Original 1931-pixel canvas is normalized to the existing 1932-pixel skin; no claim of a new native design resolution.',pixelsRestored:replaced,derivedFrom:[{path:original,sha256:sha(sourceBytes),role:'approved original static art'},{path:path.join(client,rel),sha256:sha(before),role:'previous text-free native content skin',generationRecord:'E:/work/image/designs/mail-ui-v1/fidelity-20261016/client/'+rel+'.generation.json'}],actualModel:null,actualQuality:null,modelBasis:'No new generation; AI cleanup source has undisclosed actual model/quality.'};
 const recordRel=rel+'.generation.json';fs.writeFileSync(path.join(root,recordRel),JSON.stringify(record,null,2));
 const files=[{source:rel,target:rel,sha256:sha(final),expected_target_sha256:sha(before)}];
 fs.writeFileSync(path.join(root,'install-manifest.json'),JSON.stringify({files},null,2));console.log('MAIL_ORIGINAL_ORNAMENTS_STAGED '+replaced);
})();
