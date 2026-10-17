from pathlib import Path
import json,hashlib,re,datetime
ROOT=Path(__file__).resolve().parent;PACKAGE=ROOT.parent;CLIENT=Path('E:/work/mmorpg-client');STAGED=ROOT/'staged'
relative='Assets/Editor/EquipmentForgeUiVerification.cs'
old=(CLIENT/relative).read_text(encoding='utf-8-sig')
new=old.replace('''window.ShowEquipment();
            Click(root, "EquipSlot_3");''','''window.ShowEquipment();
            Click(root, "BagCategory_3"); // Native worn-equipment view.
            Click(root, "EquipSlot_3");''')
new=new.replace('''Require(!Find<Button>(root, "EquipForgeEnhance").interactable, "同步中必须禁用强化。");''','''var hiddenEnhance = Find<RectTransform>(root, "EquipForgeDialog")
                .GetComponentsInChildren<Button>(true).Single(button => button.name == "EquipForgeEnhance");
            Require(!hiddenEnhance.gameObject.activeInHierarchy && !hiddenEnhance.interactable,
                "同步中必须隐藏强化区且保持强化不可用。");''')
assert new!=old
assert new.count('Click(root, "BagCategory_3")')==1
assert new.count('transport.Calls.Count(call => call.Request is GetBagRequest) == 2')==old.count('transport.Calls.Count(call => call.Request is GetBagRequest) == 2')==1
assert re.findall(r'"[0-9]{2}-[^"\n]+"',old)==re.findall(r'"[0-9]{2}-[^"\n]+"',new)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
target=STAGED/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(new,encoding='utf-8')
Path(str(target)+'.meta').write_bytes((CLIENT/(relative+'.meta')).read_bytes())
install=[];guard=[]
for r in (relative,relative+'.meta'):
    install.append(dict(path=r,sha256=sha(STAGED/r),action='replace',expected_target_sha256=sha(CLIENT/r)))
    guard.append(dict(path=r,sha256=sha(CLIENT/r)))
for r in ('Assets/Scripts/UI/Ugui/Gameplay/GameplayWindow.cs','Assets/Scripts/UI/Ugui/Gameplay/GameplayWindow.Fidelity.cs','Assets/Scripts/UI/Ugui/Gameplay/EquipForgeDialog.cs','Assets/Scripts/UI/Ugui/Gameplay/EquipForgeUiState.cs'):
    guard.append(dict(path=r,sha256=sha(CLIENT/r)))
(ROOT/'sourceguard.json').write_text(json.dumps(dict(client_root=str(CLIENT),files=guard),ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'install-manifest.json').write_text(json.dumps(dict(staging_root=str(STAGED),client_root=str(CLIENT),source_guard='sourceguard.json',files=install),ensure_ascii=False,indent=2),encoding='utf-8')
# Read-only installation consistency and static capture entry checks, not a Unity execution result.
manifest=json.loads((PACKAGE/'visual-fixes-20261017/install-manifest.json').read_text(encoding='utf-8'))
matches=[dict(path=row['path'],expected_sha256=row['sha256'],installed_sha256=sha(CLIENT/row['path']),exact_match=row['sha256']==sha(CLIENT/row['path'])) for row in manifest['files']]
checks=[]
for name in ['EquipmentUiVerification.cs','EquipmentIntegrationVerification.cs','EquipmentForgeUiVerification.cs']:
    p=CLIENT/'Assets/Editor'/name;text=p.read_text(encoding='utf-8-sig')
    checks.append(dict(path=str(p),sha256=sha(p),active_hierarchy_then_single=('Where(b=>b.gameObject.activeInHierarchy).Single' in text or 'Where(item => item.gameObject.activeInHierarchy).Single' in text),first_fallback_present='.First(' in text,static_only=True))
result=dict(reviewed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),unity_started=False,client_written=False,installed_visual_patch_files=matches,installed_code_and_png_exact=all(r['exact_match'] for r in matches if not r['path'].endswith('.meta')),installed_meta_exact=all(r['exact_match'] for r in matches if r['path'].endswith('.meta')),capture_entry_checks=checks,forge_capture_known_blockers=['Worn slot must be reached via BagCategory_3.','Loading-stage enhancement control is intentionally hidden, so an active-only query cannot inspect its disabled state.'],patch=str(ROOT/'install-manifest.json'),post_fix_native_screenshots_reviewed=False)
(PACKAGE/'qa/postinstall-consistency.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(install_files=2,source_guard_files=len(guard),installed_visual_code_and_png_exact=result['installed_code_and_png_exact'],installed_visual_meta_exact=result['installed_meta_exact'])))
