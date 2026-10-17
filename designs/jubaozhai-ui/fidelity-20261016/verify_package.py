from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageOps
import hashlib,json,re,uuid
from collections import Counter
ROOT=Path(__file__).resolve().parent;CLIENT=Path('E:/work/mmorpg-client');STAGED=ROOT/'staged'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ROOT/'asset-manifest.json').read_text(encoding='utf-8'))
guards=[]
for relative in ('Assets/Scripts/UI/Ugui/Jubaozhai/JubaozhaiWindow.cs','Assets/Scripts/UI/Ugui/Jubaozhai/JubaozhaiArt.cs','Assets/Scripts/UI/Ugui/Jubaozhai/JubaozhaiUiRoot.cs','Assets/Scripts/Game/Jubaozhai/JubaozhaiModels.cs','Assets/Scripts/Game/Jubaozhai/JubaozhaiClient.cs'):
    guards.append(dict(path=relative,sha256=sha(CLIENT/relative)))
    if (STAGED/relative).exists():(STAGED/(relative+'.meta')).write_bytes((CLIENT/(relative+'.meta')).read_bytes())
for item in manifest['reused_existing_sprites']:
    assert sha(CLIENT/item['client_path'])==item['sha256']
    guards.append(dict(path=item['client_path'],sha256=item['sha256']))

original=(CLIENT/'Assets/Scripts/UI/Ugui/Jubaozhai/JubaozhaiWindow.cs').read_text(encoding='utf-8-sig')
staged=(STAGED/'Assets/Scripts/UI/Ugui/Jubaozhai/JubaozhaiWindow.cs').read_text(encoding='utf-8-sig')
api=lambda text:sorted(re.findall(r'^        public (?!sealed)([^\n{;]+)',text,re.M))
assert api(original)==api(staged),'public API changed'
calls=lambda text:Counter(re.findall(r'\bState\.(\w+)\s*\(',text))
assert calls(original)==calls(staged),f'State call counts changed: {calls(original)} != {calls(staged)}'
assert 'LoadDemo(' not in staged
protected=('Show','Hide','Back','ResetSession','Dispose','Tick','StateChanged','SelectListing','SelectedListing','UpdateSelection','ToggleSelectedFavorite','ShowSelectedDetails','ServerStatusText','ModalStatusText','ShowNotice','OpenModal','CloseModal','ConstrainFocus','BoundNavigation','SameListing','CycleSort','SortLabel')
def method(text,name):
    matches=list(re.finditer(r'^        (?:public|private)\s+(?:static\s+)?[\w<>,.\[\]?]+\s+'+name+r'\(',text,re.M));assert len(matches)==1,name
    start=matches[0].start();close=text.index(')',matches[0].end());tail=close+1
    while text[tail].isspace():tail+=1
    if text[tail:tail+2]=='=>':return text[start:text.index(';',tail)+1]
    assert text[tail]=='{',name
    level=1;end=tail+1
    while level:
        if text[end]=='{':level+=1
        elif text[end]=='}':level-=1
        end+=1
    return text[start:end]
for name in protected:assert method(original,name)==method(staged,name),f'protected business/focus method changed: {name}'

for path in STAGED.rglob('*.cs'):
    meta=Path(str(path)+'.meta')
    if not meta.exists():meta.write_text('fileFormatVersion: 2\nguid: '+uuid.uuid5(uuid.NAMESPACE_URL,'jubaozhai-fidelity/'+path.name).hex+'\n',encoding='utf-8')
folder=STAGED/'Assets/Resources/UI/Ugui/JubaozhaiFidelity20261016'
Path(str(folder)+'.meta').write_text('fileFormatVersion: 2\nguid: '+uuid.uuid5(uuid.NAMESPACE_URL,'jubaozhai-fidelity/native-assets').hex+'\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n',encoding='utf-8')
for item in manifest['new_assets']:
    p=ROOT/item['output'];assert sha(p)==item['sha256'];im=Image.open(p);im.verify()
    meta=Path(str(p)+'.meta').read_text(encoding='utf-8')
    for setting in ('spriteMode: 1','spriteMeshType: 0','spritePixelsToUnits: 100','textureCompression: 0','enableMipMap: 0','maxTextureSize: 4096'):assert setting in meta,(p.name,setting)
source=Image.open(ROOT.parent/'01-empty.png').convert('RGB');frame=Image.open(folder/'native-frame.png').convert('RGB')
mask=Image.new('L',source.size,0);draw=ImageDraw.Draw(mask)
for x0,y0,x1,y1 in ((198,197,468,735),(498,135,1729,773)):draw.rectangle((x0,y0,x1-1,y1-1),fill=255)
outside=ImageChops.multiply(ImageChops.difference(source,frame).convert('L'),ImageOps.invert(mask))
assert outside.getbbox() is None,'source exterior/ornament pixels changed'
files=[]
for path in sorted(STAGED.rglob('*')):
    if path.is_file():
        rel=path.relative_to(STAGED).as_posix();target=CLIENT/rel
        files.append(dict(path=rel,sha256=sha(path),action='replace' if target.exists() else 'add',expected_target_sha256=sha(target) if target.exists() else None))
(ROOT/'sourceguard.json').write_text(json.dumps(dict(schema='qdao.jubaozhai.fidelity.sourceguard.v1',client_root=str(CLIENT),files=guards,protected_methods=list(protected)),ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'install-manifest.json').write_text(json.dumps(dict(schema='qdao.jubaozhai.fidelity.install.v1',staging_root=str(STAGED),client_root=str(CLIENT),source_guard='sourceguard.json',files=files,new_asset_postprocessor=False),ensure_ascii=False,indent=2),encoding='utf-8')
result=dict(status='passed',public_api_unchanged=True,state_call_counts_unchanged=True,protected_methods_byte_identical=len(protected),existing_sprites_reused=len(manifest['reused_existing_sprites']),new_derived_sprites=len(manifest['new_assets']),source_exterior_and_ornament_pixels_unchanged=True,files_to_install=len(files),new_ai_generation_calls=0,client_modified=False,unity_started=False,test_execution='not run in Unity; syntax compilation only')
(ROOT/'package-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
