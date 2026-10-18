from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p): return {'path':Path(p).as_posix(),'sha256':sha(p)}
ap=Z/'current-adopted-20261012.json';a=json.loads(ap.read_text(encoding='utf-8-sig'))
ls=next(x for x in a['tiles'] if x['tileId']=='r03_c01');rs=next(x for x in a['tiles'] if x['tileId']=='r03_c02')
assert ls['image']['sha256']=='0686b42815ff39b6d262675feaa14e74065a4143f85a7f1ebb9d8473ecbe1256'
assert rs['image']['sha256']=='8656bb1a4e07b91711d60ad68f1225abe27667c3647db43d07fa9f3f6a8a0bfa'
for s in [ls,rs]:
 for k in ['image','record']: assert sha(s[k]['path'])==s[k]['sha256']
left=Image.open(ls['image']['path']).convert('RGB');right=Image.open(rs['image']['path']).convert('RGB')
qd=Z/'qa/r03_c01_v11_r03_c02_v7_shared_root_20261016';qd.mkdir(exist_ok=False)
items=[]
for i,(y0,y1) in enumerate([(0,1139),(909,2163),(1933,3187),(2957,4096)],1):
 out=Image.new('RGB',(480,y1-y0));out.paste(left.crop((3856,y0,4096,y1)),(0,0));out.paste(right.crop((0,y0,240,y1)),(240,0));p=qd/f'shared_east_west_segment{i}_100pct.png';out.save(p)
 items.append({**pin(p),'leftTileCropBox':[3856,y0,4096,y1],'rightTileCropBox':[0,y0,240,y1],'dimensions':[480,y1-y0],'sharedEdgeX':240,'nativeScale100Percent':True,'visualStatus':'PENDING'})
q={'left':{k:ls[k] for k in ['tileId','image','record']},'right':{k:rs[k] for k in ['tileId','image','record']},'selectionSource':pin(ap),'sharedEdgePixelsCovered':4096,'items':items,'method':'Exact native RGB crop and side-by-side join for QA only. No resampling, blending, correction or art changes.','formalAccepted':False}
op=qd/'qa_index.json';op.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(pin(op)))
