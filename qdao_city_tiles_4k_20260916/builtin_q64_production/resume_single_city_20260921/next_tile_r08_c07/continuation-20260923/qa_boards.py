from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,sys
v=Path(sys.argv[1]).resolve()
idx=json.loads((v/'qa/index.json').read_text(encoding='utf-8-sig'))
out=v/'qa-boards';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for group in idx['internalSeams']:
    items=[next(e for e in idx['evidence'] if e['id']==s) for s in group['segments']]
    board=Image.new('RGB',(1024,1024))
    maps=[]
    for n,item in enumerate(items):
        f=Path(item['artifact']['path']);assert sha(f)==item['artifact']['sha256']
        im=Image.open(f);xy=(n*256,0) if group['id'].startswith('vertical') else (0,n*256)
        board.paste(im,xy);maps.append({'source':item['artifact'],'pasteXY':xy,'crop':item['candidateCropLTRB']})
    dest=out/(group['id']+'.png');board.save(dest);records.append({'file':str(dest),'sha256':sha(dest),'pixelScale':'1:1','parts':maps})
for kind,name,w,h in [('internal_four_patch_junction','junctions',768,768),('external_neighbor_edge_segment','bottom-edge',1024,1024)]:
    items=[e for e in idx['evidence'] if e['kind']==kind];board=Image.new('RGB',(w,h));maps=[]
    for n,item in enumerate(items):
        f=Path(item['artifact']['path']);assert sha(f)==item['artifact']['sha256']
        xy=((n%3)*256,(n//3)*256) if name=='junctions' else (0,n*256)
        board.paste(Image.open(f),xy);maps.append({'source':item['artifact'],'pasteXY':xy,'id':item['id']})
    dest=out/(name+'.png');board.save(dest);records.append({'file':str(dest),'sha256':sha(dest),'pixelScale':'1:1','parts':maps})
candidate=Path(idx['candidate']['path']);image=Image.open(candidate)
image.resize((1024,1024),Image.Resampling.LANCZOS).save(out/'overview-preview-only.png')
(out/'index.json').write_text(json.dumps({'createdAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':idx['candidate'],'boards':records,'reviewed':False,'overview':'preview only, not original-pixel evidence'},indent=2),encoding='utf-8')
print(str(out))
