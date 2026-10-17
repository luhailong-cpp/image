from pathlib import Path
import json, hashlib, re, uuid
from PIL import Image
ROOT=Path(__file__).resolve().parent
CLIENT=Path('E:/work/mmorpg-client')
STAGED=ROOT/'staged'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
guards=[]
for relative in ('Assets/Scripts/UI/Ugui/Gameplay/GameplayWindow.cs','Assets/Tests/EditMode/Battle/GameplayWindowTests.cs','Assets/Scripts/UI/Ugui/Gameplay/GameplayUiArt.cs'):
    guards.append(dict(path=relative,sha256=sha(CLIENT/relative)))
    meta=CLIENT/(relative+'.meta')
    if (STAGED/relative).exists() and meta.exists():
        (STAGED/(relative+'.meta')).write_bytes(meta.read_bytes())
for path in STAGED.rglob('*.cs'):
    meta=Path(str(path)+'.meta')
    if not meta.exists(): meta.write_text('fileFormatVersion: 2\nguid: '+uuid.uuid5(uuid.NAMESPACE_URL,'qdao-gameplay-fidelity/'+path.name).hex+'\n',encoding='utf-8')
folder=STAGED/'Assets/Resources/UI/Ugui/GameplayFidelity20261016'
Path(str(folder)+'.meta').write_text('fileFormatVersion: 2\nguid: '+uuid.uuid5(uuid.NAMESPACE_URL,'qdao-gameplay-fidelity/asset-folder').hex+'\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n',encoding='utf-8')
original=(CLIENT/'Assets/Scripts/UI/Ugui/Gameplay/GameplayWindow.cs').read_text(encoding='utf-8-sig')
staged=(STAGED/'Assets/Scripts/UI/Ugui/Gameplay/GameplayWindow.cs').read_text(encoding='utf-8-sig')
api=lambda s: sorted(re.findall(r'^        public (?!sealed)([^\n{;]+)',s,re.M))
assert api(original)==api(staged), 'Public API was changed'
sprites=json.loads((ROOT/'slice-manifest.json').read_text(encoding='utf-8'))['sprites']
for item in sprites:
    p=folder/(item['name']+'.png'); im=Image.open(p); im.verify()
    assert sha(p)==item['sha256']
    meta=Path(str(p)+'.meta').read_text(encoding='utf-8')
    for setting in ('spriteMode: 1','spriteMeshType: 0','spritePixelsToUnits: 100','enableMipMap: 0','textureCompression: 0','maxTextureSize: 4096'):
        assert setting in meta, f'{p.name}: missing {setting}'
files=[]
for path in sorted(STAGED.rglob('*')):
    if path.is_file():
        relative=path.relative_to(STAGED).as_posix(); target=CLIENT/relative
        files.append(dict(path=relative,sha256=sha(path),action='replace' if target.exists() else 'add',expected_target_sha256=sha(target) if target.exists() else None))
(ROOT/'sourceguard.json').write_text(json.dumps(dict(schema='qdao.staged.sourceguard.v1',client_root=str(CLIENT),files=guards),indent=2),encoding='utf-8')
(ROOT/'install-manifest.json').write_text(json.dumps(dict(schema='qdao.gameplay.fidelity.install.v1',staging_root=str(STAGED),client_root=str(CLIENT),new_asset_postprocessor=False,source_guard='sourceguard.json',files=files),ensure_ascii=False,indent=2),encoding='utf-8')
result=dict(status='passed',public_api_unchanged=True,sprites_verified=len(sprites),files_to_install=len(files),image_generation_calls_in_resume=0,client_modified_by_this_agent=False,unity_started_by_this_agent=False,runtime_compile='see compile-validation.json; not a Unity execution result',test_execution='staged tests prepared and syntax-compiled only; root must run Unity Edit Mode tests after installation')
(ROOT/'package-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
