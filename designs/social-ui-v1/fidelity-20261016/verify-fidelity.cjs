const fs=require('fs'),path=require('path');
const sharp=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const directory=path.resolve(process.argv[2]||path.join(__dirname,'qa/final'));
const report=JSON.parse(fs.readFileSync(path.join(directory,'fidelity-capture.json'),'utf8'));
const checks=[];
const check=(name,passed,actual)=>checks.push({name,passed,actual});
const scale=2560/1931,offset=(1080-814*scale)/2;
(async()=>{
  check('isolated capture preserves the user scene and focus',report.activeScenePreserved&&report.eventSystemPreserved&&report.selectedObjectPreserved);
  check('all native shots captured',report.screenshots.length===8&&report.screenshots.every(s=>s.captured));
  for(const shot of report.screenshots){
    const key=shot.page==='Groups'?'groups_skin':shot.page==='Rumor'?'rumor_skin':'world_skin';
    const skin=shot.activeImages.find(i=>i.resourceKey==='UI/Ugui/SocialV1/Fidelity20261016/'+key);
    check(shot.name+' '+shot.width+': dedicated source-design skin',!!skin,skin?.resourceKey||'missing');
    if(skin)check(shot.name+' '+shot.width+': uniform design geometry',Math.abs(skin.rect.topLeft.x)<1&&Math.abs(skin.rect.topLeft.y-offset)<1&&Math.abs(skin.rect.size.x-2560)<1&&Math.abs(skin.rect.size.y-814*scale)<1,skin.rect);
    check(shot.name+' '+shot.width+': native control checks',shot.checks.every(c=>c.passed),shot.checks.filter(c=>!c.passed));
  }
  const shot=report.screenshots.find(s=>s.name==='02-preview-world'&&s.width===2560);
  if(shot){
    const source=path.resolve(__dirname,'../02-world.png');
    const target=await sharp(source).resize(2560,1079,{kernel:'linear'}).extend({top:0,bottom:1,left:0,right:0,background:'#f4ebda'}).removeAlpha().raw().toBuffer();
    const actual=await sharp(shot.file).removeAlpha().raw().toBuffer();
    for(const region of [{name:'original gourd and cloud ornament',rect:[180,530,260,155]},{name:'original left lantern',rect:[0,0,145,190]},{name:'original right lantern',rect:[1830,0,100,190]}]){
      const [sx,sy,sw,sh]=region.rect;
      const x=Math.round(sx*scale),y=Math.round(sy*scale+offset),w=Math.round(sw*scale),h=Math.round(sh*scale);
      let sum=0,n=0;
      for(let yy=y;yy<y+h;yy++)for(let xx=x;xx<x+w;xx++)for(let c=0;c<3;c++){
        const i=(yy*2560+xx)*3+c;sum+=Math.abs(actual[i]-target[i]);n++;
      }
      const mean=sum/n;
      check(region.name+': preserves source pixels within renderer sampling tolerance',mean<10,{meanAbsoluteRgbDifference:mean,limit:10});
    }
  }
  const output={status:checks.every(c=>c.passed)?'passed':'failed',completedAt:new Date().toISOString(),
    scope:'Source-art identity, uniform geometry, fixed ornamental regions and native control presence. Full visual review and functional tests are separate.',checks};
  fs.writeFileSync(path.join(directory,'fidelity-checks.json'),JSON.stringify(output,null,2)+'\n');
  console.log('SOCIAL_FIDELITY_'+output.status.toUpperCase()+' '+checks.filter(c=>c.passed).length+'/'+checks.length);
  for(const c of checks.filter(c=>!c.passed))console.log('FAIL '+c.name+' '+JSON.stringify(c.actual));
  process.exitCode=output.status==='passed'?0:1;
})();
