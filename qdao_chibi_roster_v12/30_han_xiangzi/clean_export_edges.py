"""Remove magenta backdrop RGB spill using only existing adjacent subject colors.
Alpha, silhouette, pixel locations and body geometry remain unchanged.
"""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from process_roster import DIRECTIONS, DEFAULT_PROCESSOR, load_processor, compose, sha, write_json
root=Path(__file__).resolve().parent
record={'operation':'RGB chroma-spill replacement from nearest existing non-magenta opaque subject pixel','reason':'Han Xiangzi has blue/white/navy cloth, black hair and gold/jade accents; purple/magenta is backdrop spill','geometry_and_alpha_unchanged':True,'files':{}}
paths=[root/'walk'/d/f'{i:02d}.png' for d in DIRECTIONS for i in range(1,9)]+[root/'idle'/f'{d}.png' for d in DIRECTIONS]
offsets=sorted([(dx*dx+dy*dy,dy,dx) for dy in range(-12,13) for dx in range(-12,13) if dx or dy])
for path in paths:
    a=np.array(Image.open(path).convert('RGBA')); before=a.copy()
    r,g,b=a[:,:,:3].astype(int).transpose(2,0,1)
    bad=(r>g+20)&(b>g+20)&(np.minimum(r,b)>45)&(a[:,:,3]>0)
    valid=(~bad)&(a[:,:,3]>=128)
    ys,xs=np.where(bad); pending=np.ones(len(ys),dtype=bool)
    for _,dy,dx in offsets:
        indices=np.flatnonzero(pending)
        if not len(indices): break
        cy=ys[indices]+dy; cx=xs[indices]+dx
        inside=(cy>=0)&(cx>=0)&(cy<a.shape[0])&(cx<a.shape[1])
        indices=indices[inside]; cy=cy[inside]; cx=cx[inside]
        ok=valid[cy,cx]; chosen=indices[ok]
        a[ys[chosen],xs[chosen],:3]=before[cy[ok],cx[ok],:3]
        pending[chosen]=False
    if pending.any():
        vy,vx=np.where(valid)
        for i in np.flatnonzero(pending):
            k=np.argmin((vy-ys[i])**2+(vx-xs[i])**2)
            a[ys[i],xs[i],:3]=before[vy[k],vx[k],:3]
    assert np.array_equal(a[:,:,3],before[:,:,3])
    pre=sha(path); Image.fromarray(a).save(path)
    record['files'][path.relative_to(root).as_posix()]={'affected_rgb_pixels':len(ys),'alpha_unchanged':True,'before_sha256':pre,'after_sha256':sha(path),'rgba_sha256':hashlib.sha256(a.tobytes()).hexdigest()}
processor=load_processor(DEFAULT_PROCESSOR)
walk={d:[Image.open(root/'walk'/d/f'{i:02d}.png').convert('RGBA') for i in range(1,9)] for d in DIRECTIONS}
idle={d:Image.open(root/'idle'/f'{d}.png').convert('RGBA') for d in DIRECTIONS}
for d in DIRECTIONS:
    compose(walk[d],8).save(root/'walk'/d/'strip.png')
    processor.save_transparent_gif(walk[d],root/'walk'/d/'walk.gif',60)
compose([f for d in DIRECTIONS for f in walk[d]],8).save(root/'processing/walk-review.png')
compose([idle[d] for d in DIRECTIONS],4).save(root/'processing/idle-review.png')
transforms=json.loads((root/'processing/frame-transforms.json').read_text(encoding='utf-8'))
for d in DIRECTIONS:
    for i,item in enumerate(transforms['walk'][d],1):
        item['rgba_sha256']=record['files'][f'walk/{d}/{i:02d}.png']['rgba_sha256']
        item['rgb_edge_cleanup']='processing/edge-cleanup.json'
    transforms['idle'][d]['rgba_sha256']=record['files'][f'idle/{d}.png']['rgba_sha256']
    transforms['idle'][d]['rgb_edge_cleanup']='processing/edge-cleanup.json'
write_json(root/'processing/frame-transforms.json',transforms)
manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
for item in manifest['files']:
    p=root/item['path']; item.update(sha256=sha(p),bytes=p.stat().st_size)
manifest['final_edge_cleanup']='processing/edge-cleanup.json'
write_json(root/'manifest.json',manifest)
write_json(root/'processing/edge-cleanup.json',record)
print(json.dumps({'processed_files':len(paths),'affected_rgb_pixels':sum(x['affected_rgb_pixels'] for x in record['files'].values()),'alpha_and_geometry':'unchanged'}))
