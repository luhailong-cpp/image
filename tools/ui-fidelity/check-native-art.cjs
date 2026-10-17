const fs=require('node:fs'),path=require('node:path');
const sharp=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root='E:/work/image';
const cases=[
 ['mail','designs/mail-ui-v1/01-mail-event.png','designs/mail-ui-v1/fidelity-20261016/qa/native/01-activity-mail_2560x1080.png',[0,250,120,400]],
 ['team','designs/team-ui-v2/team-ui-v2.png','designs/team-ui-v2/fidelity-20261016/qa/native/01-approved-preview_2560x1080.png',[0,390,150,310]],
 ['guild','designs/gameplay-ui/04-guild.png','docs/ui-fidelity-20261016/native/guild/01-overview_2560x1080.png',[0,0,160,260]],
 ['jubaozhai','designs/jubaozhai-ui/02-characters.png','designs/jubaozhai-ui/fidelity-20261016/qa/native/01-Character_2560x1080.png',[0,180,120,500]],
 ['channels','designs/scene-select-ui-v1/scene-select.png','designs/scene-select-ui-v1/fidelity-20261016/qa/native/multi-line_2560x1080.png',[0,180,180,470]],
 ['world-map','designs/world-map-original-20260925/world-map-original_2560x1080.png','designs/world-map-original-20260925/fidelity-20261016/qa/native/scene-1-day_2560x1080.png',[2050,180,380,400]]
];
(async()=>{const checks=[];for(const [module,reference,actualFile,rect]of cases){
 const source=path.join(root,reference),native=path.join(root,actualFile),sm=await sharp(source).metadata(),nm=await sharp(native).metadata();
 const scale=Math.min(nm.width/sm.width,nm.height/sm.height),w=Math.round(sm.width*scale),h=Math.round(sm.height*scale),left=Math.floor((nm.width-w)/2),top=Math.floor((nm.height-h)/2);
 const target=await sharp(source).resize(w,h,{kernel:'linear'}).extend({left,top,right:nm.width-w-left,bottom:nm.height-h-top,background:'#fff'}).removeAlpha().raw().toBuffer();
 const pixels=await sharp(native).removeAlpha().raw().toBuffer();
 const [sx,sy,sw,sh]=rect;let sum=0,n=0;for(let y=Math.round(sy*scale+top);y<Math.round((sy+sh)*scale+top);y++)for(let x=Math.round(sx*scale+left);x<Math.round((sx+sw)*scale+left);x++)for(let c=0;c<3;c++){let i=(y*nm.width+x)*3+c;sum+=Math.abs(target[i]-pixels[i]);n++;}
 const mean=sum/n;checks.push({module,reference,native:actualFile,referenceRect:rect,referenceResolution:[sm.width,sm.height],nativeResolution:[nm.width,nm.height],meanAbsoluteRgbDifference:mean,limit:12,passed:mean<12});
 console.log(module+': '+mean.toFixed(3)+' / limit12');
 }const report={checkedAtUtc:new Date().toISOString(),status:checks.every(c=>c.passed)?'passed':'failed',scope:'Only unchanged ornamental/source-art regions under uniform scaling. Does not certify dynamic text, full-screen visual fidelity, or live networking.',checks};fs.writeFileSync(path.join(root,'docs/ui-fidelity-20261016/native-art-checks.json'),JSON.stringify(report,null,2));process.exitCode=report.status==='passed'?0:1;})();
