"""Render current native seam strips for visual inspection, with source hashes."""
from pathlib import Path
import hashlib, json
from datetime import datetime, timezone
from PIL import Image

TASK = Path(__file__).resolve().parent
def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    cp_path = TASK / 'source-checkpoint.json'
    cp = json.loads(cp_path.read_text(encoding='utf-8-sig'))
    out = TASK/'r08_c10'/('whole-tile-qa-'+cp['version']+'-root')
    out.mkdir(exist_ok=True)
    sources = {'active':cp['fragment'],'bottom':cp['bottom'], 'left':cp['coupledNeighbors']['r08_c09'], 'bottom_left':cp['coupledNeighbors']['r09_c09']}
    imgs={}
    for key,ref in sources.items():
        if sha(ref['file']) != ref['sha256']: raise ValueError('Source changed: '+key)
        im=Image.open(ref['file']).convert('RGBA')
        if im.size != (4096,4096): raise ValueError('Not full-size source: '+key)
        imgs[key]=im
    outputs=[]
    for col in range(4):
        x=1024*col
        im=Image.new('RGBA',(1024,512))
        im.paste(imgs['active'].crop((x,3840,x+1024,4096)),(0,0))
        im.paste(imgs['bottom'].crop((x,0,x+1024,256)),(0,256))
        p=out/f'bottom-seam-{col+1}.png'; im.save(p)
        outputs.append({'file':str(p),'sha256':sha(p),'globalLTRB':[36864+x,32512,36864+x+1024,33024],'nativeScale':1})
    im=Image.new('RGBA',(512,512))
    im.paste(imgs['left'].crop((3840,3840,4096,4096)),(0,0))
    im.paste(imgs['active'].crop((0,3840,256,4096)),(256,0))
    im.paste(imgs['bottom_left'].crop((3840,0,4096,256)),(0,256))
    im.paste(imgs['bottom'].crop((0,0,256,256)),(256,256))
    p=out/'bottom-left-four-tiles.png'; im.save(p)
    outputs.append({'file':str(p),'sha256':sha(p),'globalLTRB':[36608,32512,37120,33024],'nativeScale':1})
    record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'checkpoint':{'file':str(cp_path),'sha256':sha(cp_path)},'sources':sources,'outputs':outputs,'operation':'Exact native crops pasted at their true world coordinates, no resizing','visualReviewCompleted':False,'formalAccepted':False}
    (out/'crops.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'directory':str(out),'images':len(outputs)},ensure_ascii=False))
if __name__=='__main__': main()
