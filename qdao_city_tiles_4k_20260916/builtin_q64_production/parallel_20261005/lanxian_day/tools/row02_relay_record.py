from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
from PIL import Image
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c10')
p=B/'worker-row02.json'
w=json.loads(p.read_text(encoding='utf-8-sig'))
obs={
'r02_c04':[
'Actually viewed target guide, north native r01_c04, west native r02_c03 and approved04-guild style; all four actual submitted references recorded.',
'Actual output view: curved grey stone balustrade, three cropped/whole openings, right-center capped post, existing top-right rear post base, ivory paving and original shadow retain guide footprint.',
'No imported leaves, new text or objects; clean rounded stone shading and original engraved edges. No obvious full-image contour truncation; full assembly QA still pending.'],
'r02_c03':[
'Actually viewed layout guide, north native r01_c03, west native r02_c02 and approved04-guild style; all four were actual submitted references.',
'Actual output view: rear gray post, bridge side, front balustrade post, openings and existing foliage shadow retain guide footprint; no new red lamp or object imported from neighboring crop.',
'Existing joint and bevel silhouettes readable, no obvious interior truncation in full native view; small subdued stone marks inherited from guide. Full assembled seams still require QA.'],
'r02_c02':[
'Actually viewed guide, approved04-guild style, west r02_c01 and north r01_c02 full native sources before submission; actual prompt and four references saved.',
'Actual output view: cropped red lamp post and two right curled arms, gold beads, blank gold panel, native footprint of gray bridge post, bottom cropped green leaves and existing right foliage shadow retained.',
'No new objects or lettering; central stone remains clean with painterly patches. Full assembly joint matching still requires native-resolution QA.']
}
for cell, observations in obs.items():
    image=B/'native'/f'{cell}.png'
    generation=image.with_suffix('.png.generation.json')
    g=json.loads(generation.read_text(encoding='utf-8-sig'))
    sha=hashlib.sha256(image.read_bytes()).hexdigest()
    assert sha==g['sha256']
    with Image.open(image) as im: assert im.size==(1254,1254);size=list(im.size)
    item={'cell':cell,'file':str(image),'sha256':sha,'sourceOutputPath':g['evidence']['sourceOutputPath'],'pixels':size,'actualViewPerformed':True,'guideAndStyleViewed':True,'observations':observations,'formalAccepted':False}
    w['sources']=[s for s in w['sources'] if s['cell']!=cell]+[item]
w['sources'].sort(key=lambda s:s['cell'])
for item in w['sources']:
    f=Path(item['file'])
    assert hashlib.sha256(f.read_bytes()).hexdigest()==item['sha256']
w.update(status='native_row_complete_actual_viewed_not_full_tile_approval',generatedNativeFragments=len(w['sources']),updatedAtUtc=datetime.now(timezone.utc).isoformat(),continuationWorker='row02_relay',actualModel=None,actualQuality=None)
p.write_text(json.dumps(w,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'record':str(p),'completed':len(w['sources'])}))
