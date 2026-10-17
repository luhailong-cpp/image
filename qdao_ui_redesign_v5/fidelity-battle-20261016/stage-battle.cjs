const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=__dirname,client='E:/work/mmorpg-client',hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
for(const dir of ['integration','qa'])fs.mkdirSync(path.join(root,dir),{recursive:true});
function methodEnd(code,start){const a=code.indexOf(start),open=code.indexOf('{',a);let depth=1,i=open+1;
 // Method bodies here have no brace literals; string interpolation has balanced braces.
 for(;i<code.length;i++){if(code[i]==='{')depth++;else if(code[i]==='}'&&--depth===0)return i;}throw Error(start);}
const names=['BattleScreen.cs','BattleHud.cs','BattleQueuePanel.cs','SpectatePanel.cs','BattleResultPanel.cs'];
const guards=[];
for(const name of names){
 const source=client+'/Assets/Scripts/UI/Ugui/Battle/'+name;guards.push({source,sha256:hash(source)});let code=fs.readFileSync(source,'utf8').replaceAll('\r\n','\n');
 if(name==='BattleScreen.cs'){
  code=code.replace('            _root.gameObject.SetActive(false);\n        }','            BattleFidelityArt.ApplyHud(_hudRoot);\n            _root.gameObject.SetActive(false);\n        }');
  code=code.replace('                    _skillButtons.Add(button);','                    BattleFidelityArt.Button(button.Button);\n                    _skillButtons.Add(button);');
 }
 if(name==='BattleHud.cs'){
  const end=methodEnd(code,'        public void Refresh(IReadOnlyList<BattleActorState> members');code=code.slice(0,end)+'    BattleFidelityArt.ApplyParty(_root);\n        '+code.slice(end);
 }
 if(name==='BattleQueuePanel.cs'){
  code=code.replace('            RefreshContinuousButton();\n            Hide();','            RefreshContinuousButton();\n            BattleFidelityArt.ApplyPanel(_root);\n            Hide();');
  const end=methodEnd(code,'        private void RefreshPveSizeSelection()');code=code.slice(0,end)+'    BattleFidelityArt.ApplyPanel(_root);\n        '+code.slice(end);
 }
 if(name==='SpectatePanel.cs'){
  code=code.replace('            Hide();\n        }','            BattleFidelityArt.ApplyPanel(_root);\n            Hide();\n        }');
  code=code.replace('            _entries.Add(entry);','            _entries.Add(entry);\n            BattleFidelityArt.ApplyPanel(_root);');
 }
 if(name==='BattleResultPanel.cs'){
  code=code.replace('            Hide();\n        }','            BattleFidelityArt.ApplyPanel(_root);\n            Hide();\n        }');
  code=code.replace('titleColor = BattleUiStyle.WarnText;','titleColor = QdaoUguiTheme.Html("#205B46");').replace('titleColor = QdaoUguiTheme.Cream;','titleColor = BattleFidelityArt.Ink;')
   .replace('lines[i], 26f, QdaoUguiTheme.StatusCream','lines[i], 26f, BattleFidelityArt.Ink');
 }
 fs.writeFileSync(path.join(root,'integration',name),code);
}
fs.copyFileSync(path.join(root,'BattleFidelityArt.cs'),path.join(root,'integration/BattleFidelityArt.cs'));
const meta=path.join(root,'integration/BattleFidelityArt.cs.meta');if(!fs.existsSync(meta))fs.writeFileSync(meta,'fileFormatVersion: 2\nguid: '+crypto.randomBytes(16).toString('hex')+'\n');
fs.writeFileSync(path.join(root,'source-checkout.json'),JSON.stringify({copiedAtUtc:new Date().toISOString(),guards},null,2)+'\n');
let compile=fs.readFileSync('E:/work/image/designs/team-ui-v2/fidelity-20261016/compile-staged.ps1','utf8');
const a=compile.indexOf('$sources=@('),b=compile.indexOf('$runtime=',a);
compile=compile.slice(0,a)+`$stagedNames=@('${names.join("','")}')
$sources=@(Get-ChildItem (Join-Path $Client 'Assets/Scripts') -Recurse -Filter *.cs | ForEach-Object {
 if($_.Name -in $stagedNames){'"'+(Join-Path $package ('integration/'+$_.Name))+'"'}else{'"'+$_.FullName+'"'}
})
$sources+='"'+(Join-Path $package 'integration/BattleFidelityArt.cs')+'"'
`+compile.slice(b);
compile=compile.slice(0,compile.indexOf('$editorRefs='))+`$result=[ordered]@{checkedAtUtc=[DateTime]::UtcNow.ToString('O');runtimeExit=$runtimeExit;runtimeSources=$sources.Count;missingReferences=$missing;unityEditor=$editor.FullName;csc=$csc;unityLaunched=$false;nativeCaptureRun=$false}
$result | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 -LiteralPath (Join-Path $qa 'compile-report.json')
$result | ConvertTo-Json -Depth 8
if($runtimeExit -ne 0){$runtimeOutput | Select-Object -First 18;exit 1}
`;
compile=compile.replaceAll('TeamFidelity.Runtime','BattleFidelity.Runtime');fs.writeFileSync(path.join(root,'compile-staged.ps1'),compile);
console.log('Battle-only skins staged; no shared style/widget, actor, arena, timing or connection edits.');
