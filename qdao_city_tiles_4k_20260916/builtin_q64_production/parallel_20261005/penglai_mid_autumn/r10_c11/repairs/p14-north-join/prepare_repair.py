from pathlib import Path
import json,hashlib,shutil,sys
from datetime import datetime,timezone
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
TILE=HERE.parents[1]
ROOT=TILE.parent
sys.path.insert(0,str(ROOT/'tools/multi_edge'))
import engine

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def save_image(name,pixels,operation,sources):
    p=HERE/name;assert not p.exists(),p
    image=Image.fromarray(pixels) if isinstance(pixels,np.ndarray) else pixels
    image.save(p)
    write(str(p)+'.generation.json',{**ref(p),'createdAt':datetime.now(timezone.utc).isoformat(),'operation':operation,'sources':sources,'pixels':list(image.size),'scale':1,'sourceUpscaling':False,'actuallyViewed':False,'formalAccepted':False})
    return p

def prepare():
    original=TILE/'native/p14.png';generation=Path(str(original)+'.generation.json');request=read(TILE/'native/p14.request.json')
    assert not (HERE/'input-original.png').exists()
    history=read(generation);assert history['sha256']==sha(original)
    shutil.copyfile(original,HERE/'input-original.png');shutil.copyfile(generation,HERE/'input-original.generation-history.json')
    sources={'p14':np.asarray(Image.open(original).convert('RGB'))};refs={'p14':ref(original)};ops=[]
    for record in request['contextRegions']:
        path=Path(record['file']);assert sha(path)==record['sha256']
        sources[record['source']]=np.asarray(Image.open(path).convert('RGB'));refs[record['source']]=ref(path)
        ops.append({k:record[k] for k in ['source','cropLTRB','pasteXY','role','scale']})
    layout=engine.Layout();context,known=engine.materialize_context(layout,ops,sources)
    target=np.where(known[:,:,None],context,sources['p14'])
    save_image('actual-context-target.png',target,{'kind':'actual frozen N/NE/E context pasted over retained native draft','regions':ops},list(refs.values()))
    owner=engine.owner_mask(known,['right','top'],layout)
    merged,flow,tone,report=engine.register_native(context,sources['p14'],known,owner,['right','top'],layout,max_shift=6.,tone_cap=18.,return_depth=256)
    save_image('original-bounded-registration-preview.png',merged,{'kind':'diagnostic only; exact production registration limits 6/18/256; no acceptance'},list(refs.values()))
    np.save(HERE/'original-diagnostic.flow.npy',flow);np.save(HERE/'original-diagnostic.tone.npy',tone)
    write(HERE/'original-diagnostic.json',dict(report=report,source=ref(original),preview=ref(HERE/'original-bounded-registration-preview.png'),formalAccepted=False,automaticVisualPass=False))
    crops={'north':(2957,3712,4096,4096),'northeast':(0,3712,320,4096),'east':(0,0,384,1139)}
    for role,box in crops.items():
        save_image('actual-'+role+'-focus.png',Image.fromarray(sources[role]).crop(box),{'cropLTRB':box,'role':role},[refs[role]])
    write(HERE/'preparation.json',dict(preparedAt=datetime.now(timezone.utc).isoformat(),nativeSource=ref(original),historicalSource=ref(HERE/'input-original.png'),historicalGeneration=ref(HERE/'input-original.generation-history.json'),request=ref(TILE/'native/p14.request.json'),sources=refs,actuallyViewed=False,approvedForPromotion=False,nativeFileModified=False))
    print(json.dumps({'prepared':str(HERE),'nativeFileModified':False}))

if __name__=='__main__':prepare()
