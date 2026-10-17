const fs=require('fs'),crypto=require('crypto');
const root=__dirname,client='E:/work/mmorpg-client',dest='Assets/Scripts/UI/Ugui/Guild/GuildWindow.cs',source=client+'/'+dest;
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
let code=fs.readFileSync(source,'utf8').replaceAll('\r\n','\n');
const changes=[
['"可用 / 累计帮贡", 798, 701, 315, 22','"可用 / 累计帮贡", 798, 704, 315, 22'],
['"GuildMyContribution", "", 798, 724, 315, 34','"GuildMyContribution", "", 798, 728, 315, 34'],
['"GuildRuntimeStatusViewport", _frame, 798, 678, 540, 22','"GuildRuntimeStatusViewport", _frame, 798, 678, 540, 25'],
['"GuildRuntimeStatus", "", 0, 0, 540, 22, 16','"GuildRuntimeStatus", "", 0, 0, 540, 25, 16'],
['Mathf.Max(540, _status.GetPreferredValues(_status.text).x + 8), 22)','Mathf.Max(540, _status.GetPreferredValues(_status.text).x + 8), 25)'],
['// Dedicated ivory gap: entries end at678; contribution starts701; actions start704.','// Dedicated ivory gap: entries end at678; status ends703; contribution/actions start704.']
];
for(const [a,b]of changes){if(!code.includes(a))throw Error('Current installed source drift: '+a);code=code.replace(a,b);}
fs.writeFileSync(root+'/readability-patch/GuildWindow-height.cs',code);
const manifest={status:'frozen-ready-for-install',checkedAtUtc:new Date().toISOString(),clientModified:false,unityLaunched:false,guards:[{source,sha256:hash(source)}],files:[{source:'readability-patch/GuildWindow-height.cs',destination:dest,sha256:hash(root+'/readability-patch/GuildWindow-height.cs')}],scope:'Incremental over installed22-high readability fix: restore status text/viewport height25; contribution label y704 and value y728. All messages, horizontal scrolling, original State348 fix and jade-outline funds text retained.',geometry:{status:{x:798,y:678,width:540,height:25},entryBottom:678,statusBottom:703,contributionLabel:{y:704,height:22},contributionValue:{y:728,height:34},membersButtonTop:704,statusRight:1338,refreshLeft:1365},verification:'22-high full package462 sources compiled exit0. This increment only changes6 presentation literals/comment; current-source guard checked. Unity capture pending parent.'};
fs.writeFileSync(root+'/readability-height-patch-install-manifest.json',JSON.stringify(manifest,null,2)+'\n');
const rsp=fs.readFileSync(root+'/qa/readability-patch/runtime.rsp','utf8').split(/\r?\n/).filter(x=>x&&!x.startsWith('-out:')&&!/\.cs"$/.test(x));
rsp.push('-nowarn:0436','-r:"'+root+'/qa/readability-patch/GuildReadability.Runtime.dll"','-out:"'+root+'/qa/readability-patch/GuildReadability.Height.dll"','"'+root+'/readability-patch/GuildWindow-height.cs"','"'+client+'/Assets/Scripts/UI/Ugui/Guild/GuildUiArt.cs"');fs.writeFileSync(root+'/qa/readability-patch/height-only.rsp',rsp.join('\n'));
console.log(JSON.stringify(manifest,null,2));
