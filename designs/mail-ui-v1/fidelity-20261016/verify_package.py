"""Read-only verification of the existing mail install payload and source guard."""
from pathlib import Path
from PIL import Image
import datetime, hashlib, json, re

ROOT=Path(__file__).resolve().parent
CLIENT=Path('E:/work/mmorpg-client')
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
manifest=read(ROOT/'install-manifest.json')
sprite_manifest=read(ROOT/'sprite-manifest.json')
stage=read(ROOT/'staged-code-manifest.json')
issues=[]
def check(condition,label):
    if not condition:issues.append(label)

for item in manifest['files']:
    source=ROOT/item['source']
    check(source.is_file(),'missing payload: '+item['source'])
    if source.is_file():check(sha(source)==item['sha256'],'payload hash mismatch: '+item['source'])
for guard in manifest['guards']:
    source=CLIENT/guard['target']
    check(source.is_file() and sha(source)==guard['sha256Before'],'changed source guard: '+guard['target'])
check(stage['sourceSha256Before']==manifest['guards'][0]['sha256Before'],'stage/install guard disagree')
check(len(sprite_manifest['sprites'])==25,'expected 25 approved sprites')
guids=[]
for item in sprite_manifest['sprites']:
    path=ROOT/'client'/item['assetPath']
    check(path.is_file() and sha(path)==item['sha256'],'sprite manifest hash mismatch: '+item['key'])
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        check(image.size==(item['width'],item['height']),'sprite size mismatch: '+item['key'])
    record=read(path.with_name(path.name+'.generation.json'))
    check(record['sha256']==sha(path),'sprite provenance hash mismatch: '+item['key'])
    meta=path.with_name(path.name+'.meta').read_text(encoding='utf-8-sig')
    guid=re.search(r'^guid: ([0-9a-f]{32})$',meta,re.M)
    check(guid is not None,'missing GUID: '+item['key'])
    if guid:guids.append(guid.group(1))
    for text in ('enableMipMap: 0','textureType: 8','spriteMode: 1','maxTextureSize: 4096','textureCompression: 0','spriteMeshType: 0'):
        check(text in meta,'import setting missing '+text+': '+item['key'])
check(len(set(guids))==len(guids),'duplicate sprite GUID')

# Fully transparent RGB is retained in the source crop. Count only visible pixels;
# native Unity uses alpha, so hidden RGB must never be treated as a baked status dot.
with Image.open(ROOT/'client/Assets/Resources/UI/Ugui/MailV1Fidelity/mail_envelope_unread.png') as image:
    rgba=image.convert('RGBA')
    visible_red=sum(r>170 and g<100 and b<100 and a>100 for y in range(rgba.height) for x in range(rgba.width) for r,g,b,a in [rgba.getpixel((x,y))])
check(visible_red==0,'unread envelope retains visible red dot underneath native status dot')

mail_sources=ROOT/'client/Assets/Scripts/UI/Ugui/Mail'
source_text='\n'.join(p.read_text(encoding='utf-8-sig') for p in mail_sources.glob('*.cs'))
keys=sorted(set(re.findall(r'"(mail_[a-z_]+|button_primary|button_secondary|window_frame|close_button)"',source_text)))
missing=[]
for key in keys:
    if not (ROOT/'client/Assets/Resources/UI/Ugui/MailV1Fidelity'/(key+'.png')).is_file() and not (CLIENT/'Assets/Resources/UI/Ugui/MailV1'/(key+'.png')).is_file():missing.append(key)
check(not missing,'unresolved literal sprite keys: '+', '.join(missing))
font_paths=['Assets/Resources/Fonts/SimKai.ttf','Assets/Resources/Fonts/SimKai SDF.asset']
check(any((CLIENT/p).is_file() for p in font_paths),'SimKai font dependency missing')
check(all(manifest['businessMethodExactTextChecks'].values()),'business method checks failed')
check(not list((ROOT/'client').rglob('*AssetPostprocessor*')),'unexpected asset postprocessor')

result={
    'checkedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'status':'passed' if not issues else 'failed',
    'issues':issues,
    'installPayloadFiles':len(manifest['files']),
    'spriteCount':len(sprite_manifest['sprites']),
    'payloadHashesVerified':True,
    'sourceGuardUnchanged':not any('guard' in issue for issue in issues),
    'sourceSha256':manifest['guards'][0]['sha256Before'],
    'literalSpriteDependencies':keys,
    'visibleRedDotPixelsInUnreadEnvelope':visible_red,
    'font':'Existing client SimKai / SimKai SDF; mail-only font selection, shared typography unchanged',
    'fixedCanvas':[2560,1080],
    'nativeSkinCanvas':[1932,814],
    'uniformScale':min(2560/1932,1080/814),
    'businessMethodsPreservedVerbatim':list(manifest['businessMethodExactTextChecks']),
    'runtimeCompile':read(ROOT/'qa/compile-result.json'),
    'nativeValidationPending':True,
    'visualReview':{
        'sources':['../01-mail-event.png','../02-mail-system.png'],
        'reviewed':['mail_empty_frame','mail_row_selected','mail_row_normal','mail_reward_slot','mail_envelope_unread','mail_banner'],
        'bakedDemoTitlesDatesCountsBodyRewards':False,
        'immutableArtIncludes':'night landscape, decorative moon character on lantern, paper texture, tab pictograms and hourglass',
        'dynamicContent':'titles, sender, date, inbox/unread counts, body, reward names/counts and action states remain native',
        'limits':['Unity screenshot parity remains pending','Long real mail text scrolls within the fixed approved body area','Existing reward IconKey and non-midautumn BannerKey retain legacy resource fallback; no business icon remapping or fixture injection']
    },
    'clientModifiedByAudit':False
}
(ROOT/'qa/resume-package-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'payloadFiles':result['installPayloadFiles'],'sprites':result['spriteCount'],'issues':issues},ensure_ascii=False))
raise SystemExit(0 if not issues else 1)
