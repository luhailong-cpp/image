from pathlib import Path
import json,hashlib,re
ROOT=Path(__file__).resolve().parent;CLIENT=Path('E:/work/mmorpg-client');STAGED=ROOT/'staged'
paths=['Assets/Scripts/UI/Ugui/Gameplay/GameplayWindow.Fidelity.cs','Assets/Editor/EquipmentUiVerification.cs','Assets/Editor/EquipmentIntegrationVerification.cs','Assets/Editor/EquipmentForgeUiVerification.cs','Assets/Tests/EditMode/Battle/EquipWindowTests.cs','Assets/Tests/EditMode/Battle/EquipForgeWindowTests.cs']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def strip_method(text,signature):
    start=text.index(signature);brace=text.index('{',start);level=1;p=brace+1
    while level:
        if text[p]=='{':level+=1
        elif text[p]=='}':level-=1
        p+=1
    return text[:start]+'<ONLY-NATIVE-DETAILS-METHOD>'+text[p:]
old=(CLIENT/paths[0]).read_text(encoding='utf-8-sig');new=(STAGED/paths[0]).read_text(encoding='utf-8-sig')
assert strip_method(old,'        private void RenderNativeItem(')==strip_method(new,'        private void RenderNativeItem('),'runtime edits escaped the native detail renderer'
for event in ('UnequipRequested?.Invoke(id)','EquipRequested?.Invoke(id)','OpenEquipmentActions(id)','EquipmentShareRequested?.Invoke(current.Clone())'):
    assert old.count(event)==new.count(event),(event,old.count(event),new.count(event))
assert new.count('"GameplayEquipmentDetails"')==1
guard=[];install=[]
for relative in paths:
    for item in (relative,relative+'.meta'):
        source=CLIENT/item;target=STAGED/item
        if item.endswith('.meta'):target.write_bytes(source.read_bytes())
        guard.append(dict(path=item,sha256=sha(source)))
        install.append(dict(path=item,sha256=sha(target),action='replace',expected_target_sha256=sha(source)))
for relative in ('Assets/Scripts/UI/Ugui/Gameplay/GameplayWindow.cs','Assets/Scripts/UI/Ugui/Gameplay/GameplayUiRoot.cs','Assets/Scripts/UI/Ugui/Gameplay/EquipDetailCard.cs','Assets/Scripts/UI/Ugui/Gameplay/EquipTooltip.cs','Assets/Scripts/Game/PlayerFeatures/PlayerFeaturesClient.cs','Assets/Scripts/UI/Ugui/Gameplay/EquipForgeUiState.cs'):
    guard.append(dict(path=relative,sha256=sha(CLIENT/relative)))
for relative in paths[1:]:
    text=(STAGED/relative).read_text(encoding='utf-8-sig')
    assert '.First(' not in text or '.First(' in (CLIENT/relative).read_text(encoding='utf-8-sig'),relative
(ROOT/'equipment-compat-sourceguard.json').write_text(json.dumps(dict(schema='qdao.gameplay.equipment-compat.guard.v1',client_root=str(CLIENT),files=guard),ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'equipment-compat-install-manifest.json').write_text(json.dumps(dict(schema='qdao.gameplay.equipment-compat.install.v1',staging_root=str(STAGED),client_root=str(CLIENT),source_guard='equipment-compat-sourceguard.json',files=install,resources_changed=False),ensure_ascii=False,indent=2),encoding='utf-8')
result=dict(status='passed',runtime_changed_methods=['RenderNativeItem'],business_callbacks_preserved=True,existing_class_public_api_unchanged=True,resources_changed=False,source_guard_files=len(guard),install_files=len(install),client_modified=False,unity_started=False,tests_run_in_unity=False)
(ROOT/'equipment-compat-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
