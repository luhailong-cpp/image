from pathlib import Path
import json,hashlib,datetime,sys,re
from PIL import Image
Z=Path(__file__).resolve().parent
stem=sys.argv[1];note=sys.argv[2]
assert re.fullmatch(r'r02_c01_s0[1-4]_0[1-4]_a[0-9]+',stem)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sp=Z/'connected-coast-current-selection-20261016.json';s=read(sp)
e=next(x for x in s['archivedSources'] if x['stem']==stem)
assert sha(e['path'])==e['sha256'] and sha(e['generationRecord'])==e['generationSha256']
g=read(e['generationRecord']);assert Image.open(e['path']).size==(1254,1254)
r,c=map(int,re.search(r'_s(\d+)_(\d+)_',stem).groups())
qp=Z/'qa'/f'{stem}.quick-review-connected-20261016.json'
q={'schemaVersion':1,'reviewer':'/root/connected_continuation','image':{'path':e['path'],'sha256':e['sha256']},'generationRecord':{'path':e['generationRecord'],'sha256':e['generationSha256']},'viewedAtNativeSize':[1254,1254],'scope':'quick layout and neighbor-edge owner check for continuing production only','layoutStatus':'PASS','continueProduction':True,'geometryClosurePassed':False,'materialStatus':'PENDING','internalClosurePassed':False,'formalAccepted':False,'notes':[note],'recordedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with qp.open('x',encoding='utf-8') as f:json.dump(q,f,ensure_ascii=False,indent=2);f.write('\n')
assert not any(x['row']==r and x['col']==c for x in s['selectedNative'])
s['selectedNative'].append({**e,'row':r,'col':c,'globalBox':g['globalBox'],'coreBox':g['coreBox'],'quickReview':{'path':qp.as_posix(),'sha256':sha(qp)},'status':'selected_for_assembly_pending_internal_seam_and_material_QA'})
s['selectedNative'].sort(key=lambda x:(x['row'],x['col']));s['selectedCoreCount']=len(s['selectedNative']);s['updatedAtUtc']=q['recordedAtUtc']
sp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'stem':stem,'selected':len(s['selectedNative']),'imageSha256':e['sha256'],'quickReview':qp.as_posix()}))
