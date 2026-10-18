import sys,json,hashlib,re
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
QA=ROOT/'qa'; TILE='r14_c05'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p,role):return {'path':p.as_posix(),'sha256':sha(p),'role':role}
patchid=sys.argv[1]; stem=TILE+'_'+patchid+'_v1'
rule=Path('D:/work/image/AGENTS.md'); split=Path('D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json')
rules_text=rule.read_text(encoding='utf-8-sig'); division=read(split)
assert '允许继续使用现有内置绘图工具' in rules_text
reserved=[t for b in division['batches'] if b['map']=='fishing-village-game-20261009' and b['status']=='allocated_root_reserved' for t in b['tiles']]
assert TILE not in reserved
for ext in ['.request.json','.png','.receipt.json']:
 assert not (ROOT/'native'/(stem+ext)).exists(),stem+ext+' already exists; recover rather than duplicate'
plan=read(ROOT/'coordinate-plan.json'); tile=next(t for t in plan['tiles'] if t['tile']==TILE)
patch=next(p for p in tile['patches'] if p['id']==patchid); box=patch['globalContextBox']
refs=read(ROOT/'references.json'); source=Path(refs[0]['path'])
layout=QA/(TILE+'-layout-only-20261016.png')
base=QA/(stem+'-layout-only.png')
with Image.open(source) as im:
 for dest,gbox in [(layout,tile['globalCoreBox']),(base,box)]:
  if not dest.exists():
   im.transform((1254,1254),Image.Transform.EXTENT,[v*1254/57344 for v in gbox],resample=Image.Resampling.NEAREST).save(dest)
   write(Path(str(dest)+'.derivation.json'),{'role':'layout-only enlarged guide; never final pixels','source':ref(source,'approved layout'),'globalBox':gbox,'operation':'coordinate crop nearest enlargement'})
canvas=Image.open(base).convert('RGB'); sources=[]
for rp in sorted((ROOT/'native').glob(TILE+'_p*_v1.png.generation.json')):
 rec=read(rp)
 if any(x in rec.get('status','') for x in ['rejected','superseded','frozen']):continue
 sources.append({'path':rec['file'],'sha256':rec['sha256'],'box':rec['coordinates']['globalContextBox']})
east=QA/'pair-r14c06-r14c07-v3-r14_c06-context-native.png'
assert sha(east)=='3d59c2c8d07563732944bcc4d2948d8a48fad863c9f59a59a739fda79a312053'
sources.append({'path':east.as_posix(),'sha256':sha(east),'box':[5*4096-115,13*4096-115,6*4096+115,14*4096+115]})
overlaps=[]
for src in sources:
 sb=src['box']; inter=[max(box[0],sb[0]),max(box[1],sb[1]),min(box[2],sb[2]),min(box[3],sb[3])]
 if inter[2]<=inter[0] or inter[3]<=inter[1]:continue
 assert inter[2]-inter[0]<=230 or inter[3]-inter[1]<=230
 with Image.open(src['path']) as im:canvas.paste(im.crop((inter[0]-sb[0],inter[1]-sb[1],inter[2]-sb[0],inter[3]-sb[1])),(inter[0]-box[0],inter[1]-box[1]))
 overlaps.append({**src,'globalOverlapBox':inter,'targetBox':[inter[0]-box[0],inter[1]-box[1],inter[2]-box[0],inter[3]-box[1]],'role':'protected native overlap'})
guide=QA/(stem+'-continuity.png');canvas.save(guide)
write(Path(str(guide)+'.derivation.json'),{'role':'mixed edit guide, protected native overlaps, enlarged layout elsewhere guidance only','operation':'native integer crop and paste; no native resampling or painting','baseGuide':base.as_posix(),'nativeSources':overlaps})
request={'stem':stem,'tile':TILE,'patch':patchid,'coordinates':patch,'references':[ref(guide,'edit target: exact layout plus native overlaps'),*refs,ref(layout,'larger tile layout-only context')],'overlaps':overlaps,'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'guardrailRead':{'readAtUtc':datetime.now(timezone.utc).isoformat(),'AGENTS':sha(rule),'split':sha(split),'reservedExcluded':reserved},'northBoundary':'r13_c05 root in progress: no unstable north sources consumed'}
write(ROOT/'native'/(stem+'.request.json'),request)
print(json.dumps({'stem':stem,'guide':guide.as_posix(),'layout':layout.as_posix(),'overlaps':overlaps,'guardrailRead':request['guardrailRead']}))

