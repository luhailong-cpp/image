const fs=require('fs'),crypto=require('crypto');
const root=__dirname,client='E:/work/mmorpg-client',dest='Assets/Scripts/UI/Ugui/Guild/GuildWindow.cs',source=client+'/'+dest;
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
let code=fs.readFileSync(source,'utf8').replaceAll('\r\n','\n');const before=code;
function exact(a,b){if(!code.includes(a))throw Error('Source drift: '+a);code=code.replace(a,b);}
exact('        private readonly TMP_Text _status, _summary;','        private readonly TMP_Text _status, _summary;\n        private readonly ScrollRect _statusScroll;');
exact('            _status = FidelityLabel(_frame, "GuildRuntimeStatus", "", 796, 767, 963, 25, 16, Muted);',`            // Dedicated ivory gap: entries end at678; contribution starts701; actions start704.
            var statusViewport = QdaoUguiFactory.CreateRect("GuildRuntimeStatusViewport", _frame, 798, 678, 540, 22);
            var statusHit = statusViewport.gameObject.AddComponent<Image>();
            statusHit.color = new Color(1, 1, 1, .001f); statusHit.raycastTarget = true;
            statusViewport.gameObject.AddComponent<RectMask2D>();
            _status = FidelityLabel(statusViewport, "GuildRuntimeStatus", "", 0, 0, 540, 22, 16, Muted);
            _status.overflowMode = TextOverflowModes.Overflow;
            _status.raycastTarget = false;
            _statusScroll = statusViewport.gameObject.AddComponent<ScrollRect>();
            _statusScroll.viewport = statusViewport; _statusScroll.content = _status.rectTransform;
            _statusScroll.horizontal = true; _statusScroll.vertical = false;
            _statusScroll.movementType = ScrollRect.MovementType.Clamped;
            _statusScroll.scrollSensitivity = 36;`);
exact('            _status.text = _client?.Status ?? "进入角色后，可在此与同道相聚。";',`            _status.text = _client?.Status ?? "进入角色后，可在此与同道相聚。";
            // Preserve the complete authoritative message; long status is draggable/wheel-scrollable.
            _status.rectTransform.sizeDelta = new Vector2(Mathf.Max(540, _status.GetPreferredValues(_status.text).x + 8), 22);
            _statusScroll.horizontalNormalizedPosition = 0;`);
exact('            FidelityLabel(_rail, "GuildUpgradeFundsValue", info.UpgradeCostFunds == 0 ? "已满级" :','            var upgradeFundsText = FidelityLabel(_rail, "GuildUpgradeFundsValue", info.UpgradeCostFunds == 0 ? "已满级" :');
exact('                ratio >= .55 ? Cream : Ink, align: TextAlignmentOptions.Center);','                Cream, align: TextAlignmentOptions.Center);\n            Battle.BattleUiWidgets.ApplyOutline(upgradeFundsText, .12f, new Color32(41, 79, 65, 255));');
const folder=root+'/readability-patch';fs.mkdirSync(folder,{recursive:true});fs.writeFileSync(folder+'/GuildWindow.cs',code);
const state348Preserved=code.includes('x + 136, 138, 348, 46, 30, Muted');if(!state348Preserved)throw Error('Current activity348 fix missing');
const manifest={status:'ready-for-install',checkedAtUtc:new Date().toISOString(),clientModified:false,unityLaunched:false,guards:[{source,sha256:hash(source)}],files:[{source:'readability-patch/GuildWindow.cs',destination:dest,sha256:hash(folder+'/GuildWindow.cs')}],scope:'Two local presentation fixes only. Full authoritative runtime status uses a bounded horizontal scroll row inside ivory frame (no ellipsis), and real funds text uses ivory with dark jade outline for mixed fill/background contrast. ActivityState348 fix retained. No event, permission, value, transaction or gameplay change.'};
fs.writeFileSync(root+'/readability-patch-install-manifest.json',JSON.stringify(manifest,null,2)+'\n');
fs.writeFileSync(root+'/qa/readability-patch-audit.json',JSON.stringify({checkedAtUtc:new Date().toISOString(),state348Preserved,statusSlot:{x:798,y:678,width:540,height:22,fontSize:16,content:'complete authoritative string; preferred width; horizontal ScrollRect'},separations:{overviewEntriesBottom:678,statusTop:678,statusBottom:700,contributionTop:701,membersButtonTop:704,refreshButtonLeft:1365,statusRight:1338},fundsLabel:'exact values retained, ivory text + .12 jade SDF outline, no ratio-based text-color switch',sourceGuard:manifest.guards[0],clientModified:false,unityLaunched:false},null,2)+'\n');
let compile=fs.readFileSync('E:/work/image/qdao_ui_redesign_v5/fidelity-battle-20261016/compile-staged.ps1','utf8');const a=compile.indexOf('$stagedNames='),b=compile.indexOf('$runtime=',a);
compile=compile.slice(0,a)+`$sources=@(Get-ChildItem (Join-Path $Client 'Assets/Scripts') -Recurse -Filter *.cs | ForEach-Object {
 if($_.FullName -eq (Join-Path $Client '${dest}')){'"'+(Join-Path $package 'readability-patch/GuildWindow.cs')+'"'}else{'"'+$_.FullName+'"'}
})
`+compile.slice(b);compile=compile.replace("$qa=Join-Path $package 'qa'","$qa=Join-Path $package 'qa/readability-patch'").replaceAll('BattleFidelity.Runtime','GuildReadability.Runtime');fs.writeFileSync(root+'/compile-readability-patch.ps1',compile);
console.log(JSON.stringify(manifest,null,2));
