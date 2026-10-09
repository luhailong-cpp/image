from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,d):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
for i in range(1,5):
    sp=B/'native'/f's{i}.png';lp=B/'calibrated-local'/f's{i}-field.npz';bp=B/'calibrated-boundary'/f's{i}-field.npz'
    n=np.array(Image.open(sp).convert('RGB')).astype(np.float32)
    local=np.load(lp)['offset'];boundary=np.load(bp)['offsetRight350']
    xx=np.arange(350);mix=np.where(xx<80,(1+np.cos(np.pi*np.minimum(xx,80)/80))/2,0).astype(np.float32)
    delta=local.copy();delta[:,627:977]=local[:,627:977]*(1-mix[None,:,None])+boundary*mix[None,:,None]
    delta=np.clip(delta,-24,24)
    result=np.clip(np.rint(n+delta),0,255).astype(np.uint8)
    p=B/'calibrated-refined'/f's{i}.png';p.parent.mkdir(exist_ok=True);Image.fromarray(result).save(p)
    fp=p.with_name(f's{i}-field.npz');np.savez_compressed(fp,offset=delta,boundaryBlendWeight=mix)
    write(Path(str(p)+'.generation.json'),{**ref(p),'operation':'One bounded RGB correction: convex blend of same-coordinate local material-affine field and immediate-boundary color-residual field only within first80 right pixels; no image blur/warp/resampling','derivedFrom':[ref(sp),ref(B/'guides'/f's{i}-actual-pair.png')],'field':ref(fp),'componentFieldEvidence':[ref(lp),ref(bp)],'maxAbsRGBField':float(np.abs(delta).max()),'fieldsNotAppliedCumulatively':True,'visualReview':'pending'})

