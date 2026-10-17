const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=__dirname,skill='E:/work/image/designs/class-skills-20260928/fidelity-20261016',client='E:/work/mmorpg-client';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
for(const dir of [root,skill])for(const name of ['integration','qa'])fs.mkdirSync(path.join(dir,name),{recursive:true});
const inputs=[['Attribute/AttributePanel.cs',root],['Pet/PetPanel.cs',root],['Skills/SkillPanel.cs',skill]];
for(const [relative,dest] of inputs){
 const source=client+'/Assets/Scripts/UI/Ugui/'+relative,name=path.basename(relative);let code=fs.readFileSync(source,'utf8').replaceAll('\r\n','\n');
 const guard=path.join(dest,name+'.source.json');if(!fs.existsSync(guard))fs.writeFileSync(guard,JSON.stringify({source,sha256:hash(source),copiedAtUtc:new Date().toISOString()},null,2)+'\n');
 code=code.replace('public sealed class '+name.slice(0,-3),'public sealed partial class '+name.slice(0,-3));
 if(name==='AttributePanel.cs'){
  code=code.replace('            _tooltip.gameObject.SetActive(false);\n            Hide();','            _tooltip.gameObject.SetActive(false);\n            ApplyFidelityLayout();\n            Hide();');
  code=code.replace('            _rowsRoot.anchoredPosition = Vector2.zero;\n            RefreshRemainText();','            _rowsRoot.anchoredPosition = Vector2.zero;\n            RefreshRemainText();\n            ApplyFidelityLayout();');
  code=code.replace('            _schemeListOpen = true;','            _schemeListOpen = true;\n            ApplyFidelityLayout();');
  code=code.replace('            CharacterAttributeVisuals.SelectSideTab(_combatNavigation, page == PanelPage.Combat);\n            HideTooltip();','            CharacterAttributeVisuals.SelectSideTab(_combatNavigation, page == PanelPage.Combat);\n            HideTooltip();\n            ApplyFidelityLayout();');
  code=code.replace('            RefreshSchemeButton();\n        }','            RefreshSchemeButton();\n            ApplyFidelityLayout();\n        }');
 }
 if(name==='PetPanel.cs'){
  for(const token of ['WindowW','WindowH','WindowX','WindowY','LeftX','LeftW','MidX','MidW','RightX','RightW','PetItemHeight','PetItemGap','RosterHeight'])code=code.replaceAll('PetUiStyle.'+token,'FidelityPetGeometry.'+token);
  code=code.replace('            RefreshActionButtons();\n        }','            RefreshActionButtons();\n            ApplyFidelityLayout();\n        }');
  code=code.replace('            RefreshRemainText();\n        }','            RefreshRemainText();\n            ApplyFidelityLayout();\n        }');
  const a=code.indexOf('        private UiPointRow CreatePointStepper('),b=code.indexOf('        private static UiTextButton CreateStep(',a);
  code=code.slice(0,a)+`        private UiPointRow CreatePointStepper(string name,float x,float y)
        {
            // Same UiPointRow pending/committed model and callbacks; expose the v10 slider presentation.
            return CharacterAttributeVisuals.PointRow(name,_root,x,y,1088,78.4f);
        }

`+code.slice(b);
  code=code.replace('            var anchored = row.Rect.anchoredPosition;','            var anchored = (Vector2)_root.InverseTransformPoint(row.Rect.TransformPoint(UnityEngine.Vector3.zero));');
 }
 if(name==='SkillPanel.cs'){
  code=code.replace('private const float ListHeight = 430f','private const float ListHeight = 500f');
  code=code.replace('            else SetStatus(_state?.Message ?? string.Empty);','            else SetStatus(_state?.Message ?? string.Empty);\n            ApplyFidelityLayout();');
 }
 fs.writeFileSync(path.join(dest,'integration',name),code);
}
for(const [dir,files] of [[root,['AttributeFidelityLayout.cs','AttributePanel.Fidelity.cs','PetPanel.Fidelity.cs']],[skill,['SkillPanel.Fidelity.cs']]])
 for(const name of files){const target=path.join(dir,'integration',name);fs.copyFileSync(path.join(dir,name),target);const meta=target+'.meta';if(!fs.existsSync(meta))fs.writeFileSync(meta,'fileFormatVersion: 2\nguid: '+crypto.randomBytes(16).toString('hex')+'\n');}
console.log('Three panels and local helpers staged. No client writes or new raster assets.');
let compile=fs.readFileSync('E:/work/image/designs/team-ui-v2/fidelity-20261016/compile-staged.ps1','utf8');
const a=compile.indexOf('$sources=@('),b=compile.indexOf('$runtime=',a);
compile=compile.slice(0,a)+`$sources=@(Get-ChildItem (Join-Path $Client 'Assets/Scripts') -Recurse -Filter *.cs | ForEach-Object {
 if($_.Name -eq 'AttributePanel.cs' -or $_.Name -eq 'PetPanel.cs'){'"'+(Join-Path $package ('integration/'+$_.Name))+'"'}elseif($_.Name -eq 'SkillPanel.cs'){'"${skill}/integration/SkillPanel.cs"'}else{'"'+$_.FullName+'"'}
})
$sources+=@('AttributeFidelityLayout.cs','AttributePanel.Fidelity.cs','PetPanel.Fidelity.cs') | ForEach-Object {'"'+(Join-Path $package ('integration/'+$_))+'"'}
$sources+='"${skill}/integration/SkillPanel.Fidelity.cs"'
`+compile.slice(b);
compile=compile.slice(0,compile.indexOf('$editorRefs='))+`$result=[ordered]@{checkedAtUtc=[DateTime]::UtcNow.ToString('O');runtimeExit=$runtimeExit;runtimeSources=$sources.Count;missingReferences=$missing;unityEditor=$editor.FullName;csc=$csc;unityLaunched=$false;nativeCaptureRun=$false}
$result | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 -LiteralPath (Join-Path $qa 'compile-report.json')
$result | ConvertTo-Json -Depth 8
if($runtimeExit -ne 0){$runtimeOutput | Select-Object -First 18;exit 1}
`;
compile=compile.replaceAll('TeamFidelity.Runtime','AttributeSkillFidelity.Runtime');
fs.writeFileSync(path.join(root,'compile-panels.ps1'),compile);
