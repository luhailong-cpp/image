const fs=require('fs'),path=require('path'),crypto=require('crypto');
const sharp=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=__dirname,client='E:/work/mmorpg-client',hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
async function run(){
const guards=JSON.parse(fs.readFileSync(root+'/source-checkout.json')).guards;
const files=guards.map(g=>({source:'integration/'+path.basename(g.source),destination:g.source.slice(client.length+1),sha256:hash(root+'/integration/'+path.basename(g.source))}));
for(const name of ['BattleFidelityArt.cs','BattleFidelityArt.cs.meta'])files.push({source:'integration/'+name,destination:'Assets/Scripts/UI/Ugui/Battle/'+name,sha256:hash(root+'/integration/'+name)});
const checks=[];for(const g of guards){let src=fs.readFileSync(g.source,'utf8').replaceAll('\r\n','\n');let out=fs.readFileSync(root+'/integration/'+path.basename(g.source),'utf8').replace(/^.*BattleFidelityArt\.(?:ApplyHud|ApplyParty|ApplyPanel|Button)\(.*\);\n/gm,'');
 out=out.replace('titleColor = QdaoUguiTheme.Html("#205B46");','titleColor = BattleUiStyle.WarnText;').replace('titleColor = BattleFidelityArt.Ink;','titleColor = QdaoUguiTheme.Cream;').replace('lines[i], 26f, BattleFidelityArt.Ink','lines[i], 26f, QdaoUguiTheme.StatusCream');
 checks.push({source:path.basename(g.source),guardMatches:hash(g.source)===g.sha256,businessCodeExactAfterPresentationHooks:src.replace(/\s+/g,'')===out.replace(/\s+/g,'')});}
const assetPairs=[
['05_battle_scene_2560x1080.png','Backgrounds/qdao_battle_arena_cloud_terrace_2560x1080_v1.png'],
['06_battle_entry_loading_2560x1080.png','Backgrounds/qdao_battle_entry_loading_2560x1080_v1.png'],
['06_battle_entry_clouds_fg_2560x1080.png','Overlays/qdao_battle_entry_clouds_fg_2560x1080_v1.png']
];const assets=[];for(const [a,b]of assetPairs){const p='E:/work/image/qdao_ui_redesign_v5/'+a,q=client+'/Assets/Resources/UI/Ugui/Battle/'+b;const [x,y]=await Promise.all([sharp(p).ensureAlpha().raw().toBuffer({resolveWithObject:true}),sharp(q).ensureAlpha().raw().toBuffer({resolveWithObject:true})]);assets.push({design:a,client:b,designSha256:hash(p),clientSha256:hash(q),sameDecodedRgba:x.info.width===y.info.width&&x.info.height===y.info.height&&x.data.equals(y.data),designSize:[x.info.width,x.info.height],clientSize:[y.info.width,y.info.height]});}
const report={checkedAtUtc:new Date().toISOString(),sourceChecks:checks,assets,sharedStyleFilesModified:[],newImages:[],unityLaunched:false,nativeCaptureRun:false};fs.writeFileSync(root+'/qa/source-and-asset-audit.json',JSON.stringify(report,null,2)+'\n');
if(checks.some(c=>!c.guardMatches||!c.businessCodeExactAfterPresentationHooks))throw Error('Source drift/business change');
const manifest={status:'ready-for-install',checkedAtUtc:new Date().toISOString(),clientModified:false,unityLaunched:false,guards,files,scope:'Battle-only skin: ivory/jade/gold cards, rounds, command plates, queue, spectate and settlement. No shared BattleUiStyle/Widgets, geometry, actor art, turn protocol, queue, cooldown, target, auto, flee, spectate or result callback change.',verification:'Roslyn compile-staged.ps1; source-and-asset-audit.json. Parent must recapture four production controls after install.'};
fs.writeFileSync(root+'/installation-manifest.json',JSON.stringify(manifest,null,2)+'\n');console.log(JSON.stringify(report,null,2));console.log('Frozen manifest: '+files.length+' files');}
run().catch(e=>{console.error(e);process.exitCode=1;});
