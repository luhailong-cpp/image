from pathlib import Path
from PIL import Image
import datetime, hashlib, json, shutil

ROOT = Path('E:/work/image')
CLIENT = Path('E:/work/mmorpg-client')
PACKAGE = ROOT / 'qdao_ui_redesign_v5/fidelity-20261016/login-revision-20261017'
ASSET = 'Assets/Resources/UI/Ugui/CoreFidelity20261016/'
OUT = PACKAGE / 'client' / ASSET
OUT.mkdir(parents=True, exist_ok=True)
source = ROOT / 'qdao_ui_redesign_v5/01_login_2560x1080.png'
clean_source = ROOT / 'qdao_ui_redesign_v5/fidelity-20261016/art/login-clean.png'
original = Image.open(source).convert('RGBA')
clean = Image.open(clean_source).convert('RGBA').resize(original.size, Image.Resampling.LANCZOS)
shell = original.copy()
# Only the actual server name, availability and state dot vary at runtime.
# Feather inside the paper surface; no frame, logo, scene or action lettering changes.
box = (286, 564, 756, 630)
w, h = box[2]-box[0], box[3]-box[1]
mask = Image.new('L', (w, h))
mask.putdata([round(255 * min(1, min(x, y, w-1-x, h-1-y)/10))
              for y in range(h) for x in range(w)])
shell.paste(clean.crop(box), box[:2], mask)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
files = []
sprites = {
 'login_shell': (shell, None),
 'login_server_bar': (shell.crop((230,548,1040,648)), [230,548,810,100]),
 'login_enter': (original.crop((272,676,1005,843)), [272,676,733,167]),
 'login_announcement_original': (original.crop((2200,20,2380,205)), [2200,20,180,185]),
 'login_settings_original': (original.crop((2375,20,2555,205)), [2375,20,180,185]),
}
for key, (im, rect) in sprites.items():
    target = ASSET + key + '.png'
    path = OUT / (key+'.png')
    im.save(path)
    old = CLIENT / target
    item = {'source': 'client/'+target, 'target': target, 'sha256': sha(path)}
    if old.exists(): item['expected_target_sha256'] = sha(old)
    files.append(item)
    meta = path.with_name(path.name+'.meta')
    old_meta = old.with_name(old.name+'.meta')
    template = (CLIENT / (ASSET+'login_enter.png.meta')).read_text(encoding='utf-8')
    if old_meta.exists():
        template = old_meta.read_text(encoding='utf-8')
    else:
        old_guid = next(line for line in template.splitlines() if line.startswith('guid: '))[6:]
        guid = hashlib.sha256(('login-original-20261017/'+key).encode()).hexdigest()[:32]
        template = template.replace(old_guid, guid)
    import re
    template = re.sub(r'spriteBorder: \{[^\n]+\}', 'spriteBorder: {x: 0, y: 0, z: 0, w: 0}', template)
    meta.write_text(template, encoding='utf-8')
    mf = {'source':'client/'+target+'.meta','target':target+'.meta','sha256':sha(meta)}
    if old_meta.exists(): mf['expected_target_sha256'] = sha(old_meta)
    files.append(mf)
    write(path.with_name(path.name+'.generation.json'), {
      'file':path.name,'sha256':sha(path),'derivedAt':now,'width':im.width,'height':im.height,
      'newAiGeneration':False,'actualModel':None,'actualQuality':None,
      'modelBasis':'Original approved historical art: model/quality not established by historical manifest. Clean patch traces its own built-in generation record.',
      'operation':'Original pixels, native crop without resampling' if rect and key!='login_server_bar' else 'Original full artwork; only dynamic server region replaced by feathered matching clean paper; no static art regenerated',
      'sourceRectXYWH':rect,'dynamicMaskXYXY':list(box) if key in ['login_shell','login_server_bar'] else None,
      'derivedFrom':[{'path':str(source),'sha256':sha(source),'record':str(ROOT/'qdao_ui_redesign_v5/manifest.json')}] +
       ([{'path':str(clean_source),'sha256':sha(clean_source),'record':str(clean_source)+'.generation.json','use':'dynamic server-paper area only; resized from actual source to design canvas'}] if key in ['login_shell','login_server_bar'] else [])})

write(PACKAGE/'art-install-manifest.json',{'scope':'Restore approved original login static artwork and exact action lettering; no new AI image generation','files':files})
# Final native comparison checks the immutable area; dynamic labels are native data.
write(PACKAGE/'source-geometry.json',{'sourceCanvas':[2560,1080],'dynamicServerMaskXYXY':list(box),
 'announcement':[2200,20,180,185],'settings':[2375,20,180,185],
 'enterGame':[272,676,733,167],'serverBar':[230,548,810,100],
 'expectedImmutablePixels':'Byte-equivalent decoded RGBA outside the dynamic server mask before Unity rendering.'})
print(json.dumps({'sprites':len(sprites),'files':len(files),'package':str(PACKAGE)}))
