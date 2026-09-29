from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent.parent
P=R/'20-work/export-v1/20_star_formation_master_girl'
O=R/'20-delivery-preview'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]; gifs=[]
for d in ['N','NE']:
    for slot in [f'walk/{d}/{n:02d}.png' for n in range(1,17)]+[f'idle/{d}.png']:
        p=P/slot; m=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
        im=Image.open(p); a=np.asarray(im.getchannel('A')); yy,xx=np.where(a>8)
        source=Path(m['derivedFrom']['path']); gen=json.loads(Path(m['derivedFrom']['generationRecord']).read_text(encoding='utf-8-sig'))
        assert im.size==(1024,1024) and im.mode=='RGBA'
        assert sha(p)==m['sha256'] and sha(source)==m['derivedFrom']['sha256']==gen['sha256']
        assert gen['width']>=1024 and gen['height']>=1024
        assert yy.max()==942 and not any(np.any(e>8) for e in [a[0,:],a[-1,:],a[:,0],a[:,-1]])
        rows.append({'slot':slot,'sha256':sha(p),'size':list(im.size),'mode':im.mode,'alphaLowestY':int(yy.max()),'alphaBoundingBox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'nativeSourceSha256':sha(source),'nativeSize':[gen['width'],gen['height']],'sourceAttempt':source.parent.name,'actualModel':gen.get('actualModel'),'actualQuality':gen.get('actualQuality')})
    for mode in ['dark','light']:
        p=O/f'{d}-30ms-{mode}.gif'; im=Image.open(p); durations=[]
        for n in range(im.n_frames):im.seek(n);durations.append(im.info['duration'])
        assert im.n_frames==16 and durations==[30]*16
        gifs.append({'file':p.name,'sha256':sha(p),'frames':16,'frameMs':30,'cycleMs':480})
assert len(set(r['sha256'] for r in rows))==34
assert len(set(r['nativeSourceSha256'] for r in rows))==34
out={'at':datetime.now(timezone.utc).isoformat(),'rows':rows,'gifs':gifs,'count':34,'uniqueFiles':34,'uniqueNativeSources':34,'allPass':True,'manifestSha256':sha(O/'manifest.json')}
(R/'20-tools/N-NE-final-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'count':34,'allPass':True,'topRanges':{d:[min(r['alphaBoundingBox'][1] for r in rows if f'/{d}/' in r['slot']),max(r['alphaBoundingBox'][1] for r in rows if f'/{d}/' in r['slot'])] for d in ['N','NE']}}))
