from pathlib import Path
import json, hashlib
from PIL import Image

D=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/lanxian_spring/triple_r08_c06_c08')
Q=D/'qa_v2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def j(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
im=Image.open(D/'output_v2/extended-context.png').convert('RGB')
rows=[]
for repair in j(D/'output_v2/assembly.json')['repairs']:
    l,t,r,b=[v+115 for v in repair['rectTripleXYXY']]
    boxes={'top':[l-100,t-100,r+100,t+100], 'bottom':[l-100,b-100,r+100,b+100],
           'left':[l-100,t-100,l+100,b+100], 'right':[r-100,t-100,r+100,b+100]}
    for side,box in boxes.items():
        f=Q/f"{repair['id']}-actual-roi-{side}.png"
        assert not f.exists()
        im.crop(box).save(f)
        rows.append({'repair':repair['id'],'side':side,'file':str(f),'cropExtendedXYXY':box,'sha256':sha(f),'resized':False})
for name,box in [('upper-outer-context-return',(7780,15,8834,330)),('bottom-outer-context-return',(7780,4000,8834,4311))]:
    f=Q/f'{name}.png';assert f.exists()
    rows.append({'kind':'outer-context-return','file':str(f),'cropExtendedXYXY':box,'sha256':sha(f),'resized':False})
identical=[];changed=[]
for p in sorted(Q.glob('*.png')):
    prev=D/'qa_v2'/p.name
    if prev.exists():
        (identical if sha(p)==sha(prev) else changed).append(p.name)
report={'source':str(D/'output_v2/extended-context.png'),'sourceSha256':sha(D/'output_v2/extended-context.png'),'actualRoiEdges':rows,'identicalV2Qa':identical,'changedV2Qa':changed}
(Q/'four-edge-crops.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'identical':identical,'changed':changed}))

